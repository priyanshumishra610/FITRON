#!/usr/bin/env python3
"""
FITRON AI Coach Chatbot Demo
Interactive demo showcasing the chatbot capabilities
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any

# Demo configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/chatbot/chat"
HEALTH_ENDPOINT = f"{BASE_URL}/api/v1/chatbot/health"

class ChatbotDemo:
    """Interactive demo for FITRON AI Coach"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.user_id = "demo_user_123"
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def check_health(self) -> bool:
        """Check if the chatbot is healthy"""
        try:
            response = await self.client.get(HEALTH_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health: {data['status']}")
                print(f"🤖 Model: {data.get('current_model', 'Unknown')}")
                print(f"🔗 Ollama: {'Connected' if data.get('ollama_connected') else 'Disconnected'}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def send_message(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Send a message to the chatbot"""
        payload = {"message": message}
        if user_id:
            payload["user_id"] = user_id
        
        try:
            response = await self.client.post(CHAT_ENDPOINT, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Chat request error: {e}")
            return None
    
    def print_response(self, response: Dict[str, Any]):
        """Pretty print the chatbot response"""
        print("\n" + "="*60)
        print("🤖 FITRON AI Coach Response:")
        print("="*60)
        print(f"💬 Reply: {response.get('reply', 'No reply')}")
        print(f"👤 User ID: {response.get('user_id', 'Anonymous')}")
        print(f"📊 Context: {response.get('context_length', 0)} messages")
        
        # Show special features
        if response.get('injury_risk'):
            print(f"🚨 Injury Risk: {response['injury_risk']}")
        
        if response.get('escalation_suggested'):
            print(f"🆘 Escalation: Suggested to real trainer")
        
        if response.get('video_upload_requested'):
            print(f"📹 Video Upload: Requested for form analysis")
        
        if response.get('plan_adjustment'):
            print(f"🔄 Plan Adjustment: {response['plan_adjustment']}")
        
        if response.get('goal_progress'):
            progress = response['goal_progress']
            print(f"🎯 Goal Progress: {progress.get('goal_name', 'Unknown')}")
            print(f"📈 Progress: {progress.get('current_progress', 0)}%")
        
        print("="*60)
    
    async def run_demo_scenarios(self):
        """Run predefined demo scenarios"""
        scenarios = [
            {
                "title": "🎯 Welcome & Introduction",
                "message": "Hi! I'm new to fitness and want to get started with FITRON. Can you help me?",
                "description": "Basic greeting and introduction"
            },
            {
                "title": "🚨 Injury Risk Detection (Medium)",
                "message": "I have shoulder pain during bench press. What should I do?",
                "description": "Detects injury keywords and suggests modifications"
            },
            {
                "title": "🎯 Goal Progress Tracking",
                "message": "How am I doing with my goal to get Salman Khan's arms?",
                "description": "Shows goal progress with detailed metrics"
            },
            {
                "title": "📹 Video Upload Request",
                "message": "Can you check my squat form? I want to upload a video for analysis.",
                "description": "Triggers video upload flow"
            },
            {
                "title": "🔄 Plan Adjustment (Travel)",
                "message": "I'm traveling for work and won't have access to a gym. Can you adjust my workout plan?",
                "description": "Adapts workout plan for travel"
            },
            {
                "title": "🚨 Critical Injury Risk",
                "message": "I think I tore something in my shoulder. The pain is severe and I can't move my arm.",
                "description": "High-risk injury detection with escalation"
            },
            {
                "title": "🧠 Context Awareness",
                "message": "What exercises should I do instead?",
                "description": "Remembers previous conversation about injury"
            },
            {
                "title": "👤 Anonymous User",
                "message": "Hi! I want to try FITRON but I'm not logged in yet.",
                "description": "Works without user authentication"
            }
        ]
        
        print("\n🎬 FITRON AI Coach Demo Scenarios")
        print("="*60)
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. {scenario['title']}")
            print(f"   📝 {scenario['description']}")
            print(f"   💬 Message: {scenario['message']}")
            
            # Send message
            response = await self.send_message(scenario['message'], self.user_id)
            
            if response:
                self.print_response(response)
            else:
                print("❌ No response received")
            
            # Wait for user input to continue
            if i < len(scenarios):
                input("\n⏸️  Press Enter to continue to next scenario...")
    
    async def interactive_mode(self):
        """Interactive chat mode"""
        print("\n💬 Interactive Chat Mode")
        print("="*60)
        print("Type your messages to chat with FITRON AI Coach!")
        print("Type 'quit' to exit, 'help' for examples")
        print("="*60)
        
        while True:
            try:
                message = input("\n💬 You: ").strip()
                
                if message.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thanks for trying FITRON AI Coach!")
                    break
                
                if message.lower() == 'help':
                    print("\n💡 Example messages:")
                    print("  - 'I have shoulder pain during bench press'")
                    print("  - 'How am I doing with my Salman Khan arms goal?'")
                    print("  - 'I'm traveling and need a workout plan'")
                    print("  - 'Can you check my squat form?'")
                    print("  - 'I think I tore something in my shoulder'")
                    continue
                
                if not message:
                    continue
                
                # Send message
                response = await self.send_message(message, self.user_id)
                
                if response:
                    self.print_response(response)
                else:
                    print("❌ No response received")
                    
            except KeyboardInterrupt:
                print("\n👋 Thanks for trying FITRON AI Coach!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main demo function"""
    print("🏋️‍♂️ FITRON AI Coach Chatbot Demo")
    print("="*60)
    
    async with ChatbotDemo() as demo:
        # Check health first
        print("🏥 Checking chatbot health...")
        if not await demo.check_health():
            print("❌ Chatbot is not healthy. Please make sure:")
            print("   1. Server is running: uvicorn app.main:app --reload")
            print("   2. Ollama is running: ollama serve")
            print("   3. MongoDB is running (optional)")
            return
        
        print("\n✅ Chatbot is ready!")
        
        # Ask user for demo mode
        print("\n🎬 Choose demo mode:")
        print("1. Run predefined scenarios")
        print("2. Interactive chat mode")
        print("3. Both")
        
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                await demo.run_demo_scenarios()
            elif choice == "2":
                await demo.interactive_mode()
            elif choice == "3":
                await demo.run_demo_scenarios()
                await demo.interactive_mode()
            else:
                print("Invalid choice. Running predefined scenarios...")
                await demo.run_demo_scenarios()
                
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted. Thanks for trying FITRON!")
        except Exception as e:
            print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Thanks for trying FITRON!")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        sys.exit(1) 