from fastapi import FastAPI, HTTPException, Form,UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import product as pd
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
