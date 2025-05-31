#!/usr/bin/env python3
"""Test script to check ollama thinking API structure"""

import ollama
import json

def test_thinking_api():
    """Test the thinking API to see the response structure"""
    try:
        print("Testing ollama thinking API...")
        print("=" * 50)
        
        # Test with a simple message
        messages = [{"role": "user", "content": "What is 2+2? Think step by step."}]
        
        print("Testing with think=True...")
        try:
            response = ollama.chat(
                model="deepseek-r1:latest", 
                messages=messages, 
                stream=False,
                think=True
            )
            print("Response structure:")
            print(json.dumps(response, indent=2, default=str))
            
        except Exception as e:
            print(f"Error with think=True: {e}")
            
        print("\n" + "=" * 50)
        print("Testing with think=False...")
        try:
            response = ollama.chat(
                model="deepseek-r1:latest", 
                messages=messages, 
                stream=False,
                think=False
            )
            print("Response structure:")
            print(json.dumps(response, indent=2, default=str))
            
        except Exception as e:
            print(f"Error with think=False: {e}")
            
    except Exception as e:
        print(f"Overall error: {e}")

if __name__ == "__main__":
    test_thinking_api()
