import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client
from pydantic import BaseModel
from fastapi import HTTPException

class AuthRequest(BaseModel):
    email: str
    password: str

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.on_event("startup")
def startup_check():
    print("Server running and connected to Supabase")

@app.post("/auth/signup")
def sign_up(auth_request: AuthRequest):

    if not auth_request.email or not auth_request.password:
                raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_up({
            "email": auth_request.email,
            "password": auth_request.password
        })
        return {"message": "User signed up successfully", "user": response.user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def sign_in(auth_request: AuthRequest):
    if not auth_request.email or not auth_request.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_request.email,
            "password": auth_request.password
        })
        return {"message": "User signed in successfully", "user": response.user.email}

    except Exception as e:
        raise HTTPException(status_code=401, detail={"error": "Invalid login credentials"})