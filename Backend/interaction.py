from fastapi import FastAPI, HTTPException, Form, Query
from typing import Optional, List
from datetime import datetime
import configuration as config

app = FastAPI()

# Route to add an interaction
@app.post("/add_interaction/")
async def add_interaction(
    user_id: str = Form(...),
    product_id:Optional[str] = Form(None),
    interaction_type: str = Form(...),
    duration: Optional[float] = Form(None),  # Optional duration
    description: Optional[str] = Form(None)
):
    # Create the interaction document
    interaction = {
        "user_id": user_id,
        "product_id": product_id,
        "interaction_type": interaction_type,
        "duration": duration,
        "description": description,
        "created_at": datetime.utcnow()
    }

    # Save the interaction to MongoDB
    try:
        result = config.interactions_collection.insert_one(interaction)
        interaction["_id"] = str(result.inserted_id)  # Add the inserted_id to the response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving interaction to MongoDB.")
    
    return interaction


# Route to get all interactions (with filtering options)
@app.get("/interactions/")
async def get_interactions(
    user_id: Optional[str] = Query(None),
    product_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0)
):
    # Build the query filter
    query_filter = {}
    if user_id:
        query_filter["user_id"] = user_id
    if product_id:
        query_filter["product_id"] = product_id

    # Fetch interactions from MongoDB
    interactions = []
    try:
        cursor = (
            config.interactions_collection.find()
            .skip(skip)
            .limit(limit)
        )
        for interaction in cursor:
            interaction["_id"] = str(interaction["_id"])  # Convert ObjectId to string
            interactions.append(interaction)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching interactions from MongoDB.")
    
    return interactions
