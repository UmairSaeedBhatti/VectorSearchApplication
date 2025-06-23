# Movie Semantic Search Application

This application demonstrates semantic search capabilities using Weaviate and MongoDB. It allows users to search for movies using natural language queries and provides relevant results based on semantic similarity.

## Features

- Semantic search using Weaviate
- Filter by number of results
- Choose similarity metrics (cosine, dot)
- Select search algorithms (hybrid, BM25F, vector)
- Genre filtering
- Detailed movie information display

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
