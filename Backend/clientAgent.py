import mesa
import pandas as pd
import numpy as np
import seaborn as sns
# class ClientAgent(mesa.Agent):
#     def __init__(self, unique_id, model, preferences):
#         super().__init__(unique_id, model)
#         self.preferences = preferences  # Par exemple, {'electronics', 'clothing'}
#         self.history = []  # Historique des produits vus ou achetés
    
#     def step(self):
#         # L'agent reçoit des recommandations basées sur ses préférences
#         recommended_products = self.model.recommendation_agent.get_recommendations(self)
        
#         # Si l'agent reçoit des recommandations, il interagit avec un produit
#         if recommended_products:
#             product_to_interact_with = self.random.choice(recommended_products)
#             self.interact_with_product(product_to_interact_with)
    
#     def interact_with_product(self, product):
#         # L'agent ajoute ce produit à son historique
#         self.history.append(product)
        
#         # Si le produit appartient à une catégorie préférée, il l'ajoute à ses préférences
#         if product.category not in self.preferences:
#             self.preferences.add(product.category)

#     def __str__(self):
#         return f"Client {self.unique_id}, Préférences: {self.preferences}, Historique: {len(self.history)} produits"

class MoneyAgent(mesa.Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.wealth=1

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        if self.wealth>=1:
            other_agent=self.random.choice(self.model.schedule.agents)
            if other_agent is not None:
                other_agent.wealth += 1
                self.wealth -= 1
        print(f"Hi, I am an agent, you can call me {str(self.unique_id)}. my walth is {str(self.wealth)}")   

class MoneyModel(mesa.Model):
    def __init__(self,N):
        super().__init__()
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        #creation des agent
        for i in range(self.num_agents):
            a = MoneyAgent(i,self)
            self.schedule.add(a)
    def step(self):
        """Advance the model by one step."""
        # The model's step will go here for now this will call the step method of each agent and print the agent's unique_id
        self.schedule.step()

# class MyAgent(mesa.Agent):
#     def __init__(self, name, model):
#         super().__init__(name, model)
#         self.name = name

#     def step(self):
#         print("{} activated".format(self.name))
#         for i in range(3):
#             print(i)
#         # Whatever else the agent does when activated

# class MyModel(mesa.Model):
#     def __init__(self, n_agents):
#         super().__init__()
#         self.schedule = mesa.time.RandomActivation(self)
#         self.grid = mesa.space.MultiGrid(10, 10, torus=True)
#         for i in range(n_agents):
#             a = MyAgent(i, self)
#             self.schedule.add(a)
#             coords = (self.random.randrange(0, 10), self.random.randrange(0, 10))
#             self.grid.place_agent(a, coords)

#     def step(self):
#         self.schedule.step()


starter_model = MoneyModel(10)
starter_model.step()      