from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import hashlib
from app.db import get_db
from app.db.models import User, Organization, APIKey
from app.core.config import settings
import jwt
from clerk_backend_api import Clerk


def get_database() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    yield from get_db()


# Initialize Clerk client
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

# Security scheme for API keys
api_key_scheme = HTTPBearer(scheme_name="API Key")


async def get_current_user_from_clerk(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_database)
) -> Optional[User]:
    """Get current user from Clerk JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        
        # Verify JWT token with Clerk
        # Note: In production, you'd want to verify the JWT properly
        # For now, we'll extract the user ID and look up the user
        
        # Decode without verification for development
        # In production, use proper JWT verification with Clerk's public key
        payload = jwt.decode(token, options={"verify_signature": False})
        clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            return None
        
        # Find user in database
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        return user
        
    except Exception:
        return None


async def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(api_key_scheme),
    db: Session = Depends(get_database)
) -> Optional[User]:
    """Get current user from API key"""
    if not credentials or not credentials.credentials:
        return None
    
    api_key = credentials.credentials
    
    # Hash the API key to find it in database
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Find API key in database
    api_key_record = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key_record:
        return None
    
    # Update last used timestamp
    from datetime import datetime
    api_key_record.last_used_at = datetime.utcnow()
    db.commit()
    
    # Return the user who created the API key
    return db.query(User).filter(User.id == api_key_record.created_by_user_id).first()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_database)
) -> User:
    """Get current authenticated user (from Clerk token or API key)"""
    user = None
    
    # Try Clerk authentication first
    if authorization and authorization.startswith("Bearer "):
        user = await get_current_user_from_clerk(authorization, db)
    
    # If no user from Clerk, try API key authentication
    if not user and authorization and authorization.startswith("Bearer "):
        try:
            from fastapi.security import HTTPAuthorizationCredentials
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=authorization.split(" ")[1]
            )
            user = await get_current_user_from_api_key(credentials, db)
        except Exception:
            pass
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> Organization:
    """Get current user's organization"""
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_database)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None