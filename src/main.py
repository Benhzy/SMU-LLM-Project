# ----- REQUIRED IMPORTS -----

import os
import json
import datetime
import argparse
from typing import Dict, Optional
from helper.agent_clients import AgentClient
from dotenv import load_dotenv

# ----- INITIALIZATION CODE -----

load_dotenv()

# ----- HELPER FUNCTIONS -----

class LegalSimulationWorkflow:
    def __init__(self, legal_question: str, api_keys: dict, model_backbone: Optional[str] = None, hypothetical: Optional[str] = None):
        """
        initialize the legal simulation workflow
        """
        self.legal_question = legal_question
        self.hypothetical = hypothetical
        self.api_keys = api_keys
        self.model_backbone = model_backbone

        self.agent_configs = {
            "Internal": {
                "type": "internal",
                "allowed_collections": ["collection1", "collection2", "collection3"]
            },
            "External": {
                "type": "external",
                "allowed_collections": ["collection2", "collection3"]
            }
        }
        # define agent configurations and allowed collections, these are placeholder values
        # ~ gong

        # Initialize agents using AgentClient
        self.agents = {}
        for agent_name, config in self.agent_configs.items():
            self.agents[agent_name] = AgentClient(
                name=agent_name,
                agent_type=config["type"],
                model_str=self.model_backbone,
                api_keys=self.api_keys,
                allowed_collections=config["allowed_collections"] 
            )

        # Create results directory with timestamp
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = os.path.join("results", f"analysis_{self.timestamp}")
        os.makedirs(self.results_dir, exist_ok=True)

    def _save_analysis_results(self, results: Dict) -> None:
        """
        save analysis results to a json file
        """
        output_file = os.path.join(self.results_dir, "analysis_results.json")
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            raise Exception(f"Error saving analysis results: {str(e)}")

    def perform_legal_analysis(self) -> None:
        """
        execute the complete legal analysis workflow
        """

        try:
            print("\nInitiating legal analysis workflow...")
            analysis_results = {
                "legal_question": self.legal_question,
                "hypothetical": self.hypothetical,
                "timestamp": self.timestamp,
                "model": self.model_backbone,
                "agent_outputs": {},
                "final_synthesis": None
            }

            # Determine what to analyze (question or hypothetical)
            analysis_text = self.hypothetical if self.hypothetical else self.legal_question

            # Perform analysis for each agent
            for agent_name, agent in self.agents.items():
                print(f"\nPerforming analysis using {agent_name}...")
                agent_results = agent.perform_full_structured_analysis(question=analysis_text)
                analysis_results["agent_outputs"][agent_name] = agent_results

            # Synthesize reviews using Internal and External outputs
            print("\nSynthesizing perspectives...")
            internal_review = analysis_results["agent_outputs"]["Internal"].get("review", "")
            external_review = analysis_results["agent_outputs"]["External"].get("review", "")

            reviews = [
                {"perspective": "internal_law", "review": internal_review},
                {"perspective": "external_law", "review": external_review}
            ]

            # Use one of the agents (e.g., Internal) to synthesize reviews
            synthesis = self.agents["Internal"].synthesize_reviews(reviews)
            analysis_results["final_synthesis"] = synthesis

            # Save all results
            print("\nSaving analysis results...")
            self._save_analysis_results(analysis_results)

            print(f"\nAnalysis complete! Results saved in: {self.results_dir}")

        except Exception as e:
            raise Exception(f"Error during legal analysis: {str(e)}")


def parse_arguments():
    """
    parse command-line arguments
    """
    parser = argparse.ArgumentParser(description="Legal Analysis Simulation System")
    parser.add_argument("--model", type=str, help="Selected model for generation")
    parser.add_argument("--question", type=str, help="The legal question to analyze")
    parser.add_argument("--hypo", type=str, help="The legal hypothetical scenario to analyze")
    return parser.parse_args()


def main():
    """
    main execution flow
    """

    args = parse_arguments()
    selected_model = args.model or "gpt-4o-mini"
    legal_question = args.question
    hypothetical = args.hypo

    # more logging, can remove if deemed unhelpful ~ gong
    if legal_question and hypothetical: 
        raise ValueError("Cannot provide both a legal question and a hypothetical. Please choose one.")
    if not legal_question and not hypothetical: 
        raise ValueError("Either a legal question (--question) or a legal hypothetical (--hypo) must be provided.")

    # Get API keys from environment variables
    api_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'deepseek': os.getenv('DEEPSEEK_API_KEY'),
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
    }

    if not any(api_keys.values()):
        raise ValueError("No API keys provided. At least one API key must be provided via environment variables.")
    else:  # just me being extra and adding more logging, we can remove this later ~ gong
        missing_keys = [key for key, value in api_keys.items() if not value]
        if missing_keys:
            print(f"\nWarning: The following API keys are missing: {', '.join(missing_keys)}")
            print("Only services with valid API keys will be available.")        
        available_keys = [key for key, value in api_keys.items() if value]
        print(f"\nAvailable API services: {', '.join(available_keys)}")

    try:
        print("\nInitializing legal simulation workflow...")
        workflow = LegalSimulationWorkflow(
            legal_question=legal_question or "", # pass empty string if none, might want to make the checking better
            api_keys=api_keys,
            model_backbone=selected_model,
            hypothetical=hypothetical or "", # pass empty string if none, might want to make the checking more comprehensive
        )
        workflow.perform_legal_analysis()
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")

# ----- EXECUTION CODE -----

if __name__ == "__main__":
    main()