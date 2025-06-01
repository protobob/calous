#!/usr/bin/env python3

import ollama
import json

# Test with available model
model_name = 'deepseek-r1:latest'
print(f"Testing with model: {model_name}")

response = ollama.show(model_name)
print(f"Response type: {type(response)}")
print(f"Available attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")

# Check for model_info
if hasattr(response, 'model_info'):
    print(f"\nModel Info (type: {type(response.model_info)}):")
    if isinstance(response.model_info, dict):
        print(json.dumps(response.model_info, indent=2))
    else:
        print(str(response.model_info)[:1000])

# Check parameters
if hasattr(response, 'parameters'):
    print(f"\nParameters (type: {type(response.parameters)}):")
    print(response.parameters)

# Check details
if hasattr(response, 'details'):
    print(f"\nDetails (type: {type(response.details)}):")
    if hasattr(response.details, '__dict__'):
        print(json.dumps(response.details.__dict__, indent=2, default=str))
    else:
        print(response.details)

# Check if there's a way to get context window info
print(f"\nLooking for context window information...")
for attr in dir(response):
    if not attr.startswith('_') and 'ctx' in attr.lower():
        print(f"Found context-related attribute: {attr}")
        
# Try to access the model_info differently
try:
    model_dict = response.dict() if hasattr(response, 'dict') else None
    if model_dict:
        print(f"\nModel dict keys: {list(model_dict.keys())}")
        if 'model_info' in model_dict:
            print(f"Model info from dict: {json.dumps(model_dict['model_info'], indent=2)[:1000]}")
except Exception as e:
    print(f"Error accessing dict: {e}")
