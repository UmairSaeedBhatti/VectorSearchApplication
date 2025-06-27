import streamlit as st
import weaviate
from weaviate.client import Client
from weaviate.auth import AuthClientPassword
from pymongo import MongoClient
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os
import torch
import time
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def init_mongodb_client():
    try:
        import os
        from dotenv import load_dotenv
        from pymongo import MongoClient
        
        # Load local environment variables if available
        if os.path.exists('.env.local'):
            load_dotenv('.env.local')
        
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        
        # If no URI is set, use local MongoDB
        if not mongodb_uri:
            mongodb_uri = "mongodb://localhost:27017"
            st.info("Using local MongoDB instance")
        
        # Initialize MongoDB client
        client = MongoClient(mongodb_uri)
        
        # Test connection
        try:
            client.admin.command('ping')
            st.success("MongoDB connection successful!")
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {str(e)}")
            return None
            
        return client
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        st.info("Please make sure MongoDB is running and accessible")
        return None

def init_weaviate_client():
    try:
        import os
        import weaviate
        from weaviate.classes.init import Auth
        
        # Load credentials from environment variables
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        if not weaviate_url or not weaviate_api_key:
            raise ValueError("WEAVIATE_URL and WEAVIATE_API_KEY must be set in environment variables")
            
        # Connect to Weaviate Cloud
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=Auth.api_key(weaviate_api_key)
        )
        
        if client.is_ready():
            st.success("Weaviate Cloud connection successful!")
            return client
        else:
            raise Exception("Weaviate connection failed")
    except Exception as e:
        st.error(f"Failed to connect to Weaviate: {str(e)}")
        return None
        
        if client.is_ready():
            st.success("Weaviate Cloud connection successful!")
            return client
        else:
            raise Exception("Weaviate connection failed")
    except Exception as e:
        st.error(f"Failed to connect to Weaviate: {str(e)}")
        st.info("Please make sure Weaviate is running and accessible")
        return None
        

def init_model():
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        
        # Initialize model first
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Using device: {device}")
        
        # Move model to device
        model._first_module().auto_model = model._first_module().auto_model.to(device)
        
        # Verify model is on correct device
        if next(model.parameters()).device.type != device:
            st.error("Model device mismatch!")
            return None
        
        st.success("Model initialized successfully!")
        return model
    except Exception as e:
        st.error(f"Failed to initialize model: {str(e)}")
        st.info("Please make sure PyTorch and sentence-transformers are properly installed")
        return None

weaviate_client = init_weaviate_client()
mongo_client = init_mongodb_client()
model = init_model()

if weaviate_client is None or mongo_client is None or model is None:
    st.error("Failed to initialize one or more components. Please check your configuration and try again.")
    st.stop()

db = mongo_client['movies_db']
collection = db['movies']

# Add a prominent header with developer credit
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 20px;'>
    <h1 style='color: #2E74B5; margin: 0; padding: 10px 0;'>Movie Search App</h1>
    <p style='font-size: 18px; color: #666; margin: 0; padding: 10px 0;'>Developed by <span style='color: #2E74B5; font-weight: bold;'>Umair Saeed</span></p>
</div>
""", unsafe_allow_html=True)

# Add a separator
st.markdown("""
<hr style='border: 1px solid #eee; margin: 20px 0; opacity: 0.5;'>
""", unsafe_allow_html=True)

# Search history
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Add search examples
st.markdown("### Search Examples:")
examples = [
    "corn and bread",
    "wheat",
    "poverty",
    "1909",
    "D.W. Griffith"
]

def handle_search_click(query):
    st.session_state.query = query
    st.session_state.search_history.append(query)

for example in examples:
    st.button(f"Search: {example}", key=f"search_{example}", on_click=handle_search_click, args=(example,))

# Display search history
if st.session_state.search_history:
    st.markdown("### Recent Searches:")
    for i, hist_query in enumerate(st.session_state.search_history[-5:]):
        if st.button(f"{hist_query}", key=f"history_{i}", on_click=handle_search_click, args=(hist_query,)):
            st.session_state.query = hist_query

# Main search interface
query = st.text_input("Enter your search query:", key="query")

# Sidebar configuration
with st.sidebar:
    st.header("Search Configuration")
    
    num_results = st.slider(
        "Number of Results",
        min_value=1,
        max_value=20,
        value=10,
        step=1,
        key="num_results_slider"
    )
    
    search_type = st.selectbox(
        "Search Type",
        ["Semantic Search", "Exact Match"],
        key="search_type_select"
    )
    
    genres = st.multiselect(
        "Filter by Genre",
        options=['Short', 'Drama', 'Crime', 'Comedy', 'Action', 'Romance', 'Western', 'Horror', 'Musical', 'Family'],
        key="genre_filter"
    )
    
    year_range = st.slider(
        "Year Range",
        min_value=1900,
        max_value=2025,
        value=(1900, 2025),
        step=1,
        key="year_range_slider"
    )
    
    if st.button("Clear Filters", key="clear_filters_btn"):
        st.session_state.genres = []
        st.session_state.year_range = (1900, 2025)
        st.rerun()

def search_movies(query, num_results=10, search_type="Semantic Search", genres=[], year_range=None):
    if not query.strip():
        st.warning("Please enter a search query")
        return []
    
    # Handle year search specifically
    try:
        year = int(query)
        if 1900 <= year <= 2025:
            # If it's a valid year, use it as a filter
            if year_range is None:
                year_range = (year, year)
            else:
                year_range = (max(year_range[0], year), min(year_range[1], year))
            query = ""  # Clear the query since we're using it as a year filter
    except ValueError:
        # Not a valid year, proceed with normal search
        pass
    
    # For non-year queries, check if it's meaningful
    if query and (len(query) < 3 or not any(c.isalpha() for c in query)):
        st.warning("Please enter a meaningful search query with at least 3 letters.")
        st.info("Try searching for movie titles, directors, or genres")
        return []
    
    with st.spinner(f"Searching {search_type.lower()}..."):
        if search_type == "Semantic Search":
            try:
                # Create base query
                results = weaviate_client.query.get("Movie", [
                    "title", "year", "genres", "directors", "plot"
                ])
                
                # Add filters
                if genres or year_range:
                    filter_operands = []
                    
                    if genres:
                        filter_operands.append({
                            "path": ["genres"],
                            "operator": "ContainsAny",
                            "valueStringArray": genres
                        })
                    
                    if year_range:
                        filter_operands.append({
                            "operator": "And",
                            "operands": [
                                {
                                    "path": ["year"],
                                    "operator": "GreaterThanEqual",
                                    "valueInt": year_range[0]
                                },
                                {
                                    "path": ["year"],
                                    "operator": "LessThanEqual",
                                    "valueInt": year_range[1]
                                }
                            ]
                        })
                    
                    results = results.with_where({
                        "operator": "And",
                        "operands": filter_operands
                    })
                
                # Generate text embedding
                text_embedding = model.encode(query)
                
                # Add semantic search with a minimum similarity threshold
                results = results.with_near_vector({
                    "vector": text_embedding.tolist(),
                    "certainty": 0.5  # Minimum similarity threshold (0.0 to 1.0)
                }).with_limit(num_results * 2).do()  # Get more results for reranking
                
                movies = results.get("data", {}).get("Get", {}).get("Movie", [])
                
                if not movies:
                    st.warning("No results found. Try searching for:")
                    for example in examples:
                        st.markdown(f"- {example}")
                    return []
                
                # Reranking logic
                reranked_movies = []
                
                # Calculate scores for each movie
                for movie in movies:
                    score = 0.0
                    
                    # Title match score
                    if query.lower() in movie['title'].lower():
                        score += 0.5
                    
                    # Genre match score
                    if genres and any(g.lower() in query.lower() for g in movie['genres']):
                        score += 0.3
                    
                    # Year match score if year is in query
                    if any(str(y) in query for y in range(1900, 2025)):
                        score += 0.2
                    
                    # Director match score
                    if any(d.lower() in query.lower() for d in movie['directors']):
                        score += 0.4
                    
                    reranked_movies.append({
                        'movie': movie,
                        'score': score
                    })
                
                # Sort movies by score
                reranked_movies.sort(key=lambda x: x['score'], reverse=True)
                
                # Take top N results
                top_movies = reranked_movies[:num_results]
                
                # Prepare final results
                final_results = [m['movie'] for m in top_movies]
                
                if final_results:
                    st.success(f"Found {len(final_results)} results")
                else:
                    st.warning("No results found. Try searching for:")
                    for example in examples:
                        st.markdown(f"- {example}")
                
                return final_results
                
            except Exception as e:
                st.error(f"Error performing semantic search: {str(e)}")
                return []
        else:
            try:
                query_filter = {
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"plot": {"$regex": query, "$options": "i"}},
                        {"fullplot": {"$regex": query, "$options": "i"}}
                    ]
                }
                
                if genres:
                    query_filter["genres"] = {"$in": genres}
                
                if year_range:
                    query_filter["year"] = {"$gte": year_range[0], "$lte": year_range[1]}
                
                results = list(collection.find(query_filter).limit(num_results))
                
                if results:
                    st.success(f"Found {len(results)} results")
                else:
                    st.warning("No results found. Try searching for:")
                    for example in examples:
                        st.markdown(f"- {example}")
                
                return results
                
            except Exception as e:
                st.error(f"Error performing exact match search: {str(e)}")
                return []

if st.button("Search", key="search_btn"):
    if query:
        results = search_movies(query, num_results, search_type, genres, year_range)
        
        if results:
            st.write("---")
            for movie in results:
                with st.expander(f"{movie['title']} ({movie['year']})"):
                    st.write(f"**Genres:** {', '.join(movie['genres'])}")
                    st.write(f"**Directors:** {', '.join(movie['directors'])}")
                    st.write(f"**Plot:** {movie['plot']}")
                    if 'fullplot' in movie and movie['fullplot']:
                        st.write(f"**Full Plot:** {movie['fullplot']}")
            st.write("---")
        else:
            st.warning("No results found. Try searching for:")
            for example in examples:
                st.markdown(f"- {example}")
    else:
        st.warning("Please enter a search query.")
        st.write("Number of results: ", num_results)
