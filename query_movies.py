from weaviate import Client

# Initialize Weaviate client
client = Client("http://localhost:8080")

# 1. Basic search by title
print("\n1. Search for movies with 'wheat' in the title:")
result = client.query.get("Movie", ["title", "plot"]).with_where({
    "path": ["title"],
    "operator": "Like",
    "valueString": "%wheat%"
}).do()
print(result)

# 2. Semantic search using nearText
print("\n2. Find movies similar to 'corn and bread':")
result = client.query.get("Movie", ["title", "plot"]).with_near_text({
    "concepts": ["corn and bread"]
}).do()
print(result)

# 3. Filter by year
print("\n3. Find movies from 1909:")
result = client.query.get("Movie", ["title", "year"]).with_where({
    "path": ["year"],
    "operator": "Equal",
    "valueInt": 1909
}).do()
print(result)

# 4. Filter by genre
print("\n4. Find drama movies:")
result = client.query.get("Movie", ["title", "genres"]).with_where({
    "path": ["genres"],
    "operator": "Equal",
    "valueString": "Drama"
}).do()
print(result)

# 5. Get all movies with their full details
print("\n5. Get all movies:")
result = client.query.get("Movie", ["title", "plot", "fullplot", "genres", "directors", "year"]).do()
print(result)
