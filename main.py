from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import uuid4

app = FastAPI()

# User model
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    age: int

# In-memory storage
users: Dict[str, User] = {}

# Create user
@app.post("/users/", response_model=User)
def create_user(user: User):
    user_id = str(uuid4())
    user.id = user_id
    users[user_id] = user
    return user

# Get all users
@app.get("/users/", response_model=List[User])
def get_users():
    return list(users.values())

# Get user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

# Update user
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: User):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user.id = user_id
    users[user_id] = user
    return user

# Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
