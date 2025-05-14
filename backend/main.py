from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic import BaseModel

app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", ],  # Allows your frontend origin
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

class Item(BaseModel):
    login: str
    password: str

@app.post("/buttonlogin")
def auth(data: Item):
    print(data)
    return {"message": "hello"}

@app.get("/buttonlogin")
def auth_get(auth_item: Item):  # Changed function name to avoid conflict
    print(auth_item)
    return {"message": "GET response"}

@app.get("/")
def home():
    return {"message": "hello"}