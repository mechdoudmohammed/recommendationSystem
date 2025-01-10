from fastapi import FastAPI, HTTPException, Form, Query
from typing import Optional, List
from datetime import datetime
import configuration as config
from fastapi.security import OAuth2PasswordBearer



app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Route to add a user
@app.post("/users/")
async def add_user(
    nom: str = Form(...),
    prenom: str = Form(...),
    profileAchat: Optional[str] = Form(None),  # Optional
    comportement: Optional[str] = Form(None),  # Optional
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


# Function to fetch users with pagination
async def get_users(skip=0, limit=10):
    try:
        users = list(config.users_collection.find().skip(skip).limit(limit))
        for user in users:
            user["_id"] = str(user["_id"])
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")


# Login route for JWT token
@app.post("/login/")
async def login_for_access_token(email: str = Form(...), password: str = Form(...)):
    user = config.users_collection.find_one({"email": email})
    if not user or not config.verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = config.create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
