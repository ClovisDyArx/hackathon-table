#!/usr/bin/env python3
"""
Test script for voice functionality
"""
import requests
import json

def test_speak_endpoint():
    """Test the speak endpoint"""
    url = "http://localhost:8000/api/speak"
    
    # Test data
    data = {
        'text': 'Hello, this is a test of the voice synthesis system.',
        'voice': None
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Speak endpoint working!")
        else:
            print("❌ Speak endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error testing speak endpoint: {e}")

def test_voices_endpoint():
    """Test the voices endpoint"""
    url = "http://localhost:8000/api/voices"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Voices endpoint working!")
        else:
            print("❌ Voices endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error testing voices endpoint: {e}")

if __name__ == "__main__":
    print("Testing voice endpoints...")
    print("\n1. Testing /api/voices")
    test_voices_endpoint()
    
    print("\n2. Testing /api/speak")
    test_speak_endpoint()
    
    print("\nTest completed!")
