import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
import json
from src.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.credentials: Optional[dict] = None
    
    def get_secret(self):
        if self.credentials:
            return self.credentials
        
        client = boto3.client('secretsmanager', region_name=settings.AWS_REGION)
        
        try:
            response = client.get_secret_value(SecretId=settings.DATABASE_SECRET_ARN)
            self.credentials = json.loads(response['SecretString'])
            return self.credentials
        except Exception as e:
            logger.error(f"Error retrieving secret: {e}")
            raise
    
    def connect(self):
        if self.conn and not self.conn.closed:
            return self.conn

        creds = self.get_secret()

        logger.info(f"Attempting database connection to {creds['host']}")

        try:
            self.conn = psycopg2.connect(
                host=creds['host'],
                port=creds['port'],
                database=creds['database'],
                user=creds['username'],
                password=creds['password'],
                cursor_factory=RealDictCursor,
                connect_timeout=10,  # 10 seconds timeout
                sslmode='require'  # RDS requires SSL
            )
            logger.info(f"Database connection established successfully to {creds['host']}")
            return self.conn
        except Exception as e:
            logger.error(f"Database connection FAILED to {creds['host']}: {type(e).__name__} - {e}")
            raise
    
    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")
    
    def get_cursor(self):
        conn = self.connect()
        return conn.cursor()

db = Database()

def get_db():
    cursor = None
    try:
        cursor = db.get_cursor()
        yield cursor
        if db.conn:
            db.conn.commit()
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()