from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from uuid import uuid4
from enum import Enum
import json
import os
from collections import OrderedDict

app = FastAPI()

# File path for JSON storage
JSON_FILE = "users.json"

# Helper functions for file operations
def read_users() -> Dict[str, dict]:
    if not os.path.exists(JSON_FILE):
        return {}
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def write_users(users: Dict[str, dict], new_id: str = None):
    # Sort the users so that new_id (if provided) comes first
    ordered_users = OrderedDict()
    
    # If there's a new ID, add it first
    if new_id and new_id in users:
        ordered_users[new_id] = users[new_id]
    
    # Add all other users
    for k, v in users.items():
        if k != new_id:
            ordered_users[k] = v
    
    with open(JSON_FILE, 'w') as f:
        json.dump(ordered_users, f, indent=4, ensure_ascii=False)

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

# User model
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    age: int
    gender: Gender
    phone_number: Optional[str] = None
    address: Optional[str] = None

# Create user
@app.post("/users/", response_model=User)
def create_user(user: User):
    users = read_users()
    user_id = str(uuid4())
    user.id = user_id
    users[user_id] = user.dict()
    write_users(users, new_id=user_id)  # Pass the new ID to ensure it's written first
    return user

# Get all users
@app.get("/users/", response_model=List[User])
def get_users():
    users = read_users()
    return [User(**user_data) for user_data in users.values()]

# Get user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    users = read_users()
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**users[user_id])

# Update user
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: User):
    users = read_users()
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user.id = user_id
    users[user_id] = user.dict()
    write_users(users, new_id=user_id)  # Move updated user to top
    return user

# Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    users = read_users()
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    write_users(users)
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
