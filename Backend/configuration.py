import boto3
from fastapi import FastAPI, HTTPException, Form,UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from datetime import datetime
# Connexion à MongoDB
client = MongoClient("")
db = client["recommandationDB"]
products_collection = db["product"]
# Configuration de Boto3 pour S3
s3_client = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='us-east-1')
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
    