from vdb_manager import VDBManager
from legalagents import Internal, External
from helper.configloader import load_agent_config
import os

class AgentClient:
    def __init__(self, name, agent_type="internal", model_str="gpt-4o-mini", api_keys=None,
                 allowed_collections=None):
        if allowed_collections is None:
            allowed_collections = []
        config = load_agent_config()
        agent_class = Internal if agent_type.lower() == 'internal' else External
        self.name = name
        self.agent = agent_class(
            input_model=model_str,
            api_keys=api_keys or {"openai": os.getenv("OPENAI_API_KEY")},
            config=config,
        )
        self.vdb_manager = VDBManager(client_name=name, allowed_collections=allowed_collections)

    def query(self, collection_name, query_text, **kwargs):
        return self.vdb_manager.query_collection(collection_name=collection_name,
                                                 query_text=query_text,
                                                 **kwargs)