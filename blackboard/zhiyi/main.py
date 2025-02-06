import os
import pickle
from typing import Dict, List, Optional, Tuple
from legalagents import SGLawyer, USLawyer, SGParliament, LegalReviewPanel
import asyncio
import argparse

class LegalSimulationWorkflow:
    def __init__(
        self, 
        legal_question: str,
        openai_api_key: str,
        max_steps: int = 100,
        human_in_loop_flag: Optional[Dict[str, bool]] = None,
        model_backbone: Optional[str] = None
    ):
        """Initialize with the same parameters but modified to work with updated BaseAgent"""
        self.legal_question = legal_question
        self.max_steps = max_steps
        self.openai_api_key = openai_api_key
        self.model_backbone = model_backbone or "gpt-4"
        self._validate_model_backbone()
        
        # Initialize agents
        self.SG_lawyer = SGLawyer(
            model=self.model_backbone,
            openai_api_key=self.openai_api_key
        )
        self.US_lawyer = USLawyer(
            model=self.model_backbone,
            openai_api_key=self.openai_api_key
        )
        self.SG_parliament = SGParliament(
            model=self.model_backbone,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize review panel
        self.peer_reviewers = LegalReviewPanel(
            model=self.model_backbone,
            openai_api_key=self.openai_api_key
        )
        
        # Define workflow phases
        self.phases = [
            ("statutory analysis", ["statute", "federal law"]),
            ("case law analysis", ["case_law_review", "precedent_analysis"]),
            ("practical implications", ["practice_implications", "implementation_guidance"]),
            ("synthesis", ["perspective_integration", "recommendation_development"]),
            ("review", ["initial_review", "revision_process"])
        ]
        
        # Validate phase handlers exist
        self._validate_phase_handlers()

        # Initialize phase tracking
        self.phase_status: Dict[str, bool] = {
            subtask: False 
            for phase, subtasks in self.phases 
            for subtask in subtasks
        }

        # Set human interaction settings
        self.human_in_loop_flag = human_in_loop_flag or {
            subtask: True
            for _, subtasks in self.phases
            for subtask in subtasks
        }

        # Create state save directory
        os.makedirs("state_saves", exist_ok=True)

    def _validate_model_backbone(self) -> None:
        """
        Validate the selected model backbone.
        Currently supports GPT-4 and GPT-3.5 models.
        """
        valid_models = [
            "gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo",
            "gpt-4-0125-preview", "gpt-4-1106-preview"
        ]
        
        if self.model_backbone not in valid_models:
            print(f"Warning: Using unofficial model '{self.model_backbone}'")
            print("Recommended models are:", ", ".join(valid_models))

    def _validate_phase_handlers(self) -> None:
        """Validate that all defined phases have corresponding handlers"""
        for _, subtasks in self.phases:
            for subtask in subtasks:
                handler_name = f"execute_{subtask}"
                if not hasattr(self, handler_name):
                    raise NotImplementedError(
                        f"Handler method {handler_name} not implemented for subtask {subtask}"
                    )

    async def execute_subtask(self, subtask: str) -> str:
        """Execute a specific subtask by calling its handler method"""
        handler_name = f"execute_{subtask}"
        
        try:
            if not hasattr(self, handler_name):
                raise AttributeError(f"Handler method {handler_name} not found")
                
            handler = getattr(self, handler_name)
            
            print(f"Debug - Handler type: {type(handler)}")
            print(f"Debug - Handler value: {handler}")
            
            if not callable(handler):
                raise TypeError(
                    f"Handler '{handler_name}' is a {type(handler)} "
                    f"with value '{handler}', but should be a method"
                )
                
            return await handler()
            
        except Exception as e:
            print(f"Error executing subtask {subtask}: {str(e)}")
            # Print the list of all attributes to help debug
            print("\nAvailable methods:")
            for attr_name in dir(self):
                if attr_name.startswith('execute_'):
                    attr_value = getattr(self, attr_name)
                    print(f"  {attr_name}: {type(attr_value)}")
            raise

    async def execute_common_law_analysis(self) -> str:
        """Execute common law analysis phase"""
        return await self.SG_lawyer.inference(
            self.legal_question,
            phase="jurisdictional_analysis",
            step=0
        )

    async def execute_statutory_law_review(self) -> str:
        """Execute statutory law review phase"""
        return await self.SG_lawyer.inference(
            question=self.legal_question,
            phase="statutory_analysis",
            step=0
        )

    async def execute_regulatory_framework(self) -> str:
        """Execute regulatory framework analysis phase"""
        return await self.US_lawyer.inference(
            question=self.legal_question,
            phase="federal_state_review",
            step=0
        )

    async def execute_case_law_review(self) -> str:
        """Execute case law review phase"""
        return await self.SG_lawyer.inference(
            self.legal_question,
            phase="case_law_review",  
            step=0
        )

    async def execute_precedent_analysis(self) -> str:
        """Execute precedent analysis phase"""
        return await self.US_lawyer.inference(
            self.legal_question,
            phase="comparative_analysis", 
            step=0
        )

    async def execute_practice_implications(self) -> str:
        """Execute practice implications phase"""
        return await self.SG_lawyer.inference(
            self.legal_question,
            phase="practice_implications",  
            step=0
        )

    async def execute_implementation_guidance(self) -> str:
        """Execute implementation guidance phase"""
        return await self.US_lawyer.inference(
            self.legal_question,
            phase="practice_insights",  
            step=0
        )

    async def execute_perspective_integration(self) -> str:
        """Execute perspective integration phase"""
        sg_review = await self.SG_lawyer.inference(
            self.legal_question,
            phase="review",  
            step=0
        )
        us_review = await self.US_lawyer.inference(
            self.legal_question,
            phase="review", 
            step=0
        )
        parliament_review = await self.SG_parliament.inference(
            self.legal_question,
            phase="review", 
            step=0
        )
        
        synthesis = await self.peer_reviewers.synthesize_reviews([{
            "perspective": "singapore_law",
            "review": sg_review
        }, {
            "perspective": "us_law",
            "review": us_review
        }, {
            "perspective": "parliament",
            "review": parliament_review
        }])
        return synthesis["synthesis"]

    async def execute_recommendation_development(self) -> str:
        """Execute recommendation development phase"""
        return await self.SG_parliament.inference(
            self.legal_question,
            phase="policy_analysis",  # Using correct phase name from SGParliament
            step=0
        )

    async def execute_initial_review(self) -> str:
        """Execute initial review phase"""
        sg_review = await self.SG_lawyer.inference(
            self.legal_question,
            phase="review",  # Using correct phase name
            step=0
        )
        synthesis = await self.peer_reviewers.synthesize_reviews([{
            "perspective": "singapore_law",
            "review": sg_review
        }])
        return synthesis["synthesis"]

    async def execute_revision_process(self) -> str:
        """Execute revision process phase"""
        initial_review = await self.execute_initial_review()
        parliament_review = await self.SG_parliament.inference(
            f"{self.legal_question}\n\nInitial Review:\n{initial_review}",
            phase="review",
            step=0
        )
        synthesis = await self.peer_reviewers.synthesize_reviews([{
            "perspective": "parliament",
            "review": parliament_review
        }])
        return synthesis["synthesis"]

    async def perform_legal_analysis(self) -> None:
        """Execute the complete legal analysis workflow"""
        for phase_name, subtasks in self.phases:
            print(f"\nExecuting phase: {phase_name}")
            for subtask in subtasks:
                print(f"  Executing subtask: {subtask}")
                try:
                    result = await self.execute_subtask(subtask)
                    self.phase_status[subtask] = True
                    
                    # Save state after each successful subtask
                    self.save_state(phase_name)
                    
                    print(f"  Completed subtask: {subtask}")
                    
                    if self.human_in_loop_flag.get(subtask, False):
                        input("Press Enter to continue...")
                        
                except Exception as e:
                    print(f"Error in subtask {subtask}: {str(e)}")
                    raise

class LegalQuestionPrompt:
    """Handles user interaction for legal question input"""
    
    @staticmethod
    def display_welcome_message():
        """Display welcome message and introduction"""
        print("\n" + "=" * 80)
        print("Welcome to the Legal Analysis Simulation System")
        print("=" * 80)
        print("\nThis system analyzes legal hypotheticals from multiple perspectives:")
        print("  • Singapore Legal Practitioner")
        print("  • US Legal Comparative Analysis")
        print("  • Singapore Parliamentary Consideration")
        print("\nThe system will guide you through formulating your legal question.")
        print("=" * 80 + "\n")

    @staticmethod
    def display_question_guidelines():
        """Display guidelines for formulating legal questions"""
        print("\nGuidelines for formulating your legal question:")
        print("\n1. Question Structure:")
        print("   • Start with a clear context or scenario")
        print("   • Identify the key legal issues")
        print("   • Specify any relevant facts or circumstances")
        
        print("\n2. Example Questions:")
        print("   Example 1: 'In a case where a Singapore company's AI system makes")
        print("              automated decisions that harm customers, how would")
        print("              liability be determined under current Singapore law?'")
        
        print("   Example 2: 'How would Singapore courts likely treat smart contracts")
        print("              in commercial disputes, considering both Singapore contract")
        print("              law principles and international practices?'")
        
        print("\n3. Key Components to Include:")
        print("   • Relevant jurisdiction (Singapore context)")
        print("   • Specific legal domain (e.g., contract law, tort law)")
        print("   • Key facts or circumstances")
        print("   • Specific legal questions to be addressed")
        print("\n" + "=" * 80 + "\n")

    @staticmethod
    def get_legal_question() -> str:
        """Prompt user for legal question with guidance"""
        while True:
            print("\nPlease enter your legal question. Your question should:")
            print("- Present a clear scenario or context")
            print("- Identify specific legal issues")
            print("- Include relevant facts")
            print("\nType your question below (or type 'help' for examples):")
            
            question = input("\n> ").strip()
            
            if question.lower() == 'help':
                print("\nExample Questions:")
                print("\n1. Technological Innovation:")
                print("   'How would Singapore's data protection laws apply to a")
                print("    company using AI for automated customer profiling,")
                print("    particularly regarding consent and transparency?'")
                
                print("\n2. Cross-Border Issues:")
                print("   'What legal framework would apply to a dispute between")
                print("    a Singapore-based cryptocurrency exchange and its US")
                print("    customers, considering both jurisdictions' regulations?'")
                continue
                
            if len(question) < 20:
                print("\nYour question seems too brief. Please provide more context")
                print("and specific details to enable a thorough analysis.")
                continue
                
            confirm = input("\nIs this the question you'd like to analyze? (y/n): ")
            if confirm.lower() == 'y':
                return question

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Legal Analysis Simulation System")
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enable interactive mode with detailed feedback'
    )
    return parser.parse_args()

async def main():
    """Main execution flow"""
    # Parse arguments
    args = parse_arguments()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OpenAI API key must be provided via --api-key or "
            "OPENAI_API_KEY environment variable"
        )
    
    # Initialize question prompt system
    prompter = LegalQuestionPrompt()
    
    # Display welcome and guidelines
    prompter.display_welcome_message()
    prompter.display_question_guidelines()
    
    # Get legal question from user
    legal_question = prompter.get_legal_question()
    
    print("\nInitializing analysis workflow...")
    print("=" * 80)
    
    # Initialize workflow with human interaction based on args
    workflow = LegalSimulationWorkflow(
        legal_question=legal_question,
        openai_api_key=api_key,
        human_in_loop_flag={
            subtask: args.interactive
            for subtask in [
                "common_law_analysis",
                "civil_law_analysis",
                "cross_jurisdictional_study",
                "principle_extraction",
                "framework_development",
                "literature_review",
                "perspective_integration",
                "recommendation_development",
                "initial_review",
                "revision_process"
            ]
        }
    )
    
    # Execute analysis workflow
    try:
        print("\nBeginning legal analysis...")
        await workflow.perform_legal_analysis()
        print("\nAnalysis complete! Results have been saved.")
        print("\nYou can find the detailed analysis in the 'state_saves' directory.")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Please check the error message and try again.")
        return

if __name__ == "__main__":
    asyncio.run(main())
