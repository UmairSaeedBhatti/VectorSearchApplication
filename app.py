import streamlit as st
from weaviate import Client
import config
import json
import streamlit as st
import time

# Initialize Weaviate client with retry logic
def init_weaviate_client():
    weaviate_config = config.get_weaviate_config()
    retry_count = 0
    
    while retry_count < weaviate_config['retry_max']:
        try:
            client = Client(weaviate_config['url'])
            if client.is_ready():
                return client
            else:
                raise Exception("Weaviate connection failed")
        except Exception as e:
            retry_count += 1
            if retry_count >= weaviate_config['retry_max']:
                st.error(f"Failed to connect to Weaviate after {retry_count} attempts")
                return None
            time.sleep(weaviate_config['retry_delay'])
            st.warning(f"Attempt {retry_count}/{weaviate_config['retry_max']}: Retrying Weaviate connection...")

# Initialize client
client = init_weaviate_client()

if client is None:
    st.error("Failed to connect to Weaviate. Please check your configuration and try again.")
    st.stop()

# Initialize Weaviate client
client = Client(config.WEAVIATE_URL)

st.title("Movie Semantic Search")

# Sidebar configuration
with st.sidebar:
    st.header("Search Configuration")
    
    # Number of results
    num_results = st.slider(
        "Number of Results",
        min_value=1,
        max_value=20,
        value=config.DEFAULT_RESULTS,
        step=1
    )
    
    # Similarity metric
    similarity_metric = st.selectbox(
        "Similarity Metric",
        config.SIMILARITY_METRICS
    )
    
    # Search algorithm
    search_algorithm = st.selectbox(
        "Search Algorithm",
        config.SEARCH_ALGORITHMS
    )
    
    # Genre filter
    genres = st.multiselect(
        "Filter by Genre",
        options=['Drama', 'Comedy', 'Action', 'Romance', 'Horror', 'Adventure', 'Western', 'Musical', 'War', 'Film-Noir']
    )

# Main search interface
query = st.text_input("Enter your search query:")

if st.button("Search"):
    if query:
        # Build the query
        search_query = client.query.get(
            config.WEAVIATE_CLASS,
            ["title", "plot", "fullplot", "genres", "year", "directors"]
        )

        # Add filters if genres are selected
        if genres:
            search_query = search_query.with_where({
                "path": ["genres"],
                "operator": "ContainsAny",
                "valueStringArray": genres
            })

        # Add semantic search
        if client is not None:
            search_query = search_query.with_near_text({
                "concepts": [query],
                "certainty": 0.7
            })

        # Execute the query
        result = search_query.do()
        
        # Display results
        if result.get('data', {}).get('Get', {}).get(config.WEAVIATE_CLASS):
            movies = result['data']['Get'][config.WEAVIATE_CLASS]
            
            for movie in movies[:num_results]:
                st.markdown(f"### {movie['title']}")
                st.write(f"**Year:** {movie['year']}")
                st.write(f"**Genres:** {', '.join(movie['genres'])}")
                st.write(f"**Directors:** {', '.join(movie['directors'])}")
                st.write(f"**Plot:** {movie['plot']}")
                st.write(f"**Full Plot:** {movie['fullplot']}")
                st.write("---")
        else:
            st.warning("No results found.")
