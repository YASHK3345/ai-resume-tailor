from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import User, UserCreate, UserLogin, UserResponse
from auth.auth import hash_password, verify_password, create_access_token, get_current_user
from auth.oauth import GoogleOAuth
import os

# Get database dependency
async def get_database() -> AsyncIOMotorClient:
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncIOMotorClient = Depends(get_database)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name
    )
    
    # Save to database
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    result = await db.users.insert_one(user_dict)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return UserResponse(**user.dict())

@router.post("/login")
async def login(credentials: UserLogin, db: AsyncIOMotorClient = Depends(get_database)):
    """Login user and return access token"""
    
    # Find user
    user_data = await db.users.find_one({"email": credentials.email})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(credentials.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_data["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user_data)
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(lambda: get_current_user(db=get_database()))
):
    """Get current user information"""
    return UserResponse(**current_user.dict())

@router.get("/google/url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    auth_url = GoogleOAuth.get_auth_url()
    return {"auth_url": auth_url}

@router.post("/google/callback")
async def google_oauth_callback(code: str, db: AsyncIOMotorClient = Depends(get_database)):
    """Handle Google OAuth callback"""
    
    try:
        # Exchange code for token
        token_data = await GoogleOAuth.exchange_code_for_token(code)
        
        # Get user info
        user_info = await GoogleOAuth.get_user_info(token_data["access_token"])
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_info["email"]})
        
        if existing_user:
            # User exists, log them in
            user = User(**existing_user)
        else:
            # Create new user
            user = User(
                email=user_info["email"],
                full_name=user_info.get("name", "")
            )
            
            # Save to database
            user_dict = user.dict()
            user_dict["oauth_provider"] = "google"
            user_dict["oauth_id"] = user_info["id"]
            
            await db.users.insert_one(user_dict)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user.dict())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )