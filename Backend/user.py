from fastapi import FastAPI, HTTPException, Form, Query
from typing import Optional, List
from datetime import datetime
import configuration as config

app = FastAPI()

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
    last_active: Optional[datetime] = Form(None)
):
    # Create the user document
    user = {
        "nom": nom,
        "prenom": prenom,
        "profileAchat": profileAchat,
        "comportement": comportement,
        "dateNes": dateNes,
        "Sexe": Sexe,
        "email": email,
        "last_active": last_active or datetime.utcnow(),  # Set to now if not provided
        "created_at": datetime.utcnow()
    }

    # Save the user to MongoDB
    try:
        result = config.users_collection.insert_one(user)
        user["_id"] = str(result.inserted_id)  # Add the inserted_id to the response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving user to MongoDB.")
    
    return user


# Route to get users (with filtering options)
@app.get("/users/")
async def get_users(
    nom: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0)
):
    # Build the query filter
    query_filter = {}
    if nom:
        query_filter["nom"] = nom
    if email:
        query_filter["email"] = email

    # Fetch users from MongoDB
    users = []
    try:
        cursor = (
            config.users_collection.find(query_filter)
            .skip(skip)
            .limit(limit)
        )
        for user in cursor:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
            users.append(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching users from MongoDB.")
    
    return users
