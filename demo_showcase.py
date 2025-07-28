#!/usr/bin/env python3
"""
FITRON AI Fitness OS - Demo Showcase
This script demonstrates the key features of the FITRON system
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Demo configuration
BASE_URL = "http://localhost:8000"
DEMO_EMAIL = "demo@fitron.ai"
DEMO_PASSWORD = "demo123"

class FITRONDemo:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f"🏋️‍♂️ {title}")
        print("="*60)
        
    def print_section(self, title):
        """Print a section header"""
        print(f"\n📋 {title}")
        print("-" * 40)
        
    def demo_health_check(self):
        """Demo health check"""
        self.print_header("FITRON AI FITNESS OS - DEMO SHOWCASE")
        
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Backend is healthy and running!")
                print(f"   Service: {data['service']}")
                print(f"   Users: {data['users_count']}")
                print(f"   Rep Logs: {data['rep_logs_count']}")
                print(f"   Goals: {data['goals_count']}")
                return True
            else:
                print("❌ Backend is not responding")
                return False
        except Exception as e:
            print(f"❌ Error connecting to backend: {e}")
            return False
    
    def demo_authentication(self):
        """Demo authentication system"""
        self.print_section("Authentication System")
        
        # Login
        login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                print("✅ Login successful!")
                print(f"   User: {data['user']['name']}")
                print(f"   Email: {data['user']['email']}")
                print(f"   Subscription: {data['user']['subscription_tier']}")
                
                # Get profile
                response = self.session.get(f"{BASE_URL}/api/v1/auth/profile")
                if response.status_code == 200:
                    profile = response.json()
                    print(f"   Created: {profile['created_at']}")
                return True
            else:
                print("❌ Login failed")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def demo_rep_tracking(self):
        """Demo rep tracking system"""
        self.print_section("Rep Tracking System")
        
        try:
            # Get rep logs
            response = self.session.get(f"{BASE_URL}/api/v1/rep-tracking/logs")
            if response.status_code == 200:
                rep_logs = response.json()
                print(f"✅ Retrieved {len(rep_logs)} rep logs")
                
                # Show recent reps
                recent_reps = rep_logs[:5]
                for i, rep in enumerate(recent_reps, 1):
                    print(f"   {i}. {rep['exercise_name']} - {rep['weight']}lbs x {rep['reps']} reps")
                    print(f"      Form Score: {rep['form_score']:.2f}")
                    if rep['form_feedback']:
                        print(f"      Feedback: {rep['form_feedback']}")
                
                # Demo pose analysis
                print("\n🤖 AI Pose Analysis:")
                response = self.session.post(f"{BASE_URL}/api/v1/rep-tracking/analyze-pose")
                if response.status_code == 200:
                    analysis = response.json()
                    print(f"   Form Score: {analysis['form_score']:.2f}")
                    print(f"   Feedback: {analysis['feedback']}")
                    print(f"   Ego Lifting: {'Yes' if analysis['is_ego_lifting'] else 'No'}")
                    print(f"   Knee Angle: {analysis['pose_data']['knee_angle']}°")
                
                return True
            else:
                print("❌ Failed to get rep logs")
                return False
        except Exception as e:
            print(f"❌ Rep tracking error: {e}")
            return False
    
    def demo_auto_regulation(self):
        """Demo auto-regulation system"""
        self.print_section("Auto-Regulation System")
        
        try:
            # Get auto-regulation status
            response = self.session.get(f"{BASE_URL}/api/v1/auto-regulation/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Auto-regulation status retrieved")
                print(f"   Locked: {'Yes' if status['is_locked'] else 'No'}")
                print(f"   Risk Score: {status['risk_score']:.2f}")
                print(f"   Recommendations:")
                for rec in status['recommendations']:
                    print(f"     • {rec}")
                
                # Demo override
                print("\n🔓 Override Demo:")
                override_data = {"reason": "Experienced lifter, aware of risks"}
                response = self.session.post(f"{BASE_URL}/api/v1/auto-regulation/override", json=override_data)
                if response.status_code == 200:
                    override = response.json()
                    print(f"   Override: {'Granted' if override['override_granted'] else 'Denied'}")
                    print(f"   Reason: {override['reason']}")
                    print(f"   Warning: {override['warning']}")
                
                return True
            else:
                print("❌ Failed to get auto-regulation status")
                return False
        except Exception as e:
            print(f"❌ Auto-regulation error: {e}")
            return False
    
    def demo_physique_goals(self):
        """Demo physique goals system"""
        self.print_section("Physique Goals System")
        
        try:
            # Get physique goals
            response = self.session.get(f"{BASE_URL}/api/v1/physique-goals/list")
            if response.status_code == 200:
                goals = response.json()
                print(f"✅ Retrieved {len(goals)} physique goals")
                
                for goal in goals:
                    print(f"\n   🎯 {goal['goal_name']}")
                    print(f"      Description: {goal['description']}")
                    print(f"      Celebrity: {goal['celebrity_reference']}")
                    print(f"      Progress: {goal['progress']:.1%}")
                    print(f"      Status: {goal['status']}")
                
                # Demo celebrity analysis
                print("\n🌟 Celebrity Physique Analysis:")
                celebrities = ["arnold schwarzenegger", "bruce lee", "chris hemsworth"]
                
                for celeb in celebrities:
                    analysis_data = {"celebrity_name": celeb}
                    response = self.session.post(f"{BASE_URL}/api/v1/physique-goals/analyze-celebrity", json=analysis_data)
                    if response.status_code == 200:
                        analysis = response.json()
                        print(f"\n   {analysis['name']}:")
                        print(f"      Physique Type: {analysis['physique_type']}")
                        print(f"      Muscle Groups: {', '.join(analysis['muscle_groups'])}")
                        print(f"      Body Fat: {analysis['body_fat_percentage']}%")
                        print(f"      Difficulty: {analysis['difficulty']}")
                        print(f"      Time to Achieve: {analysis['time_to_achieve']}")
                        print(f"      Similarity Score: {analysis['similarity_score']:.2f}")
                
                return True
            else:
                print("❌ Failed to get physique goals")
                return False
        except Exception as e:
            print(f"❌ Physique goals error: {e}")
            return False
    
    def demo_analytics(self):
        """Demo analytics system"""
        self.print_section("Analytics & Insights")
        
        try:
            # Get workout stats
            response = self.session.get(f"{BASE_URL}/api/v1/analytics/workout-stats")
            if response.status_code == 200:
                stats = response.json()
                print("✅ Workout Statistics:")
                print(f"   Total Workouts: {stats['total_workouts']}")
                print(f"   Total Reps: {stats['total_reps']}")
                print(f"   Total Weight Lifted: {stats['total_weight_lifted']:,} lbs")
                print(f"   Average Form Score: {stats['average_form_score']:.2f}")
                
                print("\n   💪 Strength Progress:")
                for exercise, progress in stats['strength_progress'].items():
                    print(f"      {exercise.title()}: {progress}")
                
                print("\n   📈 Weekly Progress:")
                for week in stats['weekly_progress']:
                    print(f"      Week {week['week']}: {week['reps']} reps, {week['form_score']:.2f} form")
            
            # Get form analysis
            response = self.session.get(f"{BASE_URL}/api/v1/analytics/form-analysis")
            if response.status_code == 200:
                analysis = response.json()
                print(f"\n✅ Form Analysis:")
                print(f"   Overall Form Score: {analysis['overall_form_score']:.2f}")
                
                print("\n   📊 Exercise Breakdown:")
                for exercise, data in analysis['exercise_breakdown'].items():
                    print(f"      {exercise.title()}: {data['score']:.2f}")
                    if data['common_issues']:
                        print(f"        Issues: {', '.join(data['common_issues'])}")
                
                print("\n   🎯 Improvement Areas:")
                for area in analysis['improvement_areas']:
                    print(f"      • {area}")
                
                print("\n   💪 Strengths:")
                for strength in analysis['strengths']:
                    print(f"      • {strength}")
                
                return True
            else:
                print("❌ Failed to get analytics")
                return False
        except Exception as e:
            print(f"❌ Analytics error: {e}")
            return False
    
    def demo_mobile_features(self):
        """Demo mobile app features"""
        self.print_section("Mobile App Features")
        
        print("📱 Mobile App Capabilities:")
        print("   • Real-time pose detection with MediaPipe")
        print("   • AI-powered form analysis and scoring")
        print("   • Rep counting and velocity tracking")
        print("   • Ego-lifting detection and warnings")
        print("   • Celebrity physique goal mapping")
        print("   • Auto-regulation system")
        print("   • Progress tracking and analytics")
        print("   • AI coach with personalized feedback")
        
        print("\n🎨 UI/UX Features:")
        print("   • Beautiful gradient design system")
        print("   • Interactive workout cards")
        print("   • Real-time form score visualization")
        print("   • Expandable AI coach chat interface")
        print("   • Progress charts and statistics")
        print("   • Smooth animations and transitions")
        
        return True
    
    def demo_trainer_dashboard(self):
        """Demo trainer dashboard features"""
        self.print_section("Trainer Dashboard")
        
        print("👨‍💼 Trainer Dashboard Features:")
        print("   • Real-time client monitoring")
        print("   • Form analysis and review tools")
        print("   • Progress tracking and analytics")
        print("   • Auto-regulation override system")
        print("   • Client communication tools")
        print("   • Workout plan management")
        print("   • Performance insights and reports")
        
        print("\n📊 Dashboard Analytics:")
        print("   • Client form score trends")
        print("   • Workout completion rates")
        print("   • Strength progression tracking")
        print("   • Risk assessment and alerts")
        print("   • Goal achievement monitoring")
        
        return True
    
    def run_full_demo(self):
        """Run the complete demo"""
        print("🚀 Starting FITRON AI Fitness OS Demo...")
        
        # Check if backend is running
        if not self.demo_health_check():
            return
        
        # Run all demo sections
        demos = [
            self.demo_authentication,
            self.demo_rep_tracking,
            self.demo_auto_regulation,
            self.demo_physique_goals,
            self.demo_analytics,
            self.demo_mobile_features,
            self.demo_trainer_dashboard
        ]
        
        results = []
        for demo in demos:
            try:
                result = demo()
                results.append(result)
                time.sleep(1)  # Brief pause between demos
            except Exception as e:
                print(f"❌ Demo error: {e}")
                results.append(False)
        
        # Summary
        self.print_header("DEMO SUMMARY")
        successful_demos = sum(results)
        total_demos = len(results)
        
        print(f"✅ Successful demos: {successful_demos}/{total_demos}")
        print(f"📊 Success rate: {(successful_demos/total_demos)*100:.1f}%")
        
        if successful_demos == total_demos:
            print("\n🎉 All demos completed successfully!")
            print("🏋️‍♂️ FITRON AI Fitness OS is ready to revolutionize your fitness journey!")
        else:
            print(f"\n⚠️  {total_demos - successful_demos} demo(s) failed")
            print("Please check the backend server and try again.")

if __name__ == "__main__":
    demo = FITRONDemo()
    demo.run_full_demo() 