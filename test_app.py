import json
import requests

# Example OMI memory data
sample_memory = {
    "id": 12345,
    "created_at": "2024-07-22T23:59:45.910559+00:00",
    "started_at": "2024-07-21T22:34:43.384323+00:00",
    "finished_at": "2024-07-21T22:35:43.384323+00:00",
    "transcript_segments": [
        {
            "text": "Hey Sarah, it was great seeing you at the coffee shop in Brooklyn yesterday. You seemed really happy about your new job at Google.",
            "speaker": "SPEAKER_00",
            "speakerId": 0,
            "is_user": True,
            "start": 10.0,
            "end": 20.0
        },
        {
            "text": "Yeah, I was so excited to catch up with you after all these months. The Brooklyn Heights area has changed so much!",
            "speaker": "SPEAKER_01",
            "speakerId": 1,
            "is_user": False,
            "start": 21.0,
            "end": 30.0
        }
    ],
    "structured": {
        "title": "Catching up with Sarah",
        "overview": "Reconnected with Sarah at a coffee shop in Brooklyn. She was excited about her new job at Google. We discussed how the Brooklyn Heights area has changed over the past few months. Made plans to meet again next week.",
        "emoji": "☕",
        "category": "personal",
        "action_items": [
            {
                "description": "Schedule dinner with Sarah next Tuesday",
                "completed": False
            }
        ],
        "events": []
    }
}

def test_memory_trigger():
    """Test the memory trigger endpoint with sample data."""
    url = "http://localhost:5001/memory-trigger"
    headers = {"Content-Type": "application/json"}
    
    # Send request
    response = requests.post(url, json=sample_memory, headers=headers)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_setup_status():
    """Test the setup status endpoint."""
    url = "http://localhost:5001/setup-status"
    
    # Send request
    response = requests.get(url)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

if __name__ == "__main__":
    print("Testing setup status endpoint...")
    test_setup_status()
    
    print("\nTesting memory trigger endpoint...")
    test_memory_trigger() 