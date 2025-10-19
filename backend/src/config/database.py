import psycopg2
from psycopg2.extras import RealDictCursor
from src.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """
    Database connection manager for PostgreSQL (AWS RDS)

    Architecture:
    - Uses environment variables for database credentials (simpler, no IAM needed)
    - SSL/TLS encryption for all connections (sslmode=require)
    - Connection pooling via singleton pattern (reuses connections)
    - Automatic rollback on errors
    """

    def __init__(self):
        self.conn: Optional[psycopg2.extensions.connection] = None

    def connect(self):
        """
        Establish database connection using environment variables

        Environment variables (from .env or Lambda environment):
        - DB_HOST: RDS endpoint (e.g., translatecloud-db-prod.xxx.rds.amazonaws.com)
        - DB_PORT: PostgreSQL port (default: 5432)
        - DB_NAME: Database name (default: postgres)
        - DB_USER: Database username
        - DB_PASSWORD: Database password

        Security:
        - SSL/TLS encryption (sslmode=require) - data encrypted in transit
        - Connection timeout (10s) - prevents hanging
        - RDS publicly accessible with SSL is industry-standard for serverless
        """
        # Reuse existing connection if still open
        if self.conn and not self.conn.closed:
            return self.conn

        # Get database credentials from environment variables
        db_host = settings.DB_HOST
        db_port = settings.DB_PORT or '5432'
        db_name = settings.DB_NAME or 'postgres'
        db_user = settings.DB_USER
        db_password = settings.DB_PASSWORD

        # Validate required credentials are present
        if not all([db_host, db_user, db_password]):
            error_msg = "Missing required database credentials. Set DB_HOST, DB_USER, and DB_PASSWORD environment variables."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Attempting database connection to {db_host}:{db_port}/{db_name}")

        try:
            # Connect to PostgreSQL with SSL encryption
            self.conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
                cursor_factory=RealDictCursor,  # Return results as dictionaries (easier to work with)
                connect_timeout=10,  # Timeout after 10 seconds
                sslmode='require'  # CRITICAL: Enforce SSL/TLS encryption (RDS requirement)
            )
            logger.info(f"✓ Database connection established successfully to {db_host}")
            return self.conn

        except psycopg2.OperationalError as e:
            logger.error(f"✗ Database connection FAILED to {db_host}: {e}")
            logger.error("Possible causes: Wrong credentials, RDS not publicly accessible, security group blocking port 5432")
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected database error: {type(e).__name__} - {e}")
            raise

    def close(self):
        """Close database connection gracefully"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")

    def get_cursor(self):
        """
        Get a database cursor for executing queries

        Returns:
            RealDictCursor: Cursor that returns rows as dictionaries
        """
        conn = self.connect()
        return conn.cursor()

# Singleton database instance (reused across requests for better performance)
db = Database()

def get_db():
    """
    FastAPI dependency for database access

    Usage in endpoints:
        @router.post("/users")
        def create_user(cursor: RealDictCursor = Depends(get_db)):
            cursor.execute("INSERT INTO users ...")

    Features:
    - Automatic transaction management (commit on success, rollback on error)
    - Connection pooling (reuses connections)
    - Automatic cursor cleanup
    - Error handling with detailed logging

    Yields:
        RealDictCursor: Database cursor for executing queries
    """
    cursor = None
    try:
        # Get database cursor (connects to database if needed)
        cursor = db.get_cursor()

        # Yield cursor to the endpoint function
        yield cursor

        # If endpoint succeeds, commit the transaction
        if db.conn:
            db.conn.commit()

    except Exception as e:
        # If endpoint fails, rollback the transaction (undo all changes)
        if db.conn:
            db.conn.rollback()
            logger.error(f"Database transaction rolled back due to error: {e}")
        raise

    finally:
        # Always close the cursor after request completes
        if cursor:
            cursor.close()