# visualisation.py
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from model import ECommerceModel  # Importez votre modèle ici
import configuration as config

class AgentDataElement(TextElement):
   def render(self, model):
        agent_data = model.get_data()
        return f"<pre>{agent_data}</pre>" # Vous affichez en mode texte mais vous pouver créer une fonction plus personalisé

def agent_portrayal(agent): # Nous n'avons pas de grille mais on doit quand meme ajouter cette fonction pour que Mesa fonctionne correctement
    portrayal = { "Shape": "circle",
                   "Color": "red",
                   "Filled": "true",
                   "Layer": 0,
                   "r": 0.5 }
    return portrayal

if __name__ == '__main__':
  model = ECommerceModel() # Initialize your Mesa Model

  agent_data_element = AgentDataElement()
  canvas_element = CanvasGrid(agent_portrayal, 1, 1, 500, 500) # Dummy canvas grid as Mesa needs at least one, we wont use it to show the agents positions

  server = ModularServer(
        ECommerceModel,
        [canvas_element,agent_data_element], # Add the visualization module
        "ECommerce Model",
        {},
  )

  server.port = 8521
  server.launch()