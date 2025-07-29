# 🚀 FITRON AI Coach Chatbot - Manual Setup Guide

## 📋 **Prerequisites**

### **1. Install Ollama**
```bash
# macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Ubuntu/Debian
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### **2. Install Python Dependencies**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install fastapi uvicorn httpx pymongo motor email-validator PyJWT "python-jose[cryptography]" "passlib[bcrypt]"
```

## 🏃‍♂️ **Quick Start (3 Steps)**

### **Step 1: Start Ollama**
```bash
# Start Ollama service
ollama serve &

# Wait a few seconds for it to start
sleep 3

# Check if it's running
ollama list
```

### **Step 2: Download Model (if needed)**
```bash
# Download a model (choose one)
ollama pull gemma:2b      # Fast, good for fitness (1.7GB)
ollama pull mistral:7b    # More creative responses (4.1GB)
ollama pull llama2:7b     # Balanced performance (3.8GB)
```

### **Step 3: Run the Chatbot**
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Run the demo
python simple_chatbot_demo.py
```

## 🎯 **Different Ways to Run**

### **Option 1: Interactive Demo (Recommended)**
```bash
cd backend
source venv/bin/activate
python simple_chatbot_demo.py
```
**Choose option 2 for interactive chat mode**

### **Option 2: Predefined Scenarios**
```bash
cd backend
source venv/bin/activate
python simple_chatbot_demo.py
```
**Choose option 1 to see all features demonstrated**

### **Option 3: Direct Ollama API Test**
```bash
# Test basic functionality
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma:2b",
    "messages": [
      {"role": "system", "content": "You are FITRON, an AI fitness coach. Be helpful and motivating."},
      {"role": "user", "content": "I have shoulder pain during bench press. What should I do?"}
    ],
    "stream": false
  }'
```

### **Option 4: Full FastAPI Backend (Advanced)**
```bash
# Install all dependencies
pip install -r requirements.txt

# Create environment file
cp env.example .env

# Start the full FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test the API
curl -X POST http://localhost:8000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have shoulder pain", "user_id": "user123"}'
```

## 🧪 **Testing Examples**

### **Test 1: Basic Greeting**
```bash
# In interactive mode, type:
"Hi! I'm new to fitness and need guidance."
```

### **Test 2: Injury Detection**
```bash
# In interactive mode, type:
"I have shoulder pain during bench press. What should I do?"
```

### **Test 3: Goal Progress**
```bash
# In interactive mode, type:
"How am I doing with my goal to get Salman Khan's arms?"
```

### **Test 4: Plan Adjustment**
```bash
# In interactive mode, type:
"I'm traveling and won't have gym access. Can you adjust my workout plan?"
```

### **Test 5: Critical Injury**
```bash
# In interactive mode, type:
"I think I tore something in my shoulder. The pain is severe."
```

## 🔧 **Troubleshooting**

### **Issue 1: Ollama not starting**
```bash
# Check if Ollama is already running
ps aux | grep ollama

# Kill existing process if needed
pkill ollama

# Start fresh
ollama serve &
```

### **Issue 2: Model not found**
```bash
# List available models
ollama list

# Download missing model
ollama pull gemma:2b
```

### **Issue 3: Python dependencies missing**
```bash
# Activate virtual environment
source venv/bin/activate

# Install missing packages
pip install httpx fastapi uvicorn
```

### **Issue 4: Port already in use**
```bash
# Check what's using port 11434
lsof -i :11434

# Kill process if needed
kill -9 <PID>
```

## 📊 **Expected Output Examples**

### **Successful Startup**
```
🏋️‍♂️ FITRON AI Coach Chatbot Demo
============================================================
🏥 Checking Ollama health...
✅ Ollama is ready!
🤖 Using model: gemma:2b
```

### **Injury Detection Response**
```
🚨 Injury Risk: medium
🆘 Escalation: Suggested to real trainer
💬 Reply: I understand you're experiencing shoulder pain...
```

### **Goal Progress Response**
```
🎯 Goal Progress: Salman Khan Arms
📈 Progress: 65.5%
💬 Reply: Great progress! You're on track...
```

## 🎮 **Interactive Commands**

Once in interactive mode:
- Type your message and press Enter
- Type `help` for example messages
- Type `quit` to exit
- Use Ctrl+C to interrupt

## 🚀 **Production Deployment**

### **For Production Use:**
1. Use a larger model (mistral:7b or llama2:7b)
2. Set up proper environment variables
3. Use a process manager (systemd, PM2)
4. Set up monitoring and logging
5. Configure reverse proxy (nginx)

### **Environment Variables:**
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export MODEL_NAME=gemma:2b
export DEBUG=false
```

## 🎉 **Success Indicators**

✅ **Ollama running** - `ollama list` shows models  
✅ **Model available** - Your chosen model appears in list  
✅ **Demo starts** - No import errors, health check passes  
✅ **Responses generated** - AI responds to your messages  
✅ **Features working** - Injury detection, goal tracking, etc.  

## 📞 **Getting Help**

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure Ollama is running (`ollama list`)
4. Check virtual environment is activated
5. Try the direct API test to isolate issues

---

**🏋️‍♂️ Ready to revolutionize fitness coaching? Start your FITRON AI Coach today!** 