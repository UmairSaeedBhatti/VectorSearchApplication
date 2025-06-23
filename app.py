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

# Add search examples
st.markdown("### Search Examples:")
examples = [
    "corn and bread",
    "wheat",
    "poverty",
    "1909",
    "D.W. Griffith"
]

# Create a function to handle search example clicks
def handle_search_click(query):
    st.session_state.query = query

for example in examples:
    st.button(f"Search: {example}", key=f"search_{example}", on_click=handle_search_click, args=(example,))

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
    st.info("Note: Using text-based search only since vector search requires a vectorizer module")
    search_algorithm = st.selectbox(
        "Search Algorithm",
        ["text"]  # Only show text-based search option
    )
    
    # Genre filter
    genres = st.multiselect(
        "Filter by Genre",
        options=['Short', 'Drama']
    )

# Main search interface
query = st.text_input("Enter your search query:", key="query")

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

        # Use text-based search
        search_query = search_query.with_where({
            "path": ["title", "plot", "fullplot"],
            "operator": "Like",
            "valueString": f"%{query}%"
        })
        
        # Add filters if genres are selected
        if genres:
            search_query = search_query.with_where({
                "path": ["genres"],
                "operator": "ContainsAny",
                "valueStringArray": genres
            })

        try:
            # Execute the query
            result = search_query.do()
            
            # Debug output
            st.write("Query result:")
            st.json(result)
            
            # Display results
            if 'data' in result and 'Get' in result['data'] and config.WEAVIATE_CLASS in result['data']['Get']:
                movies = result['data']['Get'][config.WEAVIATE_CLASS]
                
                if movies:
                    st.write(f"Found {len(movies)} results:")
                    st.write("---")
                    for movie in movies[:num_results]:
                        st.markdown(f"### {movie['title']}")
                        st.write(f"**Year:** {movie['year']}")
                        st.write(f"**Genres:** {', '.join(movie['genres'])}")
                        st.write(f"**Directors:** {', '.join(movie['directors'])}")
                        st.write(f"**Plot:** {movie['plot']}")
                        st.write(f"**Full Plot:** {movie['fullplot']}")
                        st.write("---")
                else:
                    st.warning("No results found. Try searching for:")
                    for example in examples:
                        st.markdown(f"- {example}")
            elif 'errors' in result:
                st.error("Error in query:")
                st.json(result['errors'])
            else:
                st.error("Unexpected query response format")
                st.json(result)
                
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            st.error("Query details:")
            st.write(f"Search query: {query}")
            st.write(f"Genres filter: {genres}")
            st.write(f"Similarity metric: {similarity_metric}")
            st.write(f"Search algorithm: {search_algorithm}")
            st.write(f"Number of results: {num_results}")
