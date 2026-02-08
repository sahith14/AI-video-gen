import requests
import json

def test_backend():
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
        
        # Test health
        response = requests.get("http://localhost:8000/health")
        print(f"Health endpoint: {response.status_code}")
        
        # Test generate endpoint
        data = {
            "script": "Test video",
            "style": ["cinematic"],
            "avatar": "male",
            "voice": "male"
        }
        response = requests.post("http://localhost:8000/api/generate", json=data)
        print(f"Generate endpoint: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure backend is running: python main.py")

if __name__ == "__main__":
    test_backend()
