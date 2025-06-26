import weaviate

# Initialize Weaviate client
client = weaviate.Client('http://localhost:8080')

# Get sample movies
result = client.query.get('Movie', ['title', 'year', 'genres', 'plot'])
.with_limit(5)
.do()

# Print results
print('Sample movies:', result)
