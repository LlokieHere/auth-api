import os
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from supabase import create_client, Client
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import FastAPI, Header
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AuthRequest(BaseModel):
    email: str
    password: str

load_dotenv()

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    try:
        bearer, token = authorization.split(" ", 1)
        user = supabase.auth.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})  

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
        return {
            "message": "User signed in successfully",
            "user": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail={"error": "Invalid login credentials"})

@app.get('/public/info')
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get('/protected/profile', dependencies=[Depends(security)])
def protected_profile(user = Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user": {
            "id": user.user.id,
            "email": user.user.email,
            "created_at": user.user.created_at
        }
    }

@app.get('/protected/dashboard', dependencies=[Depends(security)])
def protected_dashboard(user = Depends(get_current_user)):
    return {
        "message": "Welcome to your dashboard",
        "user": {
            "id": user.user.id,
            "email": user.user.email,
            "created_at": user.user.created_at
        }
    }

@app.post('/auth/logout', dependencies=[Depends(security)])
def logout(user = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "Logout failed"})