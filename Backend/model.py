from mesa import Model, Agent
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Optional
from collections import defaultdict
import random
import configuration as config

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
        print("Model initialized")

    def handle_client_interaction(self, user_id, action_type, product_id, duration, description):
        """Handles a client interaction, updates agents, and persists the interaction."""
        print(f"Handling interaction for user {user_id}, product {product_id}, type {action_type}")
        # Check if the client already has agents
        client_agent_key = user_id
        recommendation_agent_key = user_id + "recommendation"

        if client_agent_key not in self.client_agents:
            print(f"Creating new agents for user {user_id}")
            #Create a new Client Agent and Recommendation Agent
            agent = ClientAgent(client_agent_key, self, user_id=user_id)
            recommendation_agent = RecommendationAgent(recommendation_agent_key, self, user_id=user_id)
            self.client_agents[client_agent_key] = agent
            self.client_agents[recommendation_agent_key] = recommendation_agent

        else:
            print(f"Agents already exist for user {user_id}")
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
        # Envoie un message au modèle pour être distribué
        self.message_queue[recommendation_agent_key].append(interaction)
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


    def process_messages(self, recommendation_agent):
         """
        Distribue les messages en file d'attente à un agent spécifique
         """
         messages = self.message_queue.get(recommendation_agent.unique_id, [])
         if messages:
            print(f"Processing messages for recommendation agent {recommendation_agent.unique_id}: {messages}")
            recommendation_agent.process_interactions(messages)
            # Vider la queue de message pour cet agent après la distribution
            self.message_queue[recommendation_agent.unique_id] = []
         else:
            print(f"No messages to process for recommendation agent {recommendation_agent.unique_id}")


class ClientAgent(Agent):
    def __init__(self, unique_id, model, user_id=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.interactions = []
        print(f"Client agent {unique_id} initialized for user {user_id}")


    def process_interaction(self, interaction):
        """Enregistre une interaction."""
        print(f"Client agent {self.unique_id} processing interaction: {interaction}")
        self.interactions.append(interaction)

    def get_interaction_history(self):
       """Returns the client's interaction history"""
       print(f"Client agent {self.unique_id} returning interaction history")
       return self.interactions

    def get_data(self):
        print(f"Client agent {self.unique_id} getting data")
        return {
            "user_id": self.user_id,
            "interaction_history": [
                {**interaction, "product_id": str(interaction.get("product_id"))} if interaction.get("product_id") else interaction for interaction in self.interactions
            ],
            "type" : "client_agent"
        }

class RecommendationAgent(Agent):
    def __init__(self, unique_id, model, user_id=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.interactions = []
        self.products_collection = config.products_collection
        self.last_category = None
        self.last_update = datetime.min  # Keep track of when the agent was last updated
        print(f"Recommendation agent {unique_id} initialized for user {user_id}")


    def process_interactions(self, interactions):
        """
        Mise à jour des interactions du client et détermination de la catégorie.
        """
        print(f"Recommendation agent {self.unique_id} processing interactions: {interactions}")
        for interaction in interactions:
             self.interactions.append(interaction)
             if 'product_id' in interaction and interaction['product_id']:
                product_info = self.get_products_info([interaction['product_id']])
                if product_info:
                    self.last_category = product_info[0].get('category')

        self.last_update = datetime.utcnow()
        print(f"Recommendation agent {self.unique_id} updated. Last update: {self.last_update}, last category: {self.last_category}")

    def get_data(self):
        """Returns the agent data (e.g. recommended products)."""
        print(f"Recommendation agent {self.unique_id} getting data")
        recommended_products = self.recommend_products(3)

        return {
            "user_id": self.user_id,
            "recommended_products": [
                {**product, "_id": str(product.get("_id"))} for product in recommended_products
            ] if recommended_products else [],
            "interaction_history": self.interactions,
            "type": "recommendation_agent",
            "last_update": self.last_update
        }


    def recommend_products(self, num_recommendations):
         """
            Recommends products from the last viewed category randomly
            Args:
                num_recommendations (int): The number of recommendations to make.
         """
         print(f"Recommendation agent {self.unique_id} recommending products. Last category: {self.last_category}")
         if not self.last_category:
             print(f"No last category. returning empty recommendations")
             return []

         # Fetch all products in the same category
         products_info = self.get_products_by_category(self.last_category)
         if not products_info:
            print(f"No products found in category {self.last_category}. returning empty recommendations")
            return []

         if len(products_info) <= num_recommendations:
             print(f"Found {len(products_info)} product(s) matching the category {self.last_category}. returning {len(products_info)} recommendations")
             return products_info

         # Return a random selection of products
         recommendation = random.sample(products_info, num_recommendations)
         print(f"Found {len(products_info)} product(s) matching the category {self.last_category}. returning {num_recommendations} recommendations {recommendation}")
         return recommendation


    def get_products_info(self, product_ids: List[str]) -> List[dict]:
        """
        Récupère les informations des produits depuis MongoDB à partir de leurs IDs.
        """
        print(f"Recommendation agent {self.unique_id} getting products info for {product_ids}")
        products_info = []

        if not product_ids:
             print("No product ids provided. returning empty products")
             return products_info

        try:
            products_info = list(self.products_collection.find({"_id": {"$in": [ObjectId(id) for id in product_ids]}}))
            for prod in products_info:
                prod["_id"] = str(prod["_id"])
        except Exception as e:
            print(f"Error fetching products info from MongoDB : {e}")
            return []

        print(f"Returning product info from mongodb: {products_info}")
        return products_info


    def get_products_by_category(self, category: str) -> List[dict]:
        """
        Récupère les informations des produits depuis MongoDB à partir de leurs categories
        """
        print(f"Recommendation agent {self.unique_id} getting products by category: {category}")
        products_info = []

        if not category:
             print("No category provided. returning empty products")
             return products_info

        try:
            products_info = list(self.products_collection.find({"category": category}))
            for prod in products_info:
                prod["_id"] = str(prod["_id"])
        except Exception as e:
            print(f"Error fetching products info from MongoDB : {e}")
            return []

        print(f"Returning products from mongodb by category {category} : {products_info}")
        return products_info