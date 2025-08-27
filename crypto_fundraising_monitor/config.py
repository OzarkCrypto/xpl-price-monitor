"""
Configuration module for Crypto Fundraising Monitor
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# VC Tier definitions with quality scores
VC_TIERS = {
    'T1': {  # +5 points
        'a16z', 'Sequoia', 'Paradigm', 'Polychain', 'Dragonfly', 'Pantera', 
        'Multicoin', 'Jump', 'Framework', 'Bain', 'Lightspeed', 'Coinbase Ventures',
        'CoinFund', 'Hypersphere', 'Lightspeed Faction'  # Added from website
    },
    'T2': {  # +3 points
        'HashKey', 'Electric', 'Hashed', 'DCG', 'Sky9', 'Spartan', 'Animoca', 
        'NFX', 'Shima', 'Placeholder', 'Variant', 'Mirana Ventures', 'Offchain Labs',
        'Polygon', 'Yunqi Partners', 'Tykhe Ventures', 'Varrock', 'Echo', 'Breed VC',
        'WAGMI Ventures', 'Veris Ventures', 'CRIT Ventures'  # Added from website
    },
    'T3': {  # +2 points
        'Y Combinator', 'YC', 'Techstars', 'OKX Ventures', 'Binance Labs',
        'SBI Holdings', '13bookscapital', 'Mark Ransford'  # Added from website
    }
}

# VC Quality scores mapping
VC_SCORES = {}
for tier, vcs in VC_TIERS.items():
    score = 5 if tier == 'T1' else (3 if tier == 'T2' else 2)
    for vc in vcs:
        VC_SCORES[vc.lower()] = score

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1339285013')
HIGHLIGHT_THRESHOLD = int(os.getenv('HIGHLIGHT_THRESHOLD', '7'))
RUN_TIMEZONE = os.getenv('RUN_TIMEZONE', 'Asia/Seoul')

# Scraping configuration
BASE_URL = 'https://crypto-fundraising.info/'
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Database configuration
DB_PATH = 'crypto_fundraising_state.db'

# Message configuration
MAX_MESSAGE_LENGTH = 4096
SAFE_SPLIT_LENGTH = 3800  # Split before reaching max length
HEADER_MESSAGE = "📋 Daily Crypto Fundraising (New)"

# Validation
def validate_config():
    """Validate required configuration"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is required. Please set it in .env file or environment variables."
        )
    
    try:
        int(TELEGRAM_CHAT_ID)
    except ValueError:
        raise ValueError("TELEGRAM_CHAT_ID must be a valid integer")
    
    if HIGHLIGHT_THRESHOLD < 0:
        raise ValueError("HIGHLIGHT_THRESHOLD must be non-negative")
    
    return True 