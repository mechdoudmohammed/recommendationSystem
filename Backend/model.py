from mesa import Model
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Optional
from collections import defaultdict
import random
import configuration as config
from agents import ClientAgent, RecommendationAgent, SearchAgent, PersonalizationAgent, AnalyticsAgent

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
        self.message_queue = defaultdict(list)  # Queue pour les messages
        self.search_agents = {}  # Pour les SearchAgents
        self.personalization_agents = {}  # Pour les PersonalizationAgents
        self.analytics_agent = AnalyticsAgent("analytics_agent", self, self.interactions_collection) # Un seul agent d'analyse pour le moment
        print("Model initialized")

    def handle_client_interaction(self, user_id, action_type, product_id, duration, description):
        """Handles a client interaction, updates agents, and persists the interaction."""
        print(f"Handling interaction for user {user_id}, product {product_id}, type {action_type}")
        # Check if the client already has agents
        client_agent_key = user_id
        recommendation_agent_key = user_id + "recommendation"
        search_agent_key = user_id + "search"
        personalization_agent_key = user_id + "personalization"

        if client_agent_key not in self.client_agents:
             print(f"Creating new agents for user {user_id}")
            #Create a new Client Agent and Recommendation Agent
             agent = ClientAgent(client_agent_key, self, user_id=user_id)
             recommendation_agent = RecommendationAgent(recommendation_agent_key, self, user_id=user_id, products_collection=self.products_collection, interactions_collection=self.interactions_collection)
             search_agent = SearchAgent(search_agent_key, self, user_id=user_id, products_collection=self.products_collection)
             personalization_agent = PersonalizationAgent(personalization_agent_key, self, user_id=user_id, interactions_collection=self.interactions_collection)
             self.client_agents[client_agent_key] = agent
             self.client_agents[recommendation_agent_key] = recommendation_agent
             self.search_agents[search_agent_key] = search_agent
             self.personalization_agents[personalization_agent_key] = personalization_agent

        else:
            print(f"Agents already exist for user {user_id}")
            # Get existing agents
            agent = self.client_agents[client_agent_key]
            recommendation_agent = self.client_agents[recommendation_agent_key]
            search_agent = self.search_agents[search_agent_key]
            personalization_agent = self.personalization_agents[personalization_agent_key]


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
        # Envoie un message au modèle pour être distribué
        self.message_queue[recommendation_agent_key].append(interaction)
        self.message_queue[personalization_agent_key].append(interaction)
        self.analytics_agent.process_interaction(interaction) # Ajout d'interaction à l'agent analytics
        self.persist_client_interaction(interaction)


        print("Client Agent after interaction:", self.client_agents)


    def persist_client_interaction(self, interaction_data):
        """Persists the interaction data to MongoDB."""
        try:
            self.interactions_collection.insert_one(interaction_data)
            print(f"Interaction saved to MongoDB: {interaction_data}")
        except Exception as e:
            print(f"Error saving interaction to MongoDB: {e}")

    def get_data(self):
        """Retrieves data for all agents."""
        print("Getting model data")
        return {
            "agents": [
            serialize_data({
                **agent.get_data(),
                "id" : str(agent.unique_id)
            }) for agent in self.client_agents.values()
        ]
           + [
            serialize_data({
                **agent.get_data(),
                "id" : str(agent.unique_id)
            }) for agent in self.search_agents.values()
           ]
           + [
             serialize_data({
                **agent.get_data(),
                "id" : str(agent.unique_id)
             }) for agent in self.personalization_agents.values()
           ] + [
              serialize_data({
                **self.analytics_agent.get_data(),
                "id" : str(self.analytics_agent.unique_id)
            })
           ]
    }

    def get_user_recommendations(self, user_id: str):
        """Retrieves recommendations for a specific user."""
        print(f"Getting recommendations for user {user_id}")
        recommendation_agent_key = user_id + "recommendation"
        print(self.client_agents)
        if recommendation_agent_key not in self.client_agents:
            print(f"Recommendation agent not found for user {user_id}")
            return None

        recommendation_agent = self.client_agents[recommendation_agent_key]
        # Distribuer les messages au RecommendationAgent
        self.process_messages(recommendation_agent)

        return  serialize_data(recommendation_agent.get_data())

    def get_user_search_results(self, user_id: str, query: str):
         """Retrieves search results for a specific user."""
         print(f"Getting search results for user {user_id}, query {query}")
         search_agent_key = user_id + "search"
         if search_agent_key not in self.search_agents:
             print(f"Search agent not found for user {user_id}")
             return None

         search_agent = self.search_agents[search_agent_key]
        # Envoyer la requête de recherche à l'agent de recherche
         return serialize_data(search_agent.search_products(query))

    def get_user_personalized_recommendations(self, user_id: str):
        """Retrieves personalized recommendations for a specific user."""
        print(f"Getting personalized recommendations for user {user_id}")
        personalization_agent_key = user_id + "personalization"
        if personalization_agent_key not in self.personalization_agents:
            print(f"Personalization agent not found for user {user_id}")
            return None

        personalization_agent = self.personalization_agents[personalization_agent_key]
        # Distribuer les messages au PersonalizationAgent
        self.process_messages(personalization_agent)
        return serialize_data(personalization_agent.get_data())


    def process_messages(self, agent):
         """
        Distribue les messages en file d'attente à un agent spécifique
         """
         messages = self.message_queue.get(agent.unique_id, [])
         if messages:
            print(f"Processing messages for agent {agent.unique_id}: {messages}")
            agent.process_interactions(messages)
            # Vider la queue de message pour cet agent après la distribution
            self.message_queue[agent.unique_id] = []
         else:
            print(f"No messages to process for agent {agent.unique_id}")