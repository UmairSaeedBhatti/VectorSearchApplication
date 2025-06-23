import json
import requests
from weaviate import Client

# Initialize Weaviate client
client = Client(
    "http://localhost:8080"
)

# Read schema and create class
with open('movies-schema.json', 'r') as f:
    schema = json.load(f)

# Delete existing schema if it exists
if client.schema.exists("Movie"):
    client.schema.delete_class("Movie")

# Create new schema
client.schema.create(schema)

# Read movies JSON file
with open('movies_temp.json', 'r') as f:
    movies = json.load(f)

# Import movies into Weaviate
for movie in movies:
    try:
        client.data_object.create(
            data_object=movie,
            class_name="Movie"
        )
        print(f"Successfully imported movie: {movie['title']}")
    except Exception as e:
        print(f"Error importing movie {movie.get('title', 'unknown')}: {str(e)}")

print("Data import completed!")
