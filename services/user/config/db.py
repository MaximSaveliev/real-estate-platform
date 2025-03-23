import json
import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import get_settings
import uuid
from typing import Optional, Dict, Any, List

settings = get_settings()

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Connect to the PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                dbname=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                cursor_factory=RealDictCursor
            )
            print(f"Connected to {settings.POSTGRES_DB} database")
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def create_tables(self):
        """Create database tables if they don't exist"""
        with self.conn.cursor() as cursor:
            # Create roles table (simplified, without permissions field)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)

            # Create users table with bio field
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    profile_image_url VARCHAR(255),
                    bio TEXT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    role_id INTEGER REFERENCES roles(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)

            # Create agencies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agencies (
                    id UUID PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    logo_url VARCHAR(255),
                    address TEXT,
                    phone VARCHAR(20),
                    email VARCHAR(255),
                    website VARCHAR(255),
                    admin_id UUID REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)

            # Create agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    user_id UUID PRIMARY KEY REFERENCES users(id),
                    agency_id UUID REFERENCES agencies(id),
                    license_number VARCHAR(100),
                    years_of_experience INTEGER,
                    specialization VARCHAR(100),
                    bio TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)

            self.conn.commit()
            print("Database tables created")

    def ensure_default_role(self):
        """Ensure that default roles exist and return the user role ID"""
        with self.conn.cursor() as cursor:
            # Check if any roles exist
            cursor.execute("SELECT COUNT(*) as count FROM roles;")
            count = cursor.fetchone()["count"]
            
            if count == 0:
                # Create default roles
                roles = [
                    ("admin",),
                    ("agency_admin",),
                    ("agent",),
                    ("user",)
                ]
                
                for role in roles:
                    cursor.execute(
                        """
                        INSERT INTO roles (name)
                        VALUES (%s);
                        """,
                        role
                    )
                
            # Get user role ID
            cursor.execute("SELECT id FROM roles WHERE name = %s;", ("user",))
            role = cursor.fetchone()
            self.conn.commit()
            return role["id"]

    def create_user(
        self, 
        id: str,
        email: str, 
        password_hash: str, 
        first_name: str, 
        last_name: str, 
        role_id: int,
        phone: Optional[str] = None,
        profile_image_url: Optional[str] = None,
        bio: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new user in the database"""
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO users (
                        id, email, password_hash, first_name, last_name, 
                        role_id, phone, profile_image_url, bio
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id, email, first_name, last_name, phone, 
                            profile_image_url, bio, is_verified, is_active, role_id;
                    """,
                    (
                        id, email, password_hash, first_name, last_name, 
                        role_id, phone, profile_image_url, bio
                    )
                )
                result = cursor.fetchone()
                self.conn.commit()
                return result
            except Exception as e:
                self.conn.rollback()
                print(f"Error creating user: {e}")
                return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    id, email, first_name, last_name, phone, 
                    profile_image_url, bio, is_verified, is_active, role_id
                FROM users
                WHERE id = %s;
                """,
                (user_id,)
            )
            return cursor.fetchone()
            
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    id, email, first_name, last_name, phone, 
                    profile_image_url, bio, is_verified, is_active, role_id
                FROM users
                WHERE email = %s;
                """,
                (email,)
            )
            return cursor.fetchone()
            
    def update_user(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        profile_image_url: Optional[str] = None,
        bio: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update user profile information"""
        with self.conn.cursor() as cursor:
            # Get current user data
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                return None
                
            # Update only provided fields
            update_fields = []
            params = []
            
            if first_name is not None:
                update_fields.append("first_name = %s")
                params.append(first_name)
            
            if last_name is not None:
                update_fields.append("last_name = %s")
                params.append(last_name)
                
            if phone is not None:
                update_fields.append("phone = %s")
                params.append(phone)
                
            if profile_image_url is not None:
                update_fields.append("profile_image_url = %s")
                params.append(profile_image_url)
                
            if bio is not None:
                update_fields.append("bio = %s")
                params.append(bio)
                
            # Add updated_at field
            update_fields.append("updated_at = NOW()")
            
            if not update_fields:
                return user
                
            # Build update query
            query = f"""
                UPDATE users 
                SET {", ".join(update_fields)}
                WHERE id = %s
                RETURNING id, email, first_name, last_name, phone, 
                        profile_image_url, bio, is_verified, is_active, role_id;
            """
            
            params.append(user_id)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from the database"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    id, email, first_name, last_name, phone, 
                    profile_image_url, bio, is_verified, is_active, role_id
                FROM users
                ORDER BY created_at DESC;
                """
            )
            return cursor.fetchall()

database = Database()