import weaviate
from weaviate.auth import AuthClientPassword
import os
import json

# Function to test Weaviate connection
def test_weaviate_connection(host, auth=None, name="Weaviate"):
    try:
        client = weaviate.Client(
            url=host,
            auth_client_secret=auth,
            timeout_config=(5, 30)
        )
        
        if client.is_ready():
            print(f"\n{name} connection successful!")
            
            # Test query
            result = client.query.get('Movie', ['title', 'year', 'genres', 'plot'])\
                .with_limit(5)\
                .do()
            
            print(f"\nSample movies from {name}:")
            movies = result.get("data", {}).get("Get", {}).get("Movie", [])
            for movie in movies:
                print(f"- {movie.get('title', 'No title')} ({movie.get('year', 'Unknown year')})")
            
            # Check schema
            schema = client.schema.get()
            print(f"\nSchema for {name}:")
            print(json.dumps(schema, indent=2))
            
            return True
        else:
            print(f"\n{name} connection failed: Client is not ready")
            return False
            
    except Exception as e:
        print(f"\n{name} connection failed: {str(e)}")
        return False

# Test local Weaviate
print("Testing local Weaviate...")
test_weaviate_connection('http://localhost:8080', name="Local Weaviate")

# Test Weaviate Cloud (if credentials are available)
if os.getenv('WEAVIATE_HOST') and os.getenv('WEAVIATE_USER') and os.getenv('WEAVIATE_PASSWORD'):
    print("\nTesting Weaviate Cloud...")
    auth = AuthClientPassword(
        username=os.getenv('WEAVIATE_USER'),
        password=os.getenv('WEAVIATE_PASSWORD')
    )
    test_weaviate_connection(
        os.getenv('WEAVIATE_HOST'),
        auth=auth,
        name="Weaviate Cloud"
    )
else:
    print("\nSkipping Weaviate Cloud test: Credentials not found")
