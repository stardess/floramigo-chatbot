# 🚀 Floramigo - Quick Start Guide

Get Floramigo up and running in under 5 minutes!

---

## ⚡ Super Quick Start (TL;DR)

```bash
# 1. Clone & setup
git clone https://github.com/stardess/floramigo-chatbot.git
cd floramigo-chatbot
python -m venv venv
source venv/bin/activate

# 2. Install everything
pip install -r requirements-core.txt -r requirements-api.txt -r requirements-client.txt

# 3. Set API key
export OPENAI_API_KEY='sk-your-key-here'

# 4. Launch!
./scripts/demo-full.sh
```

**Done!** Say "Hey Floramigo" to start chatting.

---

## 📋 Prerequisites

### Required
- **Python 3.9 or higher**
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### For Voice Features
- **Microphone** (built-in or USB)
- **Speakers** or headphones
- **OpenAI API key** (get from [platform.openai.com](https://platform.openai.com))

### For Sensor Integration
- **ESP32** or compatible board (optional)
- **Sensors:** DHT11/DHT22, capacitive moisture sensor, photoresistor (optional)

---

## 🔧 Installation Steps

### Step 1: Install Python

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version  # Should show 3.9+
```

---

### Step 2: Clone Repository

```bash
git clone https://github.com/stardess/floramigo-chatbot.git
cd floramigo-chatbot
```

Or download ZIP and extract.

---

### Step 3: Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify
which python  # Should point to venv/bin/python
```

---

### Step 4: Install Dependencies

**Option A: All Dependencies (Recommended)**
```bash
pip install -r requirements-core.txt -r requirements-api.txt -r requirements-client.txt
```

**Option B: Separate Installation**
```bash
# Core dependencies (required)
pip install -r requirements-core.txt

# API server dependencies
pip install -r requirements-api.txt

# Client dependencies (for voice/chat)
pip install -r requirements-client.txt
```

**Verify installation:**
```bash
python -c "import fastapi, openai, uvicorn; print('✓ All imports OK')"
```

---

### Step 5: Get OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign in or create account
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

**Set the key:**

**macOS/Linux:**
```bash
export OPENAI_API_KEY='sk-your-key-here'

# Add to ~/.bashrc or ~/.zshrc for persistence:
echo "export OPENAI_API_KEY='sk-your-key-here'" >> ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='sk-your-key-here'
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

Or create `.env` file in project root:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

---

### Step 6: Verify Installation

```bash
./scripts/test-system.sh
```

Should show all green checkmarks ✓

---

## 🎯 Choose Your Launch Mode

### Mode 1: Full System (Voice + API) 🌟

**Best for:** Demos, showcasing full capabilities

```bash
./scripts/demo-full.sh
```

**What it does:**
- Starts API server on port 8000
- Ingests sample sensor data
- Launches voice chatbot with wake word detection

**Usage:**
- Say "Hey Floramigo" to activate
- Ask questions naturally
- Press Ctrl+C to exit

---

### Mode 2: API Server Only

**Best for:** Backend development, API integration

```bash
./scripts/demo-api.sh
```

**What it does:**
- Starts FastAPI server
- Shows curl examples
- Opens docs at http://localhost:8000/docs

**Try these:**
```bash
# Health check
curl http://localhost:8000/healthz

# Ingest data
curl -X POST http://localhost:8000/ingest/telemetry \
  -H 'Content-Type: application/json' \
  -d '{"temperature": 24.5, "humidity": 45, "moisture_pct": 40}'

# Ask question
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"message": "How is my plant?"}'
```

---

### Mode 3: Voice Chatbot Only

**Best for:** Testing voice features

```bash
# Start API first (in terminal 1)
uvicorn api.main:app --reload

# Then voice chatbot (in terminal 2)
./scripts/demo-voice.sh
```

---

### Mode 4: Text Chatbot

**Best for:** Quick questions without voice

```bash
# Start API first
uvicorn api.main:app --reload &

# Run text client
python client/floramigo-chat.py
```

**Commands:**
- Type questions and press Enter
- `status` - Get plant status
- `exit` - Quit

---

## 🧪 Test Everything Works

```bash
# Run system validation
./scripts/test-system.sh

# Run test suite
pytest tests/ -v

# Test voice chatbot (audio only)
python client/floramigo-voice.py --test-audio
```

---

## 🎬 Your First Conversation

After launching with `./scripts/demo-full.sh`:

```
🌿 Floramigo is ready!
   Say "hey flora" or "hey floramigo" to start

You: "Hey Floramigo"

🌿 Floramigo: "I'm listening! What would you like to know?"

You: "How is my plant doing?"

🌿 Floramigo: "Your plant is doing well! The temperature is 24.5°C, 
which is perfect. The soil moisture is at 38%, which is slightly low. 
I'd recommend watering soon. The humidity at 45% is good for most plants."

You: "Should I water it now?"

🌿 Floramigo: "Yes, I'd recommend watering now. The soil moisture at 
38% indicates the soil is getting dry. Water until you see a bit of 
drainage from the bottom..."
```

---

## 🐛 Troubleshooting

### Problem: `ModuleNotFoundError`

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements-core.txt -r requirements-api.txt -r requirements-client.txt
```

---

### Problem: Voice chatbot doesn't hear me

**Solutions:**
1. Check microphone permissions (System Preferences → Security & Privacy → Microphone)
2. Test microphone: `python client/floramigo-voice.py --test-audio`
3. Adjust microphone volume
4. Try different USB microphone
5. Check wake word threshold in code

---

### Problem: `401 Unauthorized` from OpenAI

**Solutions:**
1. Verify API key is set: `echo $OPENAI_API_KEY`
2. Check key is valid on [platform.openai.com](https://platform.openai.com)
3. Ensure key starts with `sk-`
4. Check you have credits available

---

### Problem: API won't start (port in use)

**Solutions:**
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn api.main:app --port 8001
```

---

### Problem: PyAudio installation fails

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

---

### Problem: "No module named 'floramigo'"

**Solution:**
```bash
# Make sure you're in project root
pwd  # Should show .../floramigo-chatbot

# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or reinstall in development mode
pip install -e .
```

---

## 📚 Next Steps

### Learn More
- Read [DEMO_GUIDE.md](DEMO_GUIDE.md) for interview preparation
- Check [docs/system-architecture.md](docs/system-architecture.md) for technical details
- Review [TEST_RESULTS.md](TEST_RESULTS.md) for quality metrics

### Customize
- Edit `floramigo/pcd/threshold.yaml` for plant thresholds
- Modify `floramigo/pcd/pcd_snippets.py` for custom care tips
- Update wake words in `client/floramigo-voice.py`

### Extend
- Add REST API endpoints in `api/routers/`
- Create custom plant profiles
- Integrate with mobile app
- Connect additional sensors

---

## 🆘 Get Help

- **Documentation:** See `docs/` directory
- **Issues:** [GitHub Issues](https://github.com/stardess/floramigo-chatbot/issues)
- **Examples:** Check `scripts/` for demo scripts
- **Tests:** Look at `tests/` for usage examples

---

## ✅ Quick Reference Checklist

Before demo or interview:

- [ ] Python 3.9+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list`)
- [ ] OpenAI API key set (`echo $OPENAI_API_KEY`)
- [ ] Tests pass (`./scripts/test-system.sh`)
- [ ] Microphone and speakers working
- [ ] API starts successfully
- [ ] Voice chatbot responds to wake word
- [ ] Documentation reviewed

---

**Happy planting! 🌿**
