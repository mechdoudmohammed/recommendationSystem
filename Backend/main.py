from fastapi import FastAPI, HTTPException, Form,UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import product as pd
import category as ctg
import configuration as config

app = FastAPI()

# Route pour récupérer tous les produits
@app.get("/products")
async def get_product(skip: int = 0, limit: int = 10):
    return await pd.get_products(skip=skip,limit=limit)

# Route pour ajouter un produit avec image
# @app.post("/products", response_model=Product)
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
    file: UploadFile = File(...)
):
    # Call the add_product function from product.py
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
    file: UploadFile = File(...)):
    
    # Appel de la fonction add_category depuis configuration.py
    return await ctg.add_category(
        nameCategorie=nameCategorie,
        file=file
    )