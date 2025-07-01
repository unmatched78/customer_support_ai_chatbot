#!/usr/bin/env python3
"""
Migration script to upgrade database to multi-tenant schema
This script will:
1. Create new multi-tenant tables
2. Migrate existing data to new schema
3. Create a default organization for existing data
"""

import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.db.base import Base
from app.db.models import (
    Organization, User, APIKey, 
    Conversation, Message, SystemPrompt, Customer, SupportAction,
    OrganizationPlan, OrganizationStatus, UserRole
)


def create_database_engine():
    """Create database engine"""
    return create_engine(settings.DATABASE_URL, echo=True)


def create_default_organization(session):
    """Create a default organization for existing data"""
    # Check if default organization already exists
    existing_org = session.query(Organization).filter(Organization.slug == "default").first()
    if existing_org:
        print("Default organization already exists")
        return existing_org
    
    # Create default organization
    default_org = Organization(
        name="Default Organization",
        slug="default",
        plan=OrganizationPlan.PROFESSIONAL,
        status=OrganizationStatus.ACTIVE,
        settings={
            "migrated_from_single_tenant": True,
            "migration_date": datetime.now(timezone.utc).isoformat()
        },
        branding={
            "primary_color": "#1976d2",
            "company_name": "Default Organization"
        },
        max_users=50,
        max_api_keys=10,
        max_conversations_per_month=10000,
        max_knowledge_base_size_mb=1000
    )
    
    session.add(default_org)
    session.commit()
    session.refresh(default_org)
    
    print(f"Created default organization with ID: {default_org.id}")
    return default_org


def create_default_user(session, organization):
    """Create a default admin user"""
    # Check if default user already exists
    existing_user = session.query(User).filter(User.email == "admin@default.com").first()
    if existing_user:
        print("Default user already exists")
        return existing_user
    
    # Create default admin user
    default_user = User(
        clerk_user_id="default_admin_user",
        organization_id=organization.id,
        email="admin@default.com",
        first_name="Default",
        last_name="Admin",
        role=UserRole.OWNER,
        is_active=True
    )
    
    session.add(default_user)
    session.commit()
    session.refresh(default_user)
    
    print(f"Created default user with ID: {default_user.id}")
    return default_user


def migrate_existing_data(session, organization, default_user):
    """Migrate existing data to multi-tenant schema"""
    
    # Check if we have any existing conversations without organization_id
    existing_conversations = session.execute(
        text("SELECT COUNT(*) FROM conversations WHERE organization_id IS NULL")
    ).scalar()
    
    if existing_conversations == 0:
        print("No existing conversations to migrate")
        return
    
    print(f"Migrating {existing_conversations} existing conversations...")
    
    # Update existing conversations
    session.execute(
        text("UPDATE conversations SET organization_id = :org_id WHERE organization_id IS NULL"),
        {"org_id": organization.id}
    )
    
    # Update existing messages
    session.execute(
        text("UPDATE messages SET organization_id = :org_id WHERE organization_id IS NULL"),
        {"org_id": organization.id}
    )
    
    # Update existing system prompts
    session.execute(
        text("""
            UPDATE system_prompts 
            SET organization_id = :org_id, created_by_user_id = :user_id 
            WHERE organization_id IS NULL
        """),
        {"org_id": organization.id, "user_id": default_user.id}
    )
    
    # Update existing customers
    session.execute(
        text("UPDATE customers SET organization_id = :org_id WHERE organization_id IS NULL"),
        {"org_id": organization.id}
    )
    
    # Update existing support actions
    session.execute(
        text("UPDATE support_actions SET organization_id = :org_id WHERE organization_id IS NULL"),
        {"org_id": organization.id}
    )
    
    session.commit()
    print("Migration completed successfully!")


def create_sample_api_key(session, organization, user):
    """Create a sample API key for testing"""
    import hashlib
    import secrets
    
    # Generate a sample API key
    api_key = f"sk_test_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    sample_api_key = APIKey(
        organization_id=organization.id,
        created_by_user_id=user.id,
        name="Default API Key",
        key_hash=key_hash,
        key_prefix=api_key[:12],
        scopes=["read", "write"],
        rate_limit_per_minute=100,
        rate_limit_per_hour=1000,
        rate_limit_per_day=10000,
        is_active=True
    )
    
    session.add(sample_api_key)
    session.commit()
    
    print(f"Created sample API key: {api_key}")
    print("IMPORTANT: Save this API key as it won't be shown again!")
    
    return sample_api_key


def main():
    """Main migration function"""
    print("Starting multi-tenant database migration...")
    
    # Create engine and session
    engine = create_database_engine()
    SessionLocal = sessionmaker(bind=engine)
    
    # Create all tables
    print("Creating new database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Start migration
    session = SessionLocal()
    
    try:
        # Create default organization
        default_org = create_default_organization(session)
        
        # Create default user
        default_user = create_default_user(session, default_org)
        
        # Migrate existing data
        migrate_existing_data(session, default_org, default_user)
        
        # Create sample API key
        create_sample_api_key(session, default_org, default_user)
        
        print("\n" + "="*50)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Default Organization ID: {default_org.id}")
        print(f"Default Organization Slug: {default_org.slug}")
        print(f"Default User ID: {default_user.id}")
        print(f"Default User Email: {default_user.email}")
        print("\nYour application is now multi-tenant ready!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()