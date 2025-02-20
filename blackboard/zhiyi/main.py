import os
import json
import datetime
from typing import Dict, List, Optional, Tuple
from legalagents import Internal, External, LegalReviewPanel
import argparse
from configloader import load_agent_config


class LegalSimulationWorkflow:
    def __init__(
        self, 
        legal_question: str,
        api_key: str,
        max_steps: int = 100,
        model_backbone: Optional[str] = None
    ):
        """Initialize the legal simulation workflow"""
        self.legal_question = legal_question
        self.max_steps = max_steps
        self.api_key = api_key
        self.model_backbone = model_backbone or "gpt-4o-mini"
        
        # Load agent configuration
        try:
            self.config = load_agent_config()
        except Exception as e:
            raise Exception(f"Error loading agent configuration: {str(e)}")
        
        # Initialize agents with configuration
        self.sg_lawyer = Internal(
            input_model = model_backbone,
            config=self.config,
            api_key=api_key
        )
        
        self.us_lawyer = External(
            input_model = model_backbone,
            config=self.config,
            api_key=api_key
        )
        
        # Initialize review panel
        self.review_panel = LegalReviewPanel(
            input_model = model_backbone,
            agent_config=self.config,
            api_key=api_key,
            max_steps=max_steps
        )
        
        # Create results directory with timestamp
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = os.path.join("results", f"analysis_{self.timestamp}")
        os.makedirs(self.results_dir, exist_ok=True)

    def _save_analysis_results(self, results: Dict) -> None:
        """Save analysis results to JSON file"""
        output_file = os.path.join(self.results_dir, "analysis_results.json")
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving analysis results: {str(e)}")

    def _save_agent_outputs(self, agent_outputs: Dict) -> None:
        """Save individual agent outputs"""
        for agent_name, output in agent_outputs.items():
            output_file = os.path.join(self.results_dir, f"{agent_name}_output.json")
            try:
                with open(output_file, 'w') as f:
                    json.dump(output, f, indent=2)
            except Exception as e:
                raise Exception(f"Error saving {agent_name} output: {str(e)}")

    def perform_legal_analysis(self) -> None:
        """Execute the complete legal analysis workflow"""
        try:
            print("\nInitiating legal analysis workflow...")
            
            # Store all analysis results
            analysis_results = {
                "legal_question": self.legal_question,
                "timestamp": self.timestamp,
                "model": self.model_backbone,
                "agent_outputs": {},
                "final_synthesis": None
            }
            
            # Singapore Law Analysis
            print("\nPerforming Singapore legal analysis...")
            sg_analysis = {}
            for phase in self.sg_lawyer.phases:
                print(f"Phase: {phase}")
                response = self.sg_lawyer.inference(
                    question=self.legal_question,
                    phase=phase,
                    step=1
                )
                sg_analysis[phase] = response
            analysis_results["agent_outputs"]["sg_lawyer"] = sg_analysis
            
            # US Law Comparative Analysis
            print("\nPerforming US comparative analysis...")
            us_analysis = {}
            for phase in self.us_lawyer.phases:
                print(f"Phase: {phase}")
                response = self.us_lawyer.inference(
                    question=self.legal_question,
                    phase=phase,
                    step=1
                )
                us_analysis[phase] = response
            analysis_results["agent_outputs"]["us_lawyer"] = us_analysis
            
            # Synthesize reviews
            print("\nSynthesizing perspectives...")
            reviews = [
                {
                    "perspective": "singapore_law",
                    "review": sg_analysis["review"]
                },
                {
                    "perspective": "us_law",
                    "review": us_analysis["review"]
                }
            ]
            
            synthesis = self.review_panel.synthesize_reviews(reviews)
            analysis_results["final_synthesis"] = synthesis
            
            # Save all results
            print("\nSaving analysis results...")
            self._save_analysis_results(analysis_results)
            self._save_agent_outputs(analysis_results["agent_outputs"])
            
            # Create summary file
            summary_file = os.path.join(self.results_dir, "analysis_summary.txt")
            with open(summary_file, 'w') as f:
                f.write(f"Legal Analysis Summary\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"Question: {self.legal_question}\n\n")
                f.write(f"Analysis Date: {self.timestamp}\n\n")
                f.write(f"Singapore Law Analysis:\n")
                f.write(f"{'-'*20}\n")
                f.write(sg_analysis["review"])
                f.write(f"\n\nUS Law Comparative Analysis:\n")
                f.write(f"{'-'*20}\n")
                f.write(us_analysis["review"])
                f.write(f"\n\nSynthesis:\n")
                f.write(f"{'-'*20}\n")
                f.write(synthesis["synthesis"])
                
            print(f"\nAnalysis complete! Results saved in: {self.results_dir}")
            
        except Exception as e:
            raise Exception(f"Error during legal analysis: {str(e)}")


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
        '--model',
        type=str,
        help='Selected model for generation'
    )
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

def main():
    """Main execution flow"""
    # Parse arguments
    args = parse_arguments()

    selected_model = args.model
    if selected_model:
        print(f"Model: {selected_model} has been selected")
    else:
        selected_model = None
        print("No model has been selected, default models from Agent config will be used")
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.getenv('api_key')
    if not api_key:
        raise ValueError(
            "API key must be provided via --api-key or "
            "api_key environment variable"
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
        api_key=api_key,
        model_backbone=selected_model,
    )
    
    # Execute analysis workflow
    try:
        print("\nBeginning legal analysis...")
        workflow.perform_legal_analysis()
        print("\nAnalysis complete! Results have been saved.")
        print("\nYou can find the detailed analysis in the 'results' directory.")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Please check the error message and try again.")
        return

if __name__ == "__main__":
    main()
