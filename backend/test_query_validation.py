#!/usr/bin/env python3
"""Test script for natural language query validation"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001/api/query"

def test_query(question, expected_type='success'):
    """Send a query and print the result"""
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"Expected: {expected_type}")
    print('-'*80)
    
    try:
        response = requests.post(BASE_URL, json={'question': question})
        result = response.json()
        
        # Print response
        print(f"Status Code: {response.status_code}")
        print(f"Success: {result.get('success', False)}")
        print(f"\nResponse:")
        print(result.get('response', result.get('error', 'No response')))
        
        if result.get('data'):
            print(f"\nData Count: {len(result['data'])} rows")
            if len(result['data']) > 0:
                print(f"Sample: {json.dumps(result['data'][:2], indent=2)}")
        
        # Validation
        if expected_type == 'success' and result.get('success'):
            print("✅ PASS - Query executed successfully")
        elif expected_type == 'off-topic' and not result.get('success'):
            print("✅ PASS - Off-topic detected correctly")
        elif expected_type == 'greeting' and result.get('success') and not result.get('data'):
            print("✅ PASS - Greeting handled correctly")
        else:
            print("❌ FAIL - Unexpected result")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def main():
    print("\n🧪 TESTING NATURAL LANGUAGE QUERY VALIDATION")
    print("="*80)
    print("Make sure backend is running on http://localhost:5001")
    
    # Test 1: Greetings
    print("\n\n📋 TEST CATEGORY: GREETINGS")
    test_query("hi", expected_type='greeting')
    test_query("hello", expected_type='greeting')
    test_query("hey there", expected_type='greeting')
    test_query("good morning", expected_type='greeting')
    
    # Test 2: Off-topic questions
    print("\n\n📋 TEST CATEGORY: OFF-TOPIC QUESTIONS")
    test_query("what's the weather today?", expected_type='off-topic')
    test_query("tell me a joke", expected_type='off-topic')
    test_query("what is the capital of France?", expected_type='off-topic')
    test_query("how to cook pasta?", expected_type='off-topic')
    test_query("recommend a good movie", expected_type='off-topic')
    test_query("write a python script for me", expected_type='off-topic')
    
    # Test 3: Valid task-related questions
    print("\n\n📋 TEST CATEGORY: VALID TASK QUERIES")
    test_query("show me all blocked tasks", expected_type='success')
    test_query("how many tasks are completed?", expected_type='success')
    test_query("who has the most tasks?", expected_type='success')
    test_query("list all high priority tasks", expected_type='success')
    test_query("what tasks are assigned to Alice?", expected_type='success')
    
    # Test 4: Edge cases (should work with task context)
    print("\n\n📋 TEST CATEGORY: EDGE CASES")
    test_query("what is the status of blocked tasks?", expected_type='success')
    test_query("who is working on the Web Platform project?", expected_type='success')
    
    print("\n\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

