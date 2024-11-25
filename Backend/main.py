from fastapi import FastAPI, HTTPException, Form,UploadFile, File
from pydantic import BaseModel
from typing import List, Optional,Dict
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

# Route for searching products by name
@app.get("/search_products_by_name/")
async def search_products_by_name_route(
    query: str,  # The search query (product name)
    skip: int = 0,  # Pagination: number of results to skip
    limit: int = 10  # Pagination: number of results to return
):
    # Call the function to search products by name
    return await pd.search_products_by_name(query=query, skip=skip, limit=limit)


# Route for searching products by category
@app.get("/search_products_by_category/")
async def search_products_by_category_route(
    category_name: str,  # The search query (category name)
    skip: int = 0,  # Pagination: number of results to skip
    limit: int = 10  # Pagination: number of results to return
):
    # Call the function to search products by category
    return await pd.search_products_by_category(category_name=category_name, skip=skip, limit=limit)
# Route to get products grouped by category

@app.get("/products_grouped_by_category/")
async def get_products_grouped_by_category_route(
    skip: int = 0,  # Pagination: number of results to skip
    limit: int = 10  # Pagination: number of results to return
) -> List[Dict]:
    # Call the function to get products grouped by category
    products = await pd.get_products_grouped_by_category(skip=skip, limit=limit)
    return products