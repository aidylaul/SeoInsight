"""
Database Manager for SEO Analysis
Handles all PostgreSQL database operations
"""

import os
import json
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
from contextlib import contextmanager
from seo_analyzer import get_url_variations


class DatabaseManager:
    """Handle database operations for SEO analysis results"""
    
    def __init__(self):
        self.connection = None
        # Use DATABASE_URL instead of individual parameters for better compatibility
        self.database_url = os.getenv('DATABASE_URL')
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            if self.connection:
                self.connection.close()
            self.connection = psycopg2.connect(self.database_url)
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            self.connection = None
    
    def ensure_connection(self):
        """Ensure database connection is active"""
        try:
            if self.connection is None or self.connection.closed:
                self.connect()
            else:
                # Test connection with a simple query
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.connect()
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database operations"""
        self.ensure_connection()
        if not self.connection:
            raise Exception("Database connection failed")
        
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def save_analysis(self, seo_data: Dict, analysis: Dict, score: int) -> bool:
        """Save SEO analysis results to database"""
        try:
            with self.get_cursor() as cursor:
                # Extract domain from URL
                domain = urlparse(seo_data.get('url', '')).netloc
                
                query = """
                INSERT INTO seo_analyses (
                    url, domain, title, meta_description, meta_keywords,
                    og_tags, twitter_tags, h1_tags, canonical,
                    seo_score, analysis_results
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    seo_data.get('url', ''),
                    domain,
                    seo_data.get('title', ''),
                    seo_data.get('meta_description', ''),
                    seo_data.get('meta_keywords', ''),
                    json.dumps(seo_data.get('og_tags', {})),
                    json.dumps(seo_data.get('twitter_tags', {})),
                    json.dumps(seo_data.get('h1_tags', [])),
                    seo_data.get('canonical', ''),
                    score,
                    json.dumps(analysis)
                ))
                
            return True
            
        except Exception as e:
            print(f"Failed to save analysis: {str(e)}")
            return False
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Get recent SEO analyses from database"""
        try:
            with self.get_cursor() as cursor:
                query = """
                SELECT url, domain, title, seo_score, analyzed_at
                FROM seo_analyses
                ORDER BY analyzed_at DESC
                LIMIT %s
                """
                
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                
                return [
                    {
                        'url': row[0],
                        'domain': row[1],
                        'title': row[2],
                        'seo_score': row[3],
                        'analyzed_at': row[4]
                    }
                    for row in results
                ]
                
        except Exception as e:
            print(f"Failed to fetch analyses: {str(e)}")
            return []
    
    def get_analysis_by_url(self, url: str) -> Optional[Dict]:
        """Get the most recent analysis for a specific URL"""
        try:
            with self.get_cursor() as cursor:
                # Get URL variations for flexible matching
                unique_variations = get_url_variations(url)
                
                query = """
                SELECT url, title, meta_description, og_tags, twitter_tags, 
                       h1_tags, seo_score, analysis_results, analyzed_at
                FROM seo_analyses
                WHERE url = ANY(%s)
                ORDER BY analyzed_at DESC
                LIMIT 1
                """
                
                cursor.execute(query, (unique_variations,))
                result = cursor.fetchone()
            
            if result:
                # Helper function to safely parse JSON
                def safe_json_loads(data):
                    if data is None:
                        return {}
                    if isinstance(data, (dict, list)):
                        return data  # Already parsed
                    try:
                        return json.loads(data)
                    except (json.JSONDecodeError, TypeError):
                        return {}
                
                return {
                    'url': result[0],
                    'title': result[1] or '',
                    'meta_description': result[2] or '',
                    'og_tags': safe_json_loads(result[3]),
                    'twitter_tags': safe_json_loads(result[4]),
                    'h1_tags': safe_json_loads(result[5]) if result[5] else [],
                    'seo_score': result[6],
                    'analysis_results': safe_json_loads(result[7]),
                    'analyzed_at': result[8]
                }
            
            return None
            
        except Exception as e:
            print(f"Failed to fetch analysis for URL: {str(e)}")
            return None