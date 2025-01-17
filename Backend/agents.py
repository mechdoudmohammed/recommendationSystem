from mesa import Agent
from typing import List, Dict, Optional
from bson import ObjectId
from collections import defaultdict
from datetime import datetime
import random
import configuration as config

class ClientAgent(Agent):
    def __init__(self, unique_id, model, user_id=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.interactions = []
        print(f"Client agent {unique_id} initialized for user {user_id}")
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
    def __init__(self, unique_id, model, user_id=None, products_collection=None, interactions_collection=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.products_collection = products_collection
        self.interactions_collection = interactions_collection
        self.interaction_weights = {
            "view": 0.1,  # Poids pour une vue
            "click": 0.2,  # Poids pour un clic
            "favorite": 0.4,  # Poids pour un favori
            "purchase": 0.5,  # Poids pour un achat
            "search": 0.3, #Poids pour une recherche
            "addToCart": 0.2 #Poids pour une recherche
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


class SearchAgent(Agent):
    def __init__(self, unique_id, model, user_id=None, products_collection=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.products_collection = products_collection
        print(f"Search agent {unique_id} initialized for user {user_id}")
        # Assurer que l'index est créé une seule fois
        self.ensure_text_index()

    def ensure_text_index(self):
        """Vérifie et crée l'index textuel s'il n'existe pas."""
        index_info = self.products_collection.index_information()
        if "name_text" not in index_info:
            self.products_collection.create_index([("name", "text")], name="name_text")
            print("Text index created on 'name' field for SearchAgent.")
        else:
            print("Text index on 'name' field already exists for SearchAgent.")
            
    def search_products(self, query: str, skip: int = 0, limit: int = 10) -> List[dict]:
        """
        Recherche des produits à partir d'une query.
        """
        print(f"Search agent {self.unique_id} searching for products with query: {query}, skip: {skip}, limit: {limit}")
        if not query:
            print("No query provided. Returning empty search results")
            return []

        results = []
        try:
             results = list(self.products_collection.find({"$text": {"$search": query}}).skip(skip).limit(limit))
             for res in results:
                res["_id"] = str(res["_id"])
        except Exception as e:
             print(f"Error fetching search results from MongoDB : {e}")
        print(f"Search agent {self.unique_id} returning search results: {results}")
        return results

    def get_data(self):
        print(f"Search agent {self.unique_id} getting data")
        return {
            "user_id": self.user_id,
            "type": "search_agent"
        }


class PersonalizationAgent(Agent):
      def __init__(self, unique_id, model, user_id=None, interactions_collection=None):
        super().__init__(unique_id, model)
        self.user_id = user_id
        self.interactions_collection = interactions_collection
        self.interactions = []
        self.last_update = datetime.min
        print(f"Personalization agent {unique_id} initialized for user {user_id}")

      def process_interactions(self, interactions):
          """
            Mise à jour des interactions du client.
           """
          print(f"Personalization agent {self.unique_id} processing interactions: {interactions}")
          self.interactions.extend(interactions)
          self.last_update = datetime.utcnow()
          print(f"Personalization agent {self.unique_id} updated. Last update: {self.last_update}")

      def get_user_interactions_from_db(self) -> List[dict]:
         """récupère les interactions de l'utilisateur depuis la base de données."""
         print(f"Personalization agent {self.unique_id} getting interactions for user {self.user_id}")
         interactions = []
         try:
             interactions = list(self.interactions_collection.find({"user_id": self.user_id}))
             print(f"Personalization agent {self.unique_id} found {len(interactions)} interactions in db")
             for inter in interactions:
                inter["_id"] = str(inter["_id"])
         except Exception as e:
            print(f"Error fetching user interaction from MongoDB : {e}")
         return interactions


      def get_data(self):
         """Returns the agent data (e.g. recommended products)."""
         print(f"Personalization agent {self.unique_id} getting data")
         recommended_products = self.recommend_products(5)
         return {
             "user_id": self.user_id,
             "recommended_products": [
                 {**product, "_id": str(product.get("_id"))} for product in recommended_products
             ] if recommended_products else [],
             "interaction_history": self.interactions,
             "type": "personalization_agent",
             "last_update": self.last_update
         }

      def recommend_products(self, num_recommendations:int):
            """Recommande des produits en fonction de l'historique des interactions."""
            print(f"Personalization agent {self.unique_id} recommending products for user {self.user_id}.")
            user_interactions = self.get_user_interactions_from_db()
            if not user_interactions:
                print(f"No interaction found for user {self.user_id}. Returning empty recommendations.")
                return []

            product_ids = [interaction.get("product_id") for interaction in user_interactions if interaction.get("product_id")]
            if not product_ids:
                print(f"No products_id in interaction. Returning empty recommendations.")
                return []
            #Récupérer les produits associés au id
            products_info = self.get_products_info(product_ids)
            if not products_info:
                print(f"No product info found for user {self.user_id}. Returning empty recommendations.")
                return []

            #Selectionner un certain nombre de produits de maniere random
            if len(products_info) <= num_recommendations:
                return products_info
            return random.sample(products_info, num_recommendations)

      def get_products_info(self, product_ids: List[str]) -> List[dict]:
           """
          Récupère les informations des produits depuis MongoDB à partir de leurs IDs.
          """
           print(f"Personalization agent {self.unique_id} getting products info for ids {product_ids}")
           products_info = []

           if not product_ids:
               return products_info

           try:
               products_info = list(self.model.products_collection.find({"_id": {"$in": [ObjectId(id) for id in product_ids]}}))
               for prod in products_info:
                   prod["_id"] = str(prod["_id"])
           except Exception as e:
               print(f"Error fetching products info from MongoDB : {e}")
               return []
           print(f"Personalization agent {self.unique_id} returning products info from db {products_info}")
           return products_info


class AnalyticsAgent(Agent):
    def __init__(self, unique_id, model, interactions_collection=None):
        super().__init__(unique_id, model)
        self.interactions_collection = interactions_collection
        self.interactions = []
        print(f"Analytics agent {unique_id} initialized")
    def process_interaction(self, interaction):
        """Enregistre une interaction."""
        print(f"Analytics agent {self.unique_id} processing interaction: {interaction}")
        self.interactions.append(interaction)
    def get_data(self):
        """Returns the agent's analysis data."""
        print(f"Analytics agent {self.unique_id} getting data")
        metrics = self.calculate_metrics()
        return {
            "type": "analytics_agent",
            "metrics": metrics
         }
    def calculate_metrics(self):
        """Calculates and returns key metrics."""
        print(f"Analytics agent {self.unique_id} calculating metrics")
        num_interactions = len(self.interactions)
        purchase_interactions = [inter for inter in self.interactions if inter["interaction_type"] == "purchase"]
        num_purchases = len(purchase_interactions)

        if num_interactions > 0:
          conversion_rate = (num_purchases / num_interactions) * 100
        else:
           conversion_rate = 0
        # Exemple de récupération des produits les plus populaires
        product_counts = defaultdict(int)
        for interaction in self.interactions:
           product_id = interaction.get("product_id")
           if product_id:
            product_counts[product_id] += 1
        most_popular_products = sorted(product_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        return {
             "num_interactions": num_interactions,
             "num_purchases": num_purchases,
             "conversion_rate": conversion_rate,
             "most_popular_products": most_popular_products
        }