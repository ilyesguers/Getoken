"""
Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from database.db import Base
import enum


class AccountStatus(enum.Enum):
    """Account status enumeration"""
    CREATING = "creating"
    MATURING = "maturing"
    READY = "ready"
    ACTIVE = "active"
    BANNED = "banned"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class TaskStatus(enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Account(Base):
    """Facebook account model"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Facebook credentials
    fb_email = Column(String(255), unique=True, index=True, nullable=False)
    fb_password = Column(String(255), nullable=False)
    fb_user_id = Column(String(100), index=True, nullable=True)
    fb_profile_url = Column(String(500), nullable=True)
    
    # Profile information (Arabic names)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    gender = Column(String(10), nullable=False)  # male/female
    birth_date = Column(String(20), nullable=False)
    city = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Profile picture
    profile_photo_path = Column(String(500), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    
    # Account status and tracking
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.CREATING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    matured_at = Column(DateTime(timezone=True), nullable=True)
    last_active = Column(DateTime(timezone=True), nullable=True)
    banned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Proxy information
    proxy_address = Column(String(255), nullable=True)
    proxy_port = Column(Integer, nullable=True)
    proxy_type = Column(String(20), nullable=True)  # http/https/socks5
    
    # Statistics
    total_ratings_given = Column(Integer, default=0)
    total_comments_made = Column(Integer, default=0)
    total_likes_given = Column(Integer, default=0)
    total_friends_added = Column(Integer, default=0)
    
    # Anti-detection
    user_agent = Column(String(500), nullable=True)
    fingerprint_hash = Column(String(100), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Account(id={self.id}, email={self.fb_email}, status={self.status})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "fb_email": self.fb_email,
            "display_name": self.display_name,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "matured_at": self.matured_at.isoformat() if self.matured_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "total_ratings_given": self.total_ratings_given,
            "total_comments_made": self.total_comments_made,
            "city": self.city,
        }


class Task(Base):
    """Rating/Review task model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Target information
    target_profile_url = Column(String(500), nullable=False)
    target_type = Column(String(50), nullable=False)  # marketplace/page/post/profile
    
    # Task configuration
    total_ratings_needed = Column(Integer, default=1)
    rating_type = Column(String(50), default="stars")  # stars/comments/both
    
    # Task execution
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    ratings_completed = Column(Integer, default=0)
    accounts_assigned = Column(JSON, default=list)  # List of account IDs
    
    # Configuration
    config = Column(JSON, default=dict)  # Additional settings
    
    # Notes
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Task(id={self.id}, target={self.target_profile_url}, status={self.status})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "target_profile_url": self.target_profile_url,
            "target_type": self.target_type,
            "total_ratings_needed": self.total_ratings_needed,
            "ratings_completed": self.ratings_completed,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress_percentage": (self.ratings_completed / self.total_ratings_needed * 100) 
                                   if self.total_ratings_needed > 0 else 0,
        }


class Rating(Base):
    """Individual rating/review model"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    account_id = Column(Integer, nullable=False, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    
    # Rating content
    stars = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)
    rating_type = Column(String(50), nullable=False)  # stars/comments/likes
    
    # Target
    target_url = Column(String(500), nullable=False)
    
    # Status
    status = Column(String(50), default="pending")  # pending/success/failed
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Rating(id={self.id}, account_id={self.account_id}, stars={self.stars})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "task_id": self.task_id,
            "stars": self.stars,
            "comment": self.comment,
            "rating_type": self.rating_type,
            "target_url": self.target_url,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ActivityLog(Base):
    """Activity log for monitoring"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Activity information
    log_type = Column(String(50), nullable=False)  # account_creation/rating/error/system
    account_id = Column(Integer, nullable=True, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    
    # Log content
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    level = Column(String(20), default="info")  # info/warning/error/critical
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, type={self.log_type}, level={self.level})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "log_type": self.log_type,
            "account_id": self.account_id,
            "task_id": self.task_id,
            "message": self.message,
            "level": self.level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Proxy(Base):
    """Proxy management"""
    __tablename__ = "proxies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Proxy information
    address = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    proxy_type = Column(String(20), default="http")  # http/https/socks5
    
    # Status
    is_active = Column(Boolean, default=True)
    is_working = Column(Boolean, default=True)
    last_checked = Column(DateTime(timezone=True), nullable=True)
    response_time = Column(Float, nullable=True)  # milliseconds
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    times_failed = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Source
    source = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Proxy(id={self.id}, address={self.address}, port={self.port})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "address": self.address,
            "port": self.port,
            "proxy_type": self.proxy_type,
            "is_active": self.is_active,
            "is_working": self.is_working,
            "response_time": self.response_time,
            "times_used": self.times_used,
        }
