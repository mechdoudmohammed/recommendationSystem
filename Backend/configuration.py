import boto3
import os
from fastapi import FastAPI, HTTPException, Form,UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# MongoDB configuration
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# Connexion à MongoDB
# client = MongoClient("mongodb://localhost:27017/")
client = MongoClient(f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.vvj3s.mongodb.net/")

db = client["recommandationDB"]
products_collection = db["product"]
categories_collection=db["categories"]
# Load environment variables from .env


# Configuration de Boto3 pour S3
# AWS S3 configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
bucket_name = 'novashop'
# Modèle Pydantic pour les produits
class Product(BaseModel):
    _id: Optional[str] = None 
    name: str
    color: str
    rating: float
    reviewsNumber: int
    description: str
    category: str
    keywords: List[str]
    price: float
    stock: int
    createdAt: Optional[datetime] = None
    photo: Optional[str] = None 

class Category(BaseModel):
    _id: Optional[str] = None
    nameCategorie: str
    photo: Optional[str] = None 