#!/usr/bin/env python3
"""
Simple FITRON AI Coach Chatbot Demo
Standalone demo that works without the full backend
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class InjuryRiskLevel(str, Enum):
    """Injury risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SimpleChatbotDemo:
    """Simple chatbot demo with Ollama integration"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "gemma:2b"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Injury keywords for risk detection
        self.injury_keywords = {
            "critical": ["tear", "rupture", "broken", "fracture", "dislocation", "severe pain", "can't move"],
            "high": ["sharp pain", "stabbing", "burning", "numbness", "tingling", "swelling", "bruising"],
            "medium": ["pain", "hurt", "sore", "ache", "stiff", "tight", "uncomfortable", "discomfort"],
            "low": ["tired", "fatigue", "weak", "slight", "minor", "mild"]
        }
        
        # System prompt for FITRON AI Coach
        self.system_prompt = """You are FITRON, an AI-powered fitness coach and personal trainer. You are:

1. **Expert Fitness Coach**: Provide safe, effective workout advice and form guidance
2. **Injury Prevention Specialist**: Identify potential injury risks and suggest modifications
3. **Motivational Trainer**: Keep users motivated and on track with their fitness goals
4. **Adaptive Planner**: Adjust workouts for travel, injuries, equipment limitations, etc.
5. **Goal-Oriented**: Help users track progress toward their dream physique goals

**Key Guidelines:**
- Always prioritize safety and proper form
- If injury keywords are detected (pain, hurt, tear, etc.), flag as risky and suggest escalation
- Be encouraging but realistic about progress
- Provide specific, actionable advice
- Ask clarifying questions when needed
- Suggest video uploads for form analysis when appropriate

**Response Style:**
- Friendly, professional, and motivating
- Use emojis sparingly but effectively
- Keep responses concise but comprehensive
- Always end with a clear next step or question

Remember: You're not just an AI - you're their personal trainer, coach, and fitness partner!"""

    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def check_ollama_health(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = await self.client.get(f"{self.ollama_url}/api/tags")
            if response.status_code != 200:
                return False
            
            # Check if our model is available
            models = response.json().get("models", [])
            model_available = any(model.get("name") == self.model_name for model in models)
            
            if not model_available:
                print(f"⚠️  Model {self.model_name} not found. Available models:")
                for model in models:
                    print(f"   - {model.get('name', 'Unknown')}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Ollama health check failed: {e}")
            return False
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for special triggers"""
        message_lower = message.lower()
        analysis = {
            "injury_risk": None,
            "escalation_suggested": False,
            "video_upload_requested": False,
            "plan_adjustment": None,
            "goal_progress": None
        }
        
        # Check for injury keywords
        for risk_level, keywords in self.injury_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis["injury_risk"] = InjuryRiskLevel(risk_level)
                if risk_level in ["critical", "high"]:
                    analysis["escalation_suggested"] = True
                break
        
        # Check for video upload requests
        video_triggers = ["upload video", "send video", "record", "form check", "check form", "video analysis"]
        if any(trigger in message_lower for trigger in video_triggers):
            analysis["video_upload_requested"] = True
        
        # Check for goal progress requests
        goal_triggers = ["progress", "goal", "closer to", "how am i doing", "salman khan", "celebrity", "physique"]
        if any(trigger in message_lower for trigger in goal_triggers):
            analysis["goal_progress"] = {
                "goal_name": "Salman Khan Arms",
                "current_progress": 65.5,
                "target_date": "2024-06-01",
                "metrics": {
                    "arm_circumference": {"current": 15.2, "target": 16.5, "unit": "inches"},
                    "bench_press": {"current": 185, "target": 225, "unit": "lbs"},
                    "workout_consistency": {"current": 85, "target": 90, "unit": "%"}
                },
                "next_milestone": "Reach 16-inch arm circumference",
                "estimated_completion": "3 months"
            }
        
        # Check for plan adjustment requests
        plan_triggers = {
            "travel": ["travel", "trip", "vacation", "hotel", "away"],
            "injury": ["injury", "hurt", "pain", "recovery", "rest"],
            "no_gym": ["no gym", "home workout", "no equipment"],
            "time_constraint": ["busy", "short time", "quick workout"]
        }
        
        for adjustment_type, triggers in plan_triggers.items():
            if any(trigger in message_lower for trigger in triggers):
                analysis["plan_adjustment"] = adjustment_type
                break
        
        return analysis
    
    async def generate_response(self, message: str, context_messages: List[Dict[str, str]] = None) -> str:
        """Generate response using Ollama"""
        try:
            # Build conversation context
            messages = []
            
            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add context messages if provided
            if context_messages:
                messages.extend(context_messages)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500,
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            # Make request to Ollama
            response = await self.client.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "I apologize, but I couldn't generate a response.")
            else:
                print(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return "I'm having trouble connecting to my training systems. Please try again in a moment."
                
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I encountered an unexpected error. Please try again."
    
    def print_response(self, message: str, response: str, analysis: Dict[str, Any]):
        """Pretty print the chatbot response"""
        print("\n" + "="*60)
        print("🤖 FITRON AI Coach Response:")
        print("="*60)
        print(f"💬 Reply: {response}")
        
        # Show special features
        if analysis.get('injury_risk'):
            print(f"🚨 Injury Risk: {analysis['injury_risk']}")
        
        if analysis.get('escalation_suggested'):
            print(f"🆘 Escalation: Suggested to real trainer")
        
        if analysis.get('video_upload_requested'):
            print(f"📹 Video Upload: Requested for form analysis")
        
        if analysis.get('plan_adjustment'):
            print(f"🔄 Plan Adjustment: {analysis['plan_adjustment']}")
        
        if analysis.get('goal_progress'):
            progress = analysis['goal_progress']
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
            }
        ]
        
        print("\n🎬 FITRON AI Coach Demo Scenarios")
        print("="*60)
        
        context_messages = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. {scenario['title']}")
            print(f"   📝 {scenario['description']}")
            print(f"   💬 Message: {scenario['message']}")
            
            # Analyze message
            analysis = self.analyze_message(scenario['message'])
            
            # Generate response
            response = await self.generate_response(scenario['message'], context_messages)
            
            # Print response
            self.print_response(scenario['message'], response, analysis)
            
            # Add to context for next iteration
            context_messages.append({"role": "user", "content": scenario['message']})
            context_messages.append({"role": "assistant", "content": response})
            
            # Keep only last 4 messages for context
            if len(context_messages) > 8:
                context_messages = context_messages[-8:]
            
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
        
        context_messages = []
        
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
                
                # Analyze message
                analysis = self.analyze_message(message)
                
                # Generate response
                response = await self.generate_response(message, context_messages)
                
                # Print response
                self.print_response(message, response, analysis)
                
                # Add to context
                context_messages.append({"role": "user", "content": message})
                context_messages.append({"role": "assistant", "content": response})
                
                # Keep only last 4 messages for context
                if len(context_messages) > 8:
                    context_messages = context_messages[-8:]
                    
            except KeyboardInterrupt:
                print("\n👋 Thanks for trying FITRON AI Coach!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main demo function"""
    print("🏋️‍♂️ FITRON AI Coach Chatbot Demo")
    print("="*60)
    
    async with SimpleChatbotDemo() as demo:
        # Check Ollama health first
        print("🏥 Checking Ollama health...")
        if not await demo.check_ollama_health():
            print("❌ Ollama is not healthy. Please make sure:")
            print("   1. Ollama is running: ollama serve")
            print("   2. Model is available: ollama pull gemma:2b")
            return
        
        print("\n✅ Ollama is ready!")
        print(f"🤖 Using model: {demo.model_name}")
        
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