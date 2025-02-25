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
        agent_type: str,
        input_model: str,
        config: Dict[str, Any],
        api_keys: Dict[str, str],
        notes: Optional[List[Dict[str, Any]]] = None
        
    ):
        """
        Initialize base agent
        
        Args:
            agent_type: Type of agent (sg_lawyer, us_lawyer)
            input_model: Model to use for this agent
            config: Configuration dictionary loaded from JSON
            api_keys: Dictionary of API keys by provider
            notes: List of notes/instructions for the agent
        """
        if agent_type not in config:
            raise ValueError(f"Invalid agent type: {agent_type}")
            
        agent_config = config[agent_type]
        default_config = agent_config['default_config']
        
        self.agent_type = agent_type
        self.role_desc = agent_config['role_description']
        self.phase_prompts = agent_config['phase_prompts']
        self.notes = notes or []
        self.max_steps = default_config['max_steps']
        self.model = input_model or default_config['model']
        self.history: List[tuple[Optional[int], str]] = []
        self.prev_comm = ""
        self.api_keys = api_keys or {}
        self.max_hist_len = default_config['max_history']
        
        # Get the appropriate API key based on the model
        provider = get_provider(self.model)
        self.api_key = self.api_keys.get(provider)
        
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
        """Return the role description from config"""
        return self.role_desc

    def phase_prompt(self, phase: str) -> str:
        """Return the phase prompt from config"""
        if phase not in self.phase_prompts:
            raise ValueError(f"Invalid phase {phase} for agent {self.agent_type}")
        return self.phase_prompts[phase]

    def inference(
        self,
        question: str,
        phase: str,
        step: int,
        feedback: str = "",
        temp: Optional[float] = None
    ) -> str:
        """
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
            model_resp = query_model(
                model_str=self.model,
                system_prompt=system_prompt,
                prompt=user_prompt,
                api_key=self.api_key,
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

class Internal(BaseAgent):
    def __init__(
        self,
        input_model: str,
        api_keys: Dict[str, str],
        config: Dict[str, Any],
        notes: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            agent_type='internal',
            input_model = input_model,
            config=config,
            api_keys=api_keys,
            notes=notes
            
        )
        self.phases = [
            "statutory_analysis",
            "case_law_review",
            "practice_implications",
            "review"
        ]
        self.perspective = "singapore_law"
        self.sg_statutes = {}                           #TODO implement VDB for contextual knowledge
        self.sg_case_law = {}

class External(BaseAgent):
    def __init__(
        self,
        input_model: str,
        api_keys: Dict[str, str],
        config: Dict[str, Any],
        notes: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            agent_type='external',
            input_model = input_model,
            config=config,
            api_keys=api_keys,
            notes=notes
        )
        self.phases = [
            "comparative_analysis",
            "federal_state_review",
            "practice_insights",
            "review"
        ]
        self.perspective = "us_law"
        self.us_constitution = {}                           #TODO implement VDB for contextual knowledge
        self.us_case_law = {}
        
class LegalReviewPanel:
    """Specialized review panel for Singapore legal analysis"""
    
    def __init__(
        self,
        agent_config: Dict[str, Any],
        input_model: str,
        api_keys: Dict[str, str],
        max_steps: int = 100,
        max_history: int = 15,
        notes: Optional[List[Dict[str, Any]]] = None,
        review_config_path: str = "settings/review.json"
    ):
        """
        Initialize the review panel with configuration
        
        Args:
            model: Model to use for synthesis
            api_key: OpenAI API key
            max_steps: Maximum steps for agent analysis
            max_history: Maximum history entries to maintain
            notes: Additional notes or instructions for agents
            review_config_path: Path to review configuration file
        """
        self.model = input_model

        # Load configurations
        try:
            with open(review_config_path, 'r') as f:
                self.review_config = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading configurations: {str(e)}")
        
        # Initialize reviewers with configuration
        self.reviewers = [
            Internal(
                input_model = input_model,
                api_keys = api_keys,
                config=agent_config,
                notes=notes,
            ),
            External(
                input_model = input_model,
                api_keys = api_keys,
                config=agent_config,
                notes=notes,
            )
        ]

    def evaluate_review(self, review: str) -> Dict[str, int]:
        """Evaluate a review based on criteria"""
        scores = {}
        for criterion, details in self.review_config["review_criteria"].items():
            scores[criterion] = 8  # TODO add eval criteria/use model to eval
        return scores

    def get_feedback_template(self, scores: Dict[str, int]) -> str:
        """Get appropriate feedback template based on scores"""
        avg_score = sum(scores.values()) / len(scores)
        thresholds = self.review_config["quality_thresholds"]
        
        if avg_score < thresholds["revision_required"]:
            return self.review_config["feedback_templates"]["revision_needed"]
        elif avg_score < thresholds["minor_improvements"]:
            return self.review_config["feedback_templates"]["minor_improvements"]
        else:
            return self.review_config["feedback_templates"]["approval"]
    
    def synthesize_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize reviews with Singapore focus
        
        Args:
            reviews: List of review dictionaries with perspective and content
            
        Returns:
            Dictionary containing synthesized analysis
        """
        # Validate required perspectives
        required_perspectives = {"singapore_law", "us_law"}
        provided_perspectives = {r["perspective"] for r in reviews}
        
        if not required_perspectives.issubset(provided_perspectives):
            missing = required_perspectives - provided_perspectives
            raise ValueError(f"Missing required perspectives: {missing}")
        
        # Extract perspectives
        synthesis = {
            "sg_law_perspective": next(r["review"] for r in reviews 
                                    if r["perspective"] == "singapore_law"),
            "us_law_perspective": next(r["review"] for r in reviews 
                                    if r["perspective"] == "us_law"),
            "requires_revision": False,
            "synthesis": "",
            "recommendations": [],
            "scores": {}
        }
        
        try:
            # Get prompts from config
            sys_prompt = self.review_config["synthesis"]["system_prompt"]
            synthesis_prompt = self.review_config["synthesis"]["synthesis_template"].format(
                sg_law_perspective=synthesis["sg_law_perspective"],
                us_law_perspective=synthesis["us_law_perspective"]
            )
            
            # Generate synthesis
            synthesis_response = query_model(
                model_str=self.model,
                system_prompt=sys_prompt,
                prompt=synthesis_prompt,
                api_key=self.api_key
            )
            
            # Extract recommendations
            recommendations = []
            if "Recommendations:" in synthesis_response:
                rec_section = synthesis_response.split("Recommendations:")[1]
                rec_lines = [line.strip() for line in rec_section.split("\n") 
                           if line.strip() and line.strip().startswith("-")]
                recommendations = rec_lines
            
            # Evaluate the synthesis
            scores = self.evaluate_review(synthesis_response)
            feedback_template = self.get_feedback_template(scores)
            
            synthesis["synthesis"] = synthesis_response
            synthesis["recommendations"] = recommendations
            synthesis["scores"] = scores
            synthesis["feedback_template"] = feedback_template
            synthesis["requires_revision"] = (
                sum(scores.values()) / len(scores) < 
                self.review_config["quality_thresholds"]["revision_required"]
            )
            
            return synthesis
            
        except Exception as e:
            print(f"Error in synthesis: {str(e)}")
            raise
            
    def get_reviewer(self, perspective: str) -> Optional[Any]:
        """Get reviewer by perspective"""
        for reviewer in self.reviewers:
            if reviewer.perspective == perspective:
                return reviewer
        return None