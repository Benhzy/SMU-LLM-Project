from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json
import time
from utils import *
from tools import *
from inference import *


@dataclass
class ReviewCriteria:
    """Data class for review criteria scores"""
    jurisdictional_understanding: int
    legal_reasoning: int
    comparative_analysis: int
    practical_application: int
    academic_merit: int

    def validate(self) -> bool:
        """Validate all scores are within acceptable range"""
        return all(
            1 <= getattr(self, field.name) <= 10
            for field in self.__dataclass_fields__.values()
        )

class BaseAgent:
    """Base class for all legal analysis agents"""
    
    def __init__(
        self, 
        model: str = "gpt-4",
        notes: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 100,
        max_history: int = 15,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize base agent
        
        Args:
            model: Name of the LLM model to use
            notes: List of notes/instructions for the agent
            max_steps: Maximum number of steps per phase
            max_history: Maximum number of history entries to keep
            openai_api_key: OpenAI API key
        """
        self.notes = notes or []
        self.max_steps = max_steps
        self.model = model
        self.phases: List[str] = []
        self.history: List[tuple[Optional[int], str]] = []
        self.prev_comm = ""
        self.openai_api_key = openai_api_key
        self.max_hist_len = max_history
        
        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = 1  # seconds

    def _rate_limit(self) -> None:
        """Implement rate limiting for API calls"""
        now = time.time()
        time_since_last = now - self.last_api_call
        if time_since_last < self.min_api_interval:
            time.sleep(self.min_api_interval - time_since_last)
        self.last_api_call = now

    def _manage_history(self, entry: str) -> None:
        """Manage history entries with cleanup"""
        self.history.append((None, entry))
        while len(self.history) > self.max_hist_len:
            self.history.pop(0)

    def role_description(self) -> str:
        """Override this method in subclasses to provide role-specific description"""
        raise NotImplementedError

    def phase_prompt(self, phase: str) -> str:
        """Override this method in subclasses to provide phase-specific prompts"""
        raise NotImplementedError

    async def inference(
        self,
        question: str,
        phase: str,
        step: int,
        feedback: str = "",
        temp: Optional[float] = None
    ) -> str:
        """
        Run inference for the agent. Modified to match query_model interface.
        
        Args:
            question: The legal question to analyze
            phase: Current phase of analysis
            step: Current step number
            feedback: Previous feedback
            temp: Temperature for model inference
            
        Returns:
            Model response
        """
        if phase not in self.phases:
            raise ValueError(f"Invalid phase {phase} for agent {self.__class__.__name__}")
            
        self._rate_limit()
        
        system_prompt = (
            f"You are {self.role_description()}\n"
            f"Task instructions: {self.phase_prompt(phase)}\n"
        )
        
        history_str = "\n".join(entry[1] for entry in self.history)
        phase_notes = [
            note["note"] for note in self.notes 
            if phase in note["phases"]
        ]
        notes_str = (
            f"Notes for the task objective: {phase_notes}\n" 
            if phase_notes else ""
        )
        
        user_prompt = (
            f"History: {history_str}\n{'~' * 10}\n"
            f"Current Step #{step}, Phase: {phase}\n"
            f"[Objective] Your goal is to analyze the following legal question: "
            f"{question}\n"
            f"Feedback: {feedback}\nNotes: {notes_str}\n"
            f"Your previous response was: {self.prev_comm}. "
            f"Please ensure your new analysis adds value.\n"
            f"Please provide your analysis below:\n"
        )

        try:
            model_resp = await query_model(
                model_str=self.model,
                system_prompt=system_prompt,
                prompt=user_prompt,
                openai_api_key=self.openai_api_key,
                temp=temp
            )
        except Exception as e:
            print(f"Error during model inference: {str(e)}")
            raise
            
        self.prev_comm = model_resp
        self._manage_history(
            f"Step #{step}, Phase: {phase}, Analysis: {model_resp}"
        )
        
        return model_resp

    
class SGLawyer(BaseAgent):
    """Expert in Singapore law and legal practice"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        notes: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 100,
        max_history: int = 15,
        openai_api_key: Optional[str] = None
    ):
        # Pass all parameters to parent class
        super().__init__(
            model=model,
            notes=notes,
            max_steps=max_steps,
            max_history=max_history,
            openai_api_key=openai_api_key
        )
        
        # Define phases specific to Singapore legal analysis
        self.phases = [
            "statutory_analysis",
            "case_law_review",
            "practice_implications",
            "review"
        ]
        self.perspective = "singapore_law"
        self.sg_statutes = {}
        self.sg_case_law = {}
        
    def role_description(self) -> str:
        return """You are a senior Singapore lawyer with extensive experience in Singapore's legal system. 
        You have a deep understanding of Singapore statutes, case law, and legal practice. 
        Your analysis should always consider:
        1. Relevant Singapore legislation and their interpretation
        2. Leading Singapore court decisions
        3. Singapore legal practice directions and professional conduct rules
        4. Local context and public policy considerations"""
    
    def phase_prompt(self, phase: str) -> str:
        if phase == "statutory_analysis":
            return """Analyze the legal question focusing on relevant Singapore statutes. Consider:
            - Primary legislation relevant to the issue
            - Subsidiary legislation and regulations
            - Legislative intent and parliamentary debates
            - Statutory interpretation principles in Singapore context
            - Recent legislative amendments and their impact"""
            
        elif phase == "case_law_review":
            return """Review Singapore case law relevant to the question. Focus on:
            - Leading Court of Appeal decisions
            - High Court precedents
            - Recent developments in case law
            - Treatment of foreign precedents by Singapore courts
            - Application of legal principles in local context"""
            
        elif phase == "practice_implications":
            return """Examine practical implications for Singapore legal practice:
            - Impact on day-to-day legal practice
            - Compliance requirements
            - Professional conduct considerations
            - Client counseling approaches
            - Risk management strategies"""
            
        elif phase == "review":
            return """Review the analysis from a Singapore law perspective:
            - Accuracy of statutory interpretation
            - Proper application of Singapore case law
            - Consideration of local context
            - Practical viability in Singapore legal system"""
            
        raise ValueError(f"Invalid phase {phase}")

class USLawyer(BaseAgent):
    """Expert in US law providing comparative perspective"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        notes: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 100,
        max_history: int = 15,
        openai_api_key: Optional[str] = None
    ):
        # Pass all parameters to parent class
        super().__init__(
            model=model,
            notes=notes,
            max_steps=max_steps,
            max_history=max_history,
            openai_api_key=openai_api_key
        )
        
        self.phases = [
            "comparative_analysis",
            "federal_state_review",
            "practice_insights",
            "review"
        ]
        self.perspective = "us_law"
        
    def role_description(self) -> str:
        return """You are a senior US lawyer providing comparative legal analysis between US and Singapore law.
        You have experience in cross-border matters and understanding of both legal systems.
        Your analysis should focus on:
        1. Key differences between US and Singapore legal approaches
        2. Relevant US legal principles and their applicability
        3. Cross-jurisdictional considerations
        4. Practical implications of different legal frameworks"""

    def phase_prompt(self, phase: str) -> str:
        if phase == "comparative_analysis":
            return """Compare US and Singapore legal approaches:
            - Fundamental differences in legal principles
            - Treatment of similar issues in both jurisdictions
            - Relative advantages and disadvantages
            - Potential for legal convergence or divergence"""
            
        elif phase == "federal_state_review":
            return """Analyze relevant US federal and state law:
            - Applicable federal statutes and regulations
            - Relevant state law variations
            - Leading US court decisions
            - Regulatory framework differences"""
            
        elif phase == "practice_insights":
            return """Share insights from US legal practice:
            - Common approaches in US jurisdiction
            - Practical challenges and solutions
            - Risk management strategies
            - Cross-border considerations"""
            
        elif phase == "review":
            return """Review the analysis considering US legal perspective:
            - Accuracy of US law interpretation
            - Comparative analysis quality
            - Cross-jurisdictional implications
            - Practical viability"""
            
        raise ValueError(f"Invalid phase {phase}")

class SGParliament(BaseAgent):
    """Representative providing legislative and policy perspective"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        notes: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 100,
        max_history: int = 15,
        openai_api_key: Optional[str] = None
    ):
        # Pass all parameters to parent class
        super().__init__(
            model=model,
            notes=notes,
            max_steps=max_steps,
            max_history=max_history,
            openai_api_key=openai_api_key
        )
        
        self.phases = [
            "policy_analysis",
            "legislative_intent",
            "public_impact",
            "review"
        ]
        self.perspective = "parliament"
        self.legislative_records = {}
        
    def role_description(self) -> str:
        return """You are a senior member of Singapore's Parliament with deep understanding of:
        1. Singapore's legislative process and parliamentary procedures
        2. Public policy considerations and national interests
        3. Legislative intent and parliamentary history
        4. Regulatory impact and public consultation processes"""
    
    def phase_prompt(self, phase: str) -> str:
        if phase == "policy_analysis":
            return """Analyze public policy implications:
            - Alignment with national interests
            - Impact on different stakeholder groups
            - Economic and social considerations
            - International obligations and commitments
            - Regulatory impact assessment"""
            
        elif phase == "legislative_intent":
            return """Examine legislative intent and history:
            - Parliamentary debates and discussions
            - Committee reports and recommendations
            - Public consultation feedback
            - Policy objectives and intended outcomes
            - Legislative development process"""
            
        elif phase == "public_impact":
            return """Assess impact on public interest:
            - Effect on different segments of society
            - Implementation challenges
            - Compliance costs and benefits
            - Public communication needs
            - Potential unintended consequences"""
            
        elif phase == "review":
            return """Review the analysis from policy perspective:
            - Alignment with legislative intent
            - Public policy considerations
            - Stakeholder impact assessment
            - Implementation viability"""
            
        raise ValueError(f"Invalid phase {phase}")

class LegalReviewPanel:
    """Specialized review panel for Singapore legal analysis"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        openai_api_key: Optional[str] = None,
        max_steps: int = 100,
        max_history: int = 15,
        notes: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize the review panel with configuration for all agents
        
        Args:
            model: The GPT model to use
            openai_api_key: OpenAI API key for model access
            max_steps: Maximum steps for agent analysis
            max_history: Maximum history entries to maintain
            notes: Additional notes or instructions for agents
        """
        self.model = model
        self.openai_api_key = openai_api_key
        
        # Initialize reviewers with consistent configuration
        self.reviewers = [
            SGLawyer(
                model=model,
                openai_api_key=openai_api_key,
                max_steps=max_steps,
                max_history=max_history,
                notes=notes
            ),
            USLawyer(
                model=model,
                openai_api_key=openai_api_key,
                max_steps=max_steps,
                max_history=max_history,
                notes=notes
            ),
            SGParliament(
                model=model,
                openai_api_key=openai_api_key,
                max_steps=max_steps,
                max_history=max_history,
                notes=notes
            )
        ]
    
    async def synthesize_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize reviews with Singapore focus"""
        synthesis = {
            "sg_law_perspective": next(r["review"] for r in reviews 
                                    if r["perspective"] == "singapore_law"),
            "us_law_perspective": next(r["review"] for r in reviews 
                                    if r["perspective"] == "us_law"),
            "parliament_perspective": next(r["review"] for r in reviews 
                                        if r["perspective"] == "parliament"),
            "requires_revision": False,
            "synthesis": "",
            "recommendations": []
        }
        
        sys_prompt = """You are a senior legal expert synthesizing perspectives on a 
        Singapore legal issue. Consider the local context and practical implications."""
        
        synthesis_prompt = f"""Please synthesize these perspectives for the Singapore context:

        Singapore Law Perspective:
        {synthesis['sg_law_perspective']}
        
        US Law Comparative Perspective:
        {synthesis['us_law_perspective']}
        
        Parliamentary Perspective:
        {synthesis['parliament_perspective']}
        
        Focus on:
        1. Key agreements and disagreements
        2. Practical implications for Singapore
        3. Areas needing clarification
        4. Recommendations for implementation"""
        
        try:
            synthesis_response = await query_model(
                model_str=self.model,
                system_prompt=sys_prompt,
                prompt=synthesis_prompt,
                openai_api_key=self.openai_api_key
            )
            synthesis["synthesis"] = synthesis_response
            return synthesis
        except Exception as e:
            print(f"Error in synthesis: {str(e)}")
            raise
