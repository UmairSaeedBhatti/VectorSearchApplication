import json
from pymongo import MongoClient
from weaviate import Client
from sentence_transformers import SentenceTransformer
import time

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def setup_weaviate_schema(client):
    """Set up Weaviate schema"""
    # Delete existing Movie class if it exists
    if client.schema.exists("Movie"):
        print("Deleting existing Movie class...")
        client.schema.delete_class("Movie")

    schema = {
        "classes": [{
            "class": "Movie",
            "description": "A movie",
            "vectorizer": "none",
            "properties": [
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "The title of the movie"
                },
                {
                    "name": "year",
                    "dataType": ["int"],
                    "description": "The year the movie was released"
                },
                {
                    "name": "genres",
                    "dataType": ["string[]"],
                    "description": "The genres of the movie"
                },
                {
                    "name": "directors",
                    "dataType": ["string[]"],
                    "description": "The directors of the movie"
                },
                {
                    "name": "plot",
                    "dataType": ["string"],
                    "description": "The plot summary of the movie"
                },
                {
                    "name": "fullplot",
                    "dataType": ["string"],
                    "description": "The full plot summary of the movie"
                }
            ]
        }]
    }
    
    client.schema.create(schema)
    print("Weaviate schema created successfully!")

def get_movie_embedding(movie):
    """Create embeddings for movie data"""
    # Combine text fields for embedding
    text = f"{movie.get('title', '')} {movie.get('plot', '')} {movie.get('fullplot', '')}"
    
    # Generate embedding using sentence transformer
    embedding = model.encode(text)
    return embedding.tolist()

def stream_data_from_mongodb_to_weaviate(mongo_client, weaviate_client):
    """Stream data from MongoDB to Weaviate"""
    # Connect to MongoDB
    db = mongo_client['movies_db']
    collection = db['movies']
    
    # Initialize batch
    weaviate_client.batch.configure(
        batch_size=100,  # Batch size
        timeout_retries=3,  # Number of retries
        num_workers=2  # Number of worker threads
    )
    
    # Stream data from MongoDB
    total_movies = collection.count_documents({})
    processed_count = 0
    
    print(f"Starting to stream {total_movies} movies to Weaviate...")
    
    for movie in collection.find({}):
        try:
            # Prepare data for Weaviate
            weaviate_data = {
                "title": movie.get('title', ''),
                "year": movie.get('year', 0),
                "genres": movie.get('genres', []),
                "directors": movie.get('directors', []),
                "plot": movie.get('plot', ''),
                "fullplot": movie.get('fullplot', '')
            }
            
            # Generate embedding
            embedding = get_movie_embedding(movie)
            
            # Add to Weaviate batch
            weaviate_client.batch.add_data_object(
                weaviate_data,
                "Movie",
                vector=embedding
            )
            
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"Processed {processed_count}/{total_movies} movies")
                
        except Exception as e:
            print(f"Error processing movie {movie.get('title', 'unknown')}: {str(e)}")
            continue
    
    # Finalize batch
    weaviate_client.batch.flush()
    print(f"Streaming completed. Processed {processed_count} movies")

if __name__ == "__main__":
    import time
    
    # Wait for Weaviate to start up
    print("Waiting for Weaviate to start up...")
    time.sleep(30)  # Wait 30 seconds for Weaviate to start
    
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb://localhost:27017')
    
    # Connect to Weaviate
    weaviate_client = Client("http://localhost:8080", timeout_config=(10, 60))
    
    # Set up Weaviate schema
    setup_weaviate_schema(weaviate_client)
    
    # Stream data
    stream_data_from_mongodb_to_weaviate(mongo_client, weaviate_client)
    print("Data migration complete!")
