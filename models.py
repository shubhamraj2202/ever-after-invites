"""
Database Models for Event Invitation Platform
Designed for multi-tenant SaaS with theme marketplace
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    User accounts for the platform
    Phase 1: Simple password auth
    Phase 2: Google OAuth integration
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Null for OAuth users

    # OAuth fields (for Google Login - Phase 2)
    oauth_provider = Column(String, nullable=True)  # "google", "facebook", etc.
    oauth_id = Column(String, nullable=True)  # Provider's user ID

    # Profile
    full_name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Subscription (for paid tiers - Phase 3)
    subscription_tier = Column(String, default="free")  # free, basic, premium
    subscription_expires = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationships
    events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")
    purchased_themes = relationship("ThemePurchase", back_populates="user")


class Event(Base):
    """
    Events created by users (weddings, birthdays, etc.)
    Each user can have multiple events
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Event details
    title = Column(String, nullable=False)  # "Sonakshi & Shubham's Wedding"
    event_type = Column(String, nullable=False)  # "wedding", "engagement", "birthday"
    slug = Column(String, unique=True, index=True, nullable=False)  # URL: /events/sonakshi-shubham

    # Theme
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)

    # Configuration (JSON - stores config.json equivalent)
    config = Column(JSON, nullable=False)  # Entire config.json as JSON

    # Custom domain (Phase 4)
    custom_domain = Column(String, unique=True, nullable=True)

    # Analytics
    view_count = Column(Integer, default=0)
    rsvp_count = Column(Integer, default=0)

    # Status
    is_published = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    event_date = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="events")
    theme = relationship("Theme", back_populates="events")
    guests = relationship("Guest", back_populates="event", cascade="all, delete-orphan")


class Theme(Base):
    """
    Themes available in the marketplace
    Phase 1: Free default themes
    Phase 3: Paid premium themes
    """
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)

    # Theme details
    name = Column(String, unique=True, nullable=False)  # "Beach Wedding", "Modern Minimalist"
    description = Column(String, nullable=True)
    preview_image = Column(String, nullable=True)

    # Pricing (Phase 3)
    is_premium = Column(Boolean, default=False)
    price = Column(Float, default=0.0)  # In USD or INR

    # Files (stored in cloud storage - Phase 4)
    html_template = Column(String, nullable=True)  # Path to template
    css_file = Column(String, nullable=True)
    js_file = Column(String, nullable=True)

    # Default config schema
    default_config = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    events = relationship("Event", back_populates="theme")
    purchases = relationship("ThemePurchase", back_populates="theme")


class ThemePurchase(Base):
    """
    Track theme purchases (e-commerce - Phase 3)
    """
    __tablename__ = "theme_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=False)

    # Payment details
    amount_paid = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_provider = Column(String, nullable=True)  # "stripe", "razorpay"
    transaction_id = Column(String, nullable=True)

    # Metadata
    purchased_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="purchased_themes")
    theme = relationship("Theme", back_populates="purchases")


class Guest(Base):
    """
    Guest list and RSVP tracking (Phase 2)
    """
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    # Guest details
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # RSVP
    rsvp_status = Column(String, default="pending")  # pending, accepted, declined
    rsvp_date = Column(DateTime, nullable=True)
    plus_one = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="guests")


# Phase 1: We won't use database yet, just config.json
# Phase 2: Migrate to database with these models
# Phase 3: Add payment tables, theme marketplace
# Phase 4: Add analytics, custom domains, etc.
