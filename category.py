from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from typing import List, Optional
from datetime import datetime
import configuration as config

# Route to add a category
async def add_category(
    nameCategorie: str = Form(...),
    file: UploadFile = File(...)):
    
    # Construct category data
    category = {
        "nameCategorie": nameCategorie,
        "photo": None  # Set to None initially, will update if file is uploaded
    }
    
    file_name = f"{category['nameCategorie']}_{datetime.utcnow().isoformat()}.jpg"
    try:
        # Upload file to S3 and get the URL
        config.s3_client.upload_fileobj(file.file, config.bucket_name, file_name)
        file_url = f"https://{config.bucket_name}.s3.amazonaws.com/{file_name}"
        category["photo"] = file_url  # Assign the file URL to the category photo
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error uploading file to S3.")
    
    # Save category data to MongoDB
    try:
        result = config.categories_collection.insert_one(category)
        category["_id"] = str(result.inserted_id)  # Add inserted_id to the returned category
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving category to MongoDB.")
    
    return category


# Route to get all categories
async def get_categories(skip: int = 0, limit: int = 10):
    categories = []
    cursor = (
        config.categories_collection.find()
        .skip(skip)
        .limit(limit)
    )
    for category in cursor:
        category["_id"] = str(category["_id"])  # Convert ObjectId to string
        categories.append(category)
    return categories
