# 🌿 Floramigo - Intelligent Plant Care System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-orange.svg)](https://openai.com/)
[![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](TEST_RESULTS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Production-ready AI plant care assistant with voice interaction, real-time sensor monitoring, and intelligent recommendations.**

---

## 🎯 What is Floramigo?

Floramigo is an intelligent plant monitoring and care system that combines:

- 🌡️ **Real-time IoT sensor monitoring** (temperature, humidity, soil moisture, light)
- 🤖 **AI-powered conversation** via GPT-4 with plant care expertise
- 🎤 **Voice interface** with wake word detection ("Hey Floramigo")
- 📊 **Automated health alerts** based on configurable thresholds
- 📱 **REST API** for integration with apps and devices
- 🧪 **95%+ test coverage** with comprehensive validation

Perfect for plant enthusiasts, developers, and anyone building IoT + AI applications.

---

## ✨ Key Features

### 🎤 **Voice Interaction**
- Wake word detection ("Hey Floramigo", "Hey Flora")
- Natural conversation powered by OpenAI Whisper + GPT-4 + TTS
- Hands-free plant care while gardening
- Multi-turn conversation with context

### 🌡️ **Real-time Monitoring**
- Continuous sensor data ingestion
- Automatic threshold checking and alerts
- 24-hour historical data tracking
- Support for multiple plant species with custom thresholds

### 🤖 **Intelligent Responses**
- Context-aware plant care advice
- Species-specific recommendations
- Actionable watering, light, and temperature guidance
- Graceful fallback when offline

### 🚀 **Production-Grade Architecture**
- FastAPI REST API with 7 endpoints
- Clean separation of concerns (API, core logic, clients)
- Async/await for high performance
- Comprehensive error handling and logging
- Docker-ready with health checks

---

## 🚀 Quick Start (3 Methods)

### Option 1: One-Command Demo (Recommended)

```bash
# Clone and setup
git clone https://github.com/stardess/floramigo-chatbot.git
cd floramigo-chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-core.txt -r requirements-api.txt -r requirements-client.txt

# Set OpenAI API key
export OPENAI_API_KEY='sk-your-key-here'

# Launch full system (API + Voice)
./scripts/demo-full.sh
```

**That's it!** Say "Hey Floramigo" and start chatting.

---

### Option 2: API-Only Demo

```bash
# Start API server
./scripts/demo-api.sh

# In another terminal, try:
curl http://localhost:8000/healthz
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"message": "How is my plant doing?"}'
```

Browse interactive docs at: **http://localhost:8000/docs**

---

### Option 3: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements-core.txt -r requirements-api.txt -r requirements-client.txt

# 2. Set API key
export OPENAI_API_KEY='sk-your-key-here'

# 3. Start API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 4. In another terminal, ingest sample data
curl -X POST http://localhost:8000/ingest/telemetry \
  -H 'Content-Type: application/json' \
  -d '{"temperature": 24.5, "humidity": 45, "moisture_pct": 38, "light_raw": 180}'

# 5. Start voice chatbot
python client/floramigo-voice.py

# OR start text chatbot
python client/floramigo-chat.py
```

---

## 📁 Project Structure

```
floramigo-chatbot/
├── 🔌 api/                      # FastAPI REST API
│   ├── main.py                  # Application entry point
│   ├── models/                  # Pydantic schemas
│   └── routers/                 # API endpoints
│       ├── ask.py               # Chat endpoint
│       ├── health.py            # Health checks
│       ├── ingest.py            # Sensor data ingestion
│       └── phd.py               # Plant health diagnosis
│
├── 🧠 floramigo/                # Core business logic
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── phd.py               # Plant Health Daemon
│   │   ├── orchestrator.py     # Context & prompt building
│   │   ├── llm_client.py        # OpenAI integration
│   │   └── rag_pipeline.py     # Plant care knowledge base
│   ├── voice/                   # Voice components
│   │   ├── stt_method.py        # Speech-to-text
│   │   └── tts_method.py        # Text-to-speech
│   └── pcd/                     # Plant Care Database
│       └── pcd_snippets.py      # Care tips and thresholds
│
├── 💬 client/                   # User interfaces
│   ├── floramigo-voice.py       # Voice chatbot (wake word)
│   ├── floramigo-chat.py        # Text chatbot (terminal)
│   └── edge_uploader.py         # CSV data uploader
│
├── 🧪 tests/                    # Test suite (95%+ coverage)
│   ├── test_api.py              # API endpoint tests
│   ├── test_phd.py              # Health daemon tests
│   ├── test_orchestrator.py    # Orchestration tests
│   └── test_integration.py     # End-to-end tests
│
├── 📚 docs/                     # Documentation
│   ├── system-architecture.md   # Architecture deep-dive
│   ├── api-contracts.md         # API specifications
│   └── runbook.md               # Operations guide
│
├── 🚀 scripts/                  # Demo launchers
│   ├── demo-full.sh             # Full system demo
│   ├── demo-api.sh              # API-only demo
│   ├── demo-voice.sh            # Voice-only demo
│   └── test-system.sh           # System validation
│
├── 📊 data/                     # Runtime data
│   ├── current_readings.json    # Latest sensor data
│   ├── sensor_history.json      # 24h historical data
│   └── alerts.json              # Alert log
│
├── README.md                    # This file
├── DEMO_GUIDE.md                # Interview demo script
├── STATUS.md                    # System status & metrics
└── TEST_RESULTS.md              # Test coverage report
```

---

## 🎯 Use Cases & Demo Scenarios

### Scenario 1: Voice Interaction Demo
```bash
./scripts/demo-full.sh

# Say: "Hey Floramigo, how is my plant doing?"
# Floramigo: "Your basil is doing well! Temperature is 24°C..."

# Say: "Should I water it today?"
# Floramigo: "The soil moisture is at 38%, which is slightly low..."
```

### Scenario 2: API Integration Demo
```bash
./scripts/demo-api.sh

# Then use curl or browse http://localhost:8000/docs
# Show IoT device integration, mobile app backend, etc.
```

### Scenario 3: Multi-Plant Management
```bash
# Ingest data for multiple plants
curl -X POST http://localhost:8000/ingest/telemetry \
  -d '{"temperature": 24, "moisture_pct": 40, "plant_name": "Basil"}'

curl -X POST http://localhost:8000/ingest/telemetry \
  -d '{"temperature": 22, "moisture_pct": 25, "plant_name": "Succulent"}'

# Query specific plant
curl -X POST http://localhost:8000/ask \
  -d '{"message": "Status?", "plant_name": "Basil"}'
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ Voice Client │ Text Client  │  Mobile App  │  Web Dashboard│
│ (wake word)  │  (terminal)  │  (future)    │   (future)    │
└──────┬───────┴──────┬───────┴──────┬───────┴───────────┬───┘
       │              │              │                   │
       └──────────────┴──────────────┴───────────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │   FastAPI REST API       │
                 │  (7 endpoints, async)    │
                 └─────────┬────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌─────────┐    ┌──────────────┐  ┌──────────┐
    │  Chat   │    │   Telemetry  │  │ Monitor  │
    │ Handler │    │   Ingestion  │  │ Control  │
    └────┬────┘    └──────┬───────┘  └────┬─────┘
         │                │               │
         └────────────────┼───────────────┘
                          ▼
            ┌──────────────────────────────┐
            │   Plant Health Daemon (PHD)  │
            │  • Normalize sensor data     │
            │  • Check thresholds          │
            │  • Generate alerts           │
            │  • Track history             │
            └──────────┬───────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌─────────┐   ┌────────┐
    │Current │   │ History │   │ Alerts │
    │Reading │   │ (24h)   │   │  Log   │
    └────────┘   └─────────┘   └────────┘
                       │
                       ▼
            ┌─────────────────────────┐
            │     Orchestrator        │
            │  • Build context        │
            │  • Add care tips        │
            │  • Call LLM             │
            └──────────┬──────────────┘
                       │
                       ▼
            ┌─────────────────────────┐
            │    LLM Client (GPT-4)   │
            │  • Graceful fallback    │
            │  • Token management     │
            └─────────────────────────┘
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthz` | Health check for monitoring |
| `GET` | `/health` | Detailed health status |
| `POST` | `/ask` | Ask Floramigo a question |
| `POST` | `/ingest/telemetry` | Ingest sensor data |
| `GET` | `/ingest/current` | Get current readings |
| `GET` | `/ingest/alerts` | Get recent alerts |
| `GET` | `/diagnose` | Get plant diagnosis |
| `POST` | `/monitor/start` | Start serial monitoring |
| `POST` | `/monitor/stop` | Stop serial monitoring |

**Full API documentation:** http://localhost:8000/docs (when running)

---

## 🧪 Testing & Quality

```bash
# Run full test suite
pytest tests/ -v

# With coverage report
pytest tests/ --cov=floramigo --cov=api --cov-report=html

# Run system validation
./scripts/test-system.sh
```

**Test Coverage:** 95.3% (see [TEST_RESULTS.md](TEST_RESULTS.md))

**Quality Metrics:**
- ✅ 50 tests, all passing
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Clean architecture (SOLID principles)
- ✅ Error handling and logging
- ✅ Security best practices

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [DEMO_GUIDE.md](DEMO_GUIDE.md) | Complete demo walkthrough for interviews |
| [STATUS.md](STATUS.md) | System status and production readiness |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Detailed test results and coverage |
| [docs/system-architecture.md](docs/system-architecture.md) | Architecture deep-dive |
| [docs/api-contracts.md](docs/api-contracts.md) | API request/response specs |
| [docs/runbook.md](docs/runbook.md) | Operations and troubleshooting |
| [dev-guide.md](dev-guide.md) | Developer setup and workflows |

---

## 🛠️ Configuration

### Environment Variables

```bash
# Required for voice & LLM features
export OPENAI_API_KEY='sk-your-key-here'

# Optional configurations
export FLORAMIGO_OPENAI_MODEL='gpt-4'           # Default: gpt-4o-mini
export FLORAMIGO_API_HOST='0.0.0.0'            # Default: 0.0.0.0
export FLORAMIGO_API_PORT='8000'                # Default: 8000
export FLORAMIGO_API_URL='http://localhost:8000' # For client
export PLANT_NAME='Basil'                       # Default plant name
export FLORAMIGO_SERIAL_PORT='/dev/ttyUSB0'    # For serial monitoring
export FLORAMIGO_BAUD_RATE='9600'              # Serial baud rate
```

### Plant Thresholds

Customize thresholds in `floramigo/pcd/threshold.yaml`:

```yaml
basil:
  temperature:
    min: 18
    max: 28
  moisture:
    min: 30
    critical: 15
  humidity:
    min: 40
```

---

## 🚢 Deployment

### Docker (Coming Soon)

```bash
docker-compose up
```

### Manual Deployment

```bash
# Install production dependencies
pip install -r requirements-api.txt -r requirements-core.txt

# Run with gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 🤝 Contributing

Contributions welcome! This project follows clean code principles and comprehensive testing.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure tests pass (`pytest tests/`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Stardess Karitonze** - *Lead Developer* - [@stardess](https://github.com/stardess)
- **Faith Ndanu** - *Contributor* - [@fndanu](https://github.com/fndanu)

---

## 🙏 Acknowledgments

- OpenAI for GPT-4, Whisper, and TTS APIs
- FastAPI framework for excellent async support
- Plant care community for threshold data
- Open source community

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/stardess/floramigo-chatbot/issues)
- **Documentation:** See `docs/` directory
- **Demo Guide:** [DEMO_GUIDE.md](DEMO_GUIDE.md)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

---

**Built with ❤️ for plants and developers**
