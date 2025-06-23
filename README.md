# Movie Semantic Search Application

This application demonstrates semantic search capabilities using Weaviate and MongoDB. It allows users to search for movies using natural language queries and provides relevant results based on semantic similarity.

## Features

- Semantic search using Weaviate
- Filter by number of results
- Choose similarity metrics (cosine, dot)
- Select search algorithms (hybrid, BM25F, vector)
- Genre filtering
- Detailed movie information display
- Retry mechanism for Weaviate connection
- Error handling and user feedback

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your MongoDB and Weaviate configuration

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Deployment

1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit Cloud
4. Deploy with one-click deployment

## Requirements

- Python 3.8+
- MongoDB
- Weaviate
- Streamlit Cloud account

## Project Structure

- `app.py`: Main Streamlit application
- `config.py`: Configuration management
- `requirements.txt`: Python dependencies
- `.streamlit/secrets.toml`: Streamlit secrets configuration
- `README.md`: Project documentation
- `movies-schema.json`: Weaviate schema definition
- `movies.json`: Sample movie data
- `import_movies.py`: Script to import data into Weaviate
- `query_movies.py`: Example queries for testing
- `weaviate-config.yaml`: Weaviate configuration
- `.gitignore`: Git ignore file

## Configuration

The application uses environment variables for configuration. Create a `.env` file with the following variables:

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=sample_mflix
MONGODB_COLLECTION=movies
WEAVIATE_URL=http://localhost:8080
```
