from fastapi import FastAPI, HTTPException, Form,UploadFile, File
from typing import List, Optional
from datetime import datetime
import configuration as config

async def add_product(
    name: str = Form(...),
    color: str = Form(...),
    rating: float = Form(...),
    reviewsNumber: int = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    keywords: List[str] = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    file: UploadFile = File(...)):

  # Construct product data
    product = config.Product(
        name=name,
        color=color,
        rating=rating,
        reviewsNumber=reviewsNumber,
        description=description,
        category=category,
        keywords=keywords,
        price=price,
        stock=stock,
        createdAt=datetime.utcnow()
    )
    file_name = f"{product.name}_{datetime.utcnow().isoformat()}.jpg"
    try:
        config.s3_client.upload_fileobj(file.file, config.bucket_name, file_name)
        file_url = f"https://{config.bucket_name}.s3.amazonaws.com/{file_name}"
        product.photo = file_url
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error uploading file to S3.")

    # Save product data to MongoDB
    product_dict = product.dict(by_alias=True)
    try:
        result = config.products_collection.insert_one(product_dict)
        product_dict["_id"] = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving product to MongoDB.")

    return product_dict
async def get_products(skip: int = 0, limit: int = 10):
    products = []
    cursor = (
        config.products_collection.find()
        .skip(skip)
        .limit(limit)
    )
    for product in cursor:
        product["_id"] = str(product["_id"])  # Conversion de l'ObjectId en str
        products.append(product)
    return products


async def search_products_by_name(query: str, skip: int = 0, limit: int = 10):
    # Split the query into terms
    terms = query.split()

    # Create a list of regex conditions for each term
    regex_conditions = [{"name": {"$regex": term, "$options": "i"}} for term in terms]
    
    # Combine all regex conditions with an OR logic (i.e., any term must match)
    combined_query = {"$or": regex_conditions}

    products = []
    cursor = (
        config.products_collection.find(combined_query)
        .skip(skip)
        .limit(limit)
    )

    for product in cursor:
        product["_id"] = str(product["_id"])  # Convert ObjectId to string
        products.append(product)

    return products
async def search_products_by_category(category_name: str, skip: int = 0, limit: int = 10):
    # Create a condition for category search (case-insensitive)
    category_condition = {"category": {"$regex": category_name, "$options": "i"}}

    products = []
    cursor = (
        config.products_collection.find(category_condition)
        .skip(skip)
        .limit(limit)
    )

    for product in cursor:
        product["_id"] = str(product["_id"])  # Convert ObjectId to string
        products.append(product)

    return products

