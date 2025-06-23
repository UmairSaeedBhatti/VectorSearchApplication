import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration module for the application

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DB', 'sample_mflix')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'movies')

# Weaviate Configuration
WEAVIATE_URL = os.getenv('WEAVIATE_URL', 'http://localhost:8080')
WEAVIATE_CLASS = 'Movie'
WEAVIATE_RETRY_MAX = 5
WEAVIATE_RETRY_DELAY = 2  # seconds

# Streamlit Configuration
DEFAULT_RESULTS = 5
SIMILARITY_METRICS = ['cosine', 'dot']
SEARCH_ALGORITHMS = ['hybrid', 'BM25F', 'vector']

# Get Weaviate configuration
def get_weaviate_config():
    return {
        'url': WEAVIATE_URL,
        'retry_max': WEAVIATE_RETRY_MAX,
        'retry_delay': WEAVIATE_RETRY_DELAY
    }

    # Streamlit Configuration
    DEFAULT_RESULTS = 5
    SIMILARITY_METRICS = ['cosine', 'dot']
    SEARCH_ALGORITHMS = ['hybrid', 'BM25F', 'vector']
