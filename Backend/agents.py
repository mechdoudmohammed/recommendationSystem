from mesa import Agent
from typing import List, Dict, Optional
from bson import ObjectId
from collections import defaultdict
from datetime import datetime
import configuration as config  # Importez le fichier de configuration
import random

class ClientAgent(Agent):
    def __init__(self, unique_id, model, user_id=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.interactions = []


    def process_interaction(self, interaction):
        """Enregistre une interaction."""
        self.interactions.append(interaction)

    def get_interaction_history(self):
       """Returns the client's interaction history"""
       return self.interactions
    
    def get_data(self):
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
        self.last_category = None  # Keep track of the user's most recently interacted category

    def request_interaction_history(self, client_agent):
        """
        Asks the client agent for his interaction history and extracts category from the last product interaction
        """
        self.interactions = client_agent.get_interaction_history()

        # Retrieve the category of the most recent product interaction
        if self.interactions:
            last_interaction = self.interactions[-1]
            if 'product_id' in last_interaction and last_interaction['product_id']:
                product_info = self.get_products_info([last_interaction['product_id']])
                if product_info:
                     self.last_category = product_info[0].get('category')


    def process_interaction(self, interaction):
        """
        We need to have this method for a good execution,
        but we are going to use interaction history requested on
        request_interaction_history method,
        """
        pass

    def get_data(self):
        """Returns the agent data (e.g. recommended products)."""
        recommended_products = self.recommend_products(3)

        return {
            "user_id": self.user_id,
            "recommended_products": [
                {**product, "_id": str(product.get("_id"))} for product in recommended_products
            ] if recommended_products else [],
            "interaction_history": self.interactions,
            "type": "recommendation_agent"
        }

    def recommend_products(self, num_recommendations):
         """
            Recommends products from the last viewed category randomly
            Args:
                num_recommendations (int): The number of recommendations to make.
         """
         if not self.last_category:
             return []
         
         # Fetch all products in the same category
         products_info = self.get_products_by_category(self.last_category)
         if not products_info:
            return []

         if len(products_info) <= num_recommendations:
             return products_info
         
         # Return a random selection of products
         return random.sample(products_info, num_recommendations)


    def get_products_info(self, product_ids: List[str]) -> List[dict]:
        """
        Récupère les informations des produits depuis MongoDB à partir de leurs IDs.
        """
        products_info = []

        if not product_ids:
            return products_info

        try:
            products_info = list(self.products_collection.find({"_id": {"$in": [ObjectId(id) for id in product_ids]}}))
            for prod in products_info:
                prod["_id"] = str(prod["_id"])
        except Exception as e:
            print(f"Error fetching products info from MongoDB : {e}")
            return []

        return products_info

    def get_products_by_category(self, category: str) -> List[dict]:
        """
        Récupère les informations des produits depuis MongoDB à partir de leurs categories
        """
        products_info = []

        if not category:
            return products_info

        try:
            products_info = list(self.products_collection.find({"category": category}))
            for prod in products_info:
                prod["_id"] = str(prod["_id"])
        except Exception as e:
            print(f"Error fetching products info from MongoDB : {e}")
            return []

        return products_info