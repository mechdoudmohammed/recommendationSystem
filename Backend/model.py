from mesa import Model, Agent
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Optional
from collections import defaultdict
import random
import configuration as config
import numpy as np


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
            recommendation_agent = RecommendationAgent(recommendation_agent_key, self, user_id=user_id, products_collection=self.products_collection, interactions_collection=self.interactions_collection)
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
    def __init__(self, unique_id, model, user_id=None, products_collection=None, interactions_collection=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.products_collection = products_collection
        self.interactions_collection = interactions_collection
        self.interaction_weights = {
            "view": 0.1,  # Poids pour une vue
            "click": 0.3,  # Poids pour un clic
            "favorite": 0.5,  # Poids pour un favori
            "purchase": 0.6,  # Poids pour un achat
            "search": 0.2 #Poids pour une recherche
        }
        self.interactions = []
        self.last_update = datetime.min  # Keep track of when the agent was last updated
        print(f"Recommendation agent {unique_id} initialized for user {user_id}")

    def calculate_product_scores(self):
         """Calcul les scores des produits en fonction de l'historique d'interaction."""
         product_scores = defaultdict(float)
         user_interactions = self.get_user_interactions_from_db()

         for interaction in user_interactions:
                product_id = interaction["product_id"]
                interaction_type = interaction["interaction_type"]
                weight = self.interaction_weights.get(interaction_type, 0)

                if interaction_type == "view":
                  duration = interaction.get("duration",0)
                  weight *= (1 + duration/300)
                product_scores[product_id] += weight
         return product_scores

    def process_interactions(self, interactions):
        """
        Mise à jour des interactions du client.
        """
        print(f"Recommendation agent {self.unique_id} processing interactions: {interactions}")
        self.interactions.extend(interactions)
        self.last_update = datetime.utcnow()
        print(f"Recommendation agent {self.unique_id} updated. Last update: {self.last_update}")


    def get_user_interactions_from_db(self) -> List[dict]:
         """récupère les interactions de l'utilisateur depuis la base de données."""
         print(f"Recommendation agent {self.unique_id} getting interactions for user {self.user_id}")
         interactions = []
         try:
             interactions = list(self.interactions_collection.find({"user_id": self.user_id}))
             print(f"Recommendation agent {self.unique_id} found {len(interactions)} interactions in db")
             for inter in interactions:
                inter["_id"] = str(inter["_id"])
         except Exception as e:
            print(f"Error fetching user interaction from MongoDB : {e}")
         return interactions


    def get_data(self):
        """Returns the agent data (e.g. recommended products)."""
        print(f"Recommendation agent {self.unique_id} getting data")
        recommended_products = self.recommend_products(8)

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
        """Recommande des produits en fonction de l'historique des interactions."""
        print(f"Recommendation agent {self.unique_id} recommending products for user {self.user_id}.")

        user_interactions = self.get_user_interactions_from_db()
        if not user_interactions:
            print(f"No interaction found for user {self.user_id}. Returning empty recommendations.")
            return []

        # Récupérer les produits déjà achetés et leurs catégories
        purchased_products_info = []
        purchased_categories = set()
        for interaction in user_interactions:
            if interaction["interaction_type"] == "purchase":
                product_info = self.get_products_info(interaction["product_id"])
                if product_info:
                    purchased_products_info.append(product_info[0])
                    purchased_categories.add(product_info[0]["category"])
        # Récupérer les catégories des produits vus ou favoris (éviter d'utiliser des produits achetés)
        categories = set()
        for interaction in user_interactions:
            if interaction["interaction_type"] in ["view", "favorite"] :
                 product_info = self.get_products_info(interaction["product_id"])
                 if product_info:
                     categories.add(product_info[0]["category"])
        
        # Ajouter les categories des produits achetés
        categories.update(purchased_categories)


        if not categories:
            print(f"No categories found for user {self.user_id}. Returning empty recommendations.")
            return []
        
        #Récupérer tous les produits de toutes les categories
        all_products_to_recommend = []
        for category in categories:
            products_in_category = self.get_products_by_category(category)
            if products_in_category:
                 # Filtrer les produits en excluant ceux déjà achetés
                  products_to_recommend = [
                        product
                        for product in products_in_category
                        if product not in purchased_products_info
                    ]
                  all_products_to_recommend.extend(products_to_recommend)

        if not all_products_to_recommend:
             print(f"No products to recommend after filtering. Returning empty recommendations")
             return []
        
        # Calculer les scores pour les produits
        product_scores = self.calculate_product_scores()
        print(f"les score {product_scores}")
        # Assigner un score à chaque produit
        scored_products = []
        for product in all_products_to_recommend:
            score = product_scores.get(product["_id"], 0)  # Récupérer le score du produit, 0 si non trouvé
            scored_products.append((product, score))

        # Trier les produits par score en ordre décroissant
        sorted_products = sorted(scored_products, key=lambda item: item[1], reverse=True)

        # Sélectionner les num_recommendations meilleurs produits
        recommendations = [product for product, score in sorted_products[:num_recommendations]]

        if len(recommendations) < num_recommendations:
            print(f"Found {len(recommendations)} product(s) matching the categories. returning {len(recommendations)} recommendations")
            print(f"Returning {len(recommendations)} product recommendations: {[product['_id'] for product in recommendations]}")
        else:
            print(f"Found {len(all_products_to_recommend)} product(s) matching the categories. returning {num_recommendations} recommendations {[prod['_id'] for prod in recommendations]}")
        return recommendations


    def get_products_info(self, product_id: str) -> List[dict]:
        """
        Récupère les informations d'un produit depuis MongoDB à partir de son ID.
        """
        print(f"Recommendation agent {self.unique_id} getting product info for {product_id}")
        products_info = []

        if not product_id:
             print("No product id provided. returning empty products")
             return products_info

        try:
            products_info = list(self.products_collection.find({"_id": ObjectId(product_id)}))
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