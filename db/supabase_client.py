"""Supabase client for cognitive API"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import httpx

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials in .env file")

def get_supabase() -> Client:
    """Return a singleton Supabase client with proper HTTP/2 handling"""
    # Create httpx client with HTTP/1.1 only (more stable on Render)
    # This fixes the StreamReset error
    http_client = httpx.Client(
        http2=False,  # Disable HTTP/2 to avoid connection resets
        timeout=30.0,  # 30 second timeout
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options={
            'client': http_client
        }
    )
