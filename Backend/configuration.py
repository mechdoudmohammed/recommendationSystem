import boto3
import os
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
from passlib.context import CryptContext


load_dotenv()

# MongoDB configuration
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# Connexion à MongoDB
client = MongoClient(f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.vvj3s.mongodb.net/")
db = client["recommandationDB"]
products_collection = db["product"]
categories_collection = db["categories"]
users_collection = db["users"]
interactions_collection = db["interactions"]

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

# JWT Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token creation function
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Pydantic Models
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

class User(BaseModel):
    _id: Optional[str] = None
    nom: str
    prenom: str
    profileAchat: Optional[str] = None
    comportement: Optional[str] = None
    dateNes: datetime
    Sexe: str
    email: str
    last_active: Optional[datetime] = None
    created_at: Optional[datetime] = None

class UserInDB(User):
    hashed_password: str

class Interaction(BaseModel):
    _id: Optional[str] = None
    user_id: str
    product_id: Optional[str] = None
    interaction_type: str
    duration: Optional[float] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
