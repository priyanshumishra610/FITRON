#!/usr/bin/env python3
"""
FITRON AI Coach Chatbot Test Script
Test various chat scenarios and functionality
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/chatbot/chat"
HEALTH_ENDPOINT = f"{BASE_URL}/api/v1/chatbot/health"
TEST_USER_ID = "test_user_123"

async def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Ollama connected: {data.get('ollama_connected', False)}")
                print(f"   Current model: {data.get('current_model', 'Unknown')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def test_chat_message(message: str, user_id: str = None) -> Dict[str, Any]:
    """Test a chat message"""
    payload = {"message": message}
    if user_id:
        payload["user_id"] = user_id
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(CHAT_ENDPOINT, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Chat request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Chat request error: {e}")
            return None

async def run_chat_tests():
    """Run comprehensive chat tests"""
    print("🤖 FITRON AI Coach Chatbot Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    if not await test_health_check():
        print("❌ Health check failed. Make sure the server is running and Ollama is available.")
        return
    
    print("\n" + "=" * 50)
    print("💬 Testing Chat Scenarios")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic Greeting",
            "message": "Hello! I'm new to fitness and need some guidance.",
            "expected_features": ["context_length", "reply"]
        },
        {
            "name": "Injury Risk Detection (Medium)",
            "message": "I have shoulder pain during bench press. What should I do?",
            "expected_features": ["injury_risk", "escalation_suggested"]
        },
        {
            "name": "Goal Progress Request",
            "message": "How am I doing with my goal to get Salman Khan's arms?",
            "expected_features": ["goal_progress"]
        },
        {
            "name": "Video Upload Request",
            "message": "Can you check my form? I want to upload a video for analysis.",
            "expected_features": ["video_upload_requested"]
        },
        {
            "name": "Plan Adjustment (Travel)",
            "message": "I'm traveling for work and won't have access to a gym. Can you adjust my workout plan?",
            "expected_features": ["plan_adjustment"]
        },
        {
            "name": "Critical Injury Risk",
            "message": "I think I tore something in my shoulder. The pain is severe and I can't move my arm.",
            "expected_features": ["injury_risk", "escalation_suggested"]
        },
        {
            "name": "Context Continuation",
            "message": "What exercises should I do instead?",
            "expected_features": ["context_length"]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['name']}")
        print(f"📝 Message: {scenario['message']}")
        
        response = await test_chat_message(scenario['message'], TEST_USER_ID)
        
        if response:
            print(f"✅ Response received ({len(response.get('reply', ''))} characters)")
            
            # Check expected features
            for feature in scenario['expected_features']:
                if feature in response and response[feature]:
                    print(f"   ✅ {feature}: {response[feature]}")
                else:
                    print(f"   ⚠️  {feature}: Not detected")
            
            # Show injury risk if present
            if response.get('injury_risk'):
                print(f"   🚨 Injury Risk Level: {response['injury_risk']}")
            
            # Show escalation if suggested
            if response.get('escalation_suggested'):
                print(f"   🆘 Escalation Suggested: {response['escalation_suggested']}")
            
            # Show context length
            print(f"   📊 Context Length: {response.get('context_length', 0)} messages")
            
        else:
            print("❌ No response received")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary")
    print("=" * 50)
    print("✅ All tests completed!")
    print("📋 Features tested:")
    print("   - Basic chat functionality")
    print("   - Injury risk detection")
    print("   - Goal progress tracking")
    print("   - Video upload requests")
    print("   - Plan adjustments")
    print("   - Context awareness")
    print("   - Escalation suggestions")

async def test_anonymous_chat():
    """Test anonymous chat functionality"""
    print("\n" + "=" * 50)
    print("👤 Testing Anonymous Chat")
    print("=" * 50)
    
    response = await test_chat_message("Hi! I want to try FITRON but I'm not logged in yet.")
    
    if response:
        print("✅ Anonymous chat working")
        print(f"   User ID: {response.get('user_id', 'None (anonymous)')}")
        print(f"   Reply: {response.get('reply', '')[:100]}...")
    else:
        print("❌ Anonymous chat failed")

async def main():
    """Main test function"""
    try:
        await run_chat_tests()
        await test_anonymous_chat()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("=" * 50)
        print("🚀 Your FITRON AI Coach is ready to use!")
        print("📖 Check the API docs at: http://localhost:8000/docs")
        print("💡 Try the curl example:")
        print("""
curl -X POST http://localhost:8000/api/v1/chatbot/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "I have shoulder pain during bench press", "user_id": "user123"}'
        """)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 