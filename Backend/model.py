from mesa import Model
from agents import ClientAgent, RecommendationAgent
import configuration as config
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List

def serialize_data(data: Any) -> Any:
    """
    Fonction pour sérialiser les données et convertir les ObjectId en str.
    """
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data
    
class ECommerceModel(Model):
    def __init__(self):
        super().__init__()
        self.products_collection = config.products_collection
        self.interactions_collection = config.interactions_collection
        self.client_agents = {}

    def handle_client_interaction(self, user_id, action_type, product_id, duration, description):
        """Handles a client interaction, updates agents, and persists the interaction."""

        # Check if the client already has agents
        client_agent_key = user_id
        recommendation_agent_key = user_id + "recommendation"

        if client_agent_key not in self.client_agents:
            #Create a new Client Agent and Recommendation Agent
            agent = ClientAgent(client_agent_key, self, user_id=user_id)
            recommendation_agent = RecommendationAgent(recommendation_agent_key, self, user_id=user_id)
            self.client_agents[client_agent_key] = agent
            self.client_agents[recommendation_agent_key] = recommendation_agent
            
        else:
            # Get existing agents
            agent = self.client_agents[client_agent_key]
            recommendation_agent = self.client_agents[recommendation_agent_key]

        #Form the interaction event to save it
        interaction = {
            "user_id": user_id,
            "product_id": product_id,
            "interaction_type": action_type,
            "duration": duration,
            "description": description,
            "created_at": datetime.utcnow()
        }

        #Notify each agent about the new interaction
        agent.process_interaction(interaction)
        recommendation_agent.process_interaction(interaction)
        self.persist_client_interaction(interaction)
        print("Client Agent after interaction:", self.client_agents)

    def persist_client_interaction(self, interaction_data):
        """Persists the interaction data to MongoDB."""
        try:
            self.interactions_collection.insert_one(interaction_data)
        except Exception as e:
            print(f"Error saving interaction to MongoDB: {e}")

    def get_data(self):
        """Retrieves data for all agents."""
        return {
        "agents": [
            serialize_data({
                **agent.get_data(),
                "id" : str(agent.unique_id)
            }) for agent in self.client_agents.values()
        ]
    }

    def get_user_recommendations(self, user_id: str):
        """Retrieves recommendations for a specific user."""
        recommendation_agent_key = user_id + "recommendation"
        print(self.client_agents)
        if recommendation_agent_key not in self.client_agents:
            return None

        recommendation_agent = self.client_agents[recommendation_agent_key]
        
        # Request interaction history to sync with the client agent
        client_agent_key = user_id
        if client_agent_key in self.client_agents:
             client_agent = self.client_agents[client_agent_key]
             recommendation_agent.request_interaction_history(client_agent)

        return  serialize_data(recommendation_agent.get_data())