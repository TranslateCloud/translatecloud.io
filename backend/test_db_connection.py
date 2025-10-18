import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.config.database import db

def test_connection():
    print('Testing database connection...')
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f'PostgreSQL version: {version}')
        
        cursor.execute('SELECT COUNT(*) as count FROM users;')
        user_count = cursor.fetchone()
        print(f'Users in database: {user_count["count"]}')
        
        cursor.execute('SELECT COUNT(*) as count FROM projects;')
        project_count = cursor.fetchone()
        print(f'Projects in database: {project_count["count"]}')
        
        cursor.execute('SELECT COUNT(*) as count FROM translations;')
        translation_count = cursor.fetchone()
        print(f'Translations in database: {translation_count["count"]}')
        
        cursor.close()
        print('')
        print('Database connection successful!')
        return True
        
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False
    finally:
        db.close()

if __name__ == '__main__':
    test_connection()