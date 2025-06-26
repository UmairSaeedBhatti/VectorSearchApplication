from pymongo import MongoClient
import json

# Initialize MongoDB client
try:
    # Connect to MongoDB Atlas
    atlas_client = MongoClient("mongodb+srv://umairsaeed368:XRY1KbbQBy1H62m6@cluster0.ql5xox0.mongodb.net/")
    
    # Get the sample_mflix database and movies collection
    source_db = atlas_client['sample_mflix']
    source_collection = source_db['movies']
    
    # Get the number of movies in the source
    total_movies = source_collection.count_documents({})
    print(f"Found {total_movies} movies in sample_mflix")
    
    # Create our target database and collection
    target_client = MongoClient('mongodb://localhost:27017')
    target_db = target_client['movies_db']
    target_collection = target_db['movies']
    
    # Drop existing collection if it exists
    if "movies" in target_db.list_collection_names():
        target_collection.drop()
        print("Dropped existing movies collection")
    
    # Copy movies from sample_mflix to our movies_db
    print("Copying movies data...")
    
    # Get all movies (limited to 100 for testing)
    movies = list(source_collection.find({}, {
        "_id": 0,
        "title": 1,
        "year": 1,
        "genres": 1,
        "directors": 1,
        "plot": 1,
        "fullplot": 1
    }).limit(100))
    
    # Insert into target collection
    target_collection.insert_many(movies)
    print(f"Copied {len(movies)} movies to movies_db")
    
    # Print statistics
    print("\nDatabase statistics:")
    print(f"Movies in sample_mflix: {total_movies}")
    print(f"Movies in movies_db: {target_collection.count_documents({})}")
    
    # Show sample movies
    print("\nSample movies:")
    for movie in movies[:3]:
        print(f"- {movie['title']} ({movie['year']}) - {', '.join(movie['genres'])}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)
finally:
    if 'atlas_client' in locals():
        atlas_client.close()
    if 'target_client' in locals():
        target_client.close()
