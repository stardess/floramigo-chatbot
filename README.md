Repo Layout for Prototype

/floramigo
  /client
    floramigo-chatbot-tts-stt.py     # your app 
    stt_method.py                    # your STT 
    tts_method.py                    # your TTS 
    edge_uploader.py                 # CSV → /ingest/telemetry 
  /server
    app.py                           # FastAPI endpoints (/ingest, /ask, /commands)
    rules.py                         # PHD v1 (deterministic status/actions)
    orchestrator.py                  # prompt build + PCD tips + LLM call + parse cmd
    pcd_snippets.json                # RAG v0 (small care tips)
    db.sql                           # schema bootstrap
  .env.example                       # OPENAI_API_KEY, APP_TOKEN, EDGE_TOKEN, PG_DSN
  README.md                          # how to run locally (SQLite/Postgres)
