from fastapi import FastAPI, HTTPException, Form, UploadFile, File, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import product as pd
import category as ctg
import configuration as config
import user as usr
from fastapi.middleware.cors import CORSMiddleware
from model import ECommerceModel  # Importez votre modèle ici
import interaction as itn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',  # Allow specific origin (your React app)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
model = ECommerceModel()

# User routes from user.py are now included in main.py
@app.post("/add_user/")
async def add_user(
    nom: str = Form(...),
    prenom: str = Form(...),
    profileAchat: Optional[str] = Form(None),
    comportement: Optional[str] = Form(None),
    dateNes: datetime = Form(...),
    Sexe: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    last_active: Optional[datetime] = Form(None)
):
    hashed_password = config.hash_password(password)
    user = {
        "nom": nom,
        "prenom": prenom,
        "profileAchat": profileAchat,
        "comportement": comportement,
        "dateNes": dateNes,
        "Sexe": Sexe,
        "email": email,
        "password": hashed_password,
        "last_active": last_active or datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    try:
        result = config.users_collection.insert_one(user)
        user["_id"] = str(result.inserted_id)
        del user["password"]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving user to MongoDB.")
    
    return user

@app.get("/users/")
async def get_users(skip: int = 0, limit: int = 10):
    return await usr.get_users(skip=skip, limit=limit)


# Route pour récupérer tous les produits
@app.get("/products")
async def get_product(skip: int = 0, limit: int = 10):
    return await pd.get_products(skip=skip, limit=limit)

# Route pour ajouter un produit avec image
@app.post("/add_product/")
async def create_product(
    name: str = Form(...),
    color: str = Form(...),
    rating: float = Form(...),
    reviewsNumber: int = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    keywords: List[str] = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    file: UploadFile = File(...),
):
    return await pd.add_product(
        name=name,
        color=color,
        rating=rating,
        reviewsNumber=reviewsNumber,
        description=description,
        category=category,
        keywords=keywords,
        price=price,
        stock=stock,
        file=file
    )

# Route pour récupérer toutes les catégories
@app.get("/categories")
async def get_categories(skip: int = 0, limit: int = 10):
    return await ctg.get_categories(skip=skip, limit=limit)

# Route pour ajouter une catégorie avec image
@app.post("/add_category/")
async def create_category(
    nameCategorie: str = Form(...),
    file: UploadFile = File(...),
):
    return await ctg.add_category(nameCategorie=nameCategorie, file=file)



# Route for searching products by id
@app.get("/search_product_by_id/")
async def search_product_by_id_route(product_id: str):
    return await pd.search_product_by_id(product_id=product_id)



# Route for searching products by category
@app.get("/search_products_by_category/")
async def search_products_by_category_route(
    category_name: str,
    skip: int = 0,
    limit: int = 10
):
    return await pd.search_products_by_category(category_name=category_name, skip=skip, limit=limit)

# Route to get products grouped by category
@app.get("/products_grouped_by_category/")
async def get_products_grouped_by_category_route(
    skip: int = 0,
    limit: int = 10
) -> List[Dict]:
    return await pd.get_products_grouped_by_category(skip=skip, limit=limit)

# Route to add an interaction
@app.post("/add_interaction/")
async def add_interaction(
    user_id: str = Form(...),
    product_id: Optional[str] = Form(None),
    interaction_type: Optional[str] = Form(None),
    duration: Optional[float] = Form(None),
    description: Optional[str] = Form(None)
):
    return await itn.add_interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=interaction_type,
        duration=duration,
        description=description
    )

# Route to get interactions
@app.get("/interactions/")
async def get_interactions(
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    return await itn.get_interactions(
        user_id=user_id,
        product_id=product_id,
        skip=skip,
        limit=limit
    )


@app.post("/login/")
async def login_for_access_token(
    email: str = Form(...),
    password: str = Form(...)
):
    # Récupérer l'utilisateur depuis la base de données par son email
    user = config.users_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Vérifier le mot de passe
    if not config.verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Convertir l'ObjectId en chaîne
    user["_id"] = str(user["_id"])
    
    # Créer le token JWT
    access_token = config.create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "user": user}


#multi agent commance ici


class InteractionData(BaseModel):
    user_id: str
    interaction_type: str
    product_id: str
    duration: Optional[int] = None
    description: Optional[str] = None

@app.post("/simulation/step")
async def simulation_step(interaction_data: InteractionData):
    """
    Endpoint to simulate a client interaction.
    """
    try:
        model.handle_client_interaction(
           interaction_data.user_id,
           interaction_data.interaction_type,
           interaction_data.product_id,
           interaction_data.duration,
           interaction_data.description,
        )
        return {"message": "Interaction processed"}

    except Exception as e:
      print(f"Error processing interaction: {e}")
      raise HTTPException(status_code=500, detail=f"Error processing interaction : {e}")


class RecommendationRequest(BaseModel):
    user_id: str

@app.post("/simulation/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Endpoint to retrieve recommendations for a specific user using a POST request.
    """
    try:
        user_id = request.user_id
        recommendations = model.get_user_recommendations(user_id)
        if recommendations is None:
          raise HTTPException(status_code=404, detail="Recommendation agent not found for user")

        return {"user_id": user_id, "recommendations": recommendations}
    except Exception as e:
      print(f"Error retrieving recommendations: {e}")
      raise HTTPException(status_code=404, detail=f"Error retrieving recommendations: {e}")
    
class SearchProductByNameRequest(BaseModel):
    user_id: str
    query: str
    skip: int = 0
    limit: int = 10

@app.post("/simulation/search_products_by_name/")
async def search_products_by_name_route(request: SearchProductByNameRequest):
        """
        Endpoint pour rechercher des produits par nom en utilisant l'agent Search.
        """
        try:
            user_id = request.user_id
            query = request.query
            skip = request.skip
            limit = request.limit

            search_results = model.get_user_search_results(user_id, query)
            if search_results is None:
                raise HTTPException(status_code=404, detail="Search agent not found for user")
            
            return {"user_id": user_id, "query": query, "results": search_results}
        except Exception as e:
            print(f"Error retrieving search results: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving search results: {e}")
    

@app.get("/simulation/agents")
async def get_agents():
    """
    Endpoint to get the current agents and their data.
    """
    try:
        agents_data = model.get_data()
        return agents_data
    except Exception as e:
        print(f"Error retrieving agents data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving agents data: {e}")