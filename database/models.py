from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table, MetaData
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base declarative model
Base = declarative_base()

# Global session factory
SessionLocal = None

# User-Role many-to-many relationship
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, backref="users")
    sessions = relationship("UserSession", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

class Role(Base):
    """Role model for user permissions"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    def __repr__(self):
        return f"<Role {self.name}>"

class UserSession(Base):
    """Store user sessions for tracking login status"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(64), unique=True, nullable=False)
    ip_address = Column(String(39))  # IPv6 compatible
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession {self.session_id}>"

class FileUpload(Base):
    """Track uploaded files"""
    __tablename__ = 'file_uploads'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)  # Size in bytes
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<FileUpload {self.filename}>"

class AuditLog(Base):
    """Audit logs for tracking user actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50))  # Type of object being acted upon
    entity_id = Column(Integer)       # ID of object being acted upon
    description = Column(Text)
    ip_address = Column(String(39))  # IPv6 compatible
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"

# Config storage in database
class SystemConfig(Base):
    """System configuration storage"""
    __tablename__ = 'system_configs'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemConfig {self.key}>"

def initialize_database(db_config: Dict[str, Any]) -> None:
    """Initialize the database connection and create tables if they don't exist.
    
    Args:
        db_config: Dictionary containing database configuration
    """
    global SessionLocal
    
    try:
        # Create connection string based on database type
        if db_config.get('type', 'mssql').lower() == 'mysql':
            connection_string = (
                f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
        else:  # Default to MSSQL
            if db_config.get('trusted', 'yes').lower() == 'yes':
                connection_string = (
                    f"mssql+pyodbc://{db_config.get('server', 'localhost')}/"
                    f"{db_config.get('database', 'QLTAIKHOAN')}?"
                    f"driver={db_config.get('driver', '{ODBC Driver 17 for SQL Server}')}"
                    "&trusted_connection=yes"
                )
            else:
                connection_string = (
                    f"mssql+pyodbc://{db_config.get('username', '')}:{db_config.get('password', '')}"
                    f"@{db_config.get('server', 'localhost')}/"
                    f"{db_config.get('database', 'QLTAIKHOAN')}?"
                    f"driver={db_config.get('driver', '{ODBC Driver 17 for SQL Server}')}"
                )
        
        # Create engine with connection pooling and timeout settings
        engine = create_engine(
            connection_string,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True  # Test connections before use
        )
        
        # Configure session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False  # Better for web applications
        )

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.critical(f"Database initialization failed: {str(e)}", exc_info=True)
        raise