"""
Supabase database connection
"""
from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger


# Initialize Supabase client
try:
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error("Failed to initialize Supabase client", e)
    raise

