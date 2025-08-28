Repo Layout for Prototype

/floramigo <br>
  &nbsp;&nbsp;/client<br>
  &nbsp;&nbsp;&nbsp;&nbsp;floramigo-chatbot-tts-stt.py     # your app <br>
  &nbsp;&nbsp;&nbsp;&nbsp;stt_method.py                    # your STT <br>
  &nbsp;&nbsp;&nbsp;&nbsp;tts_method.py                    # your TTS <br>
  &nbsp;&nbsp;&nbsp;&nbsp;edge_uploader.py                 # CSV → /ingest/telemetry <br>
  &nbsp;&nbsp;/server<br>
  &nbsp;&nbsp;&nbsp;&nbsp;app.py                           # FastAPI endpoints (/ingest, /ask, /commands)<br>
  &nbsp;&nbsp;&nbsp;&nbsp;rules.py                         # PHD v1 (deterministic status/actions)<br>
  &nbsp;&nbsp;&nbsp;&nbsp;orchestrator.py                  # prompt build + PCD tips + LLM call + parse cmd<br>
  &nbsp;&nbsp;&nbsp;&nbsp;pcd_snippets.json                # RAG v0 (small care tips)<br>
  &nbsp;&nbsp;&nbsp;&nbsp;db.sql                           # schema bootstrap<br>
  &nbsp;&nbsp;.env.example                       # OPENAI_API_KEY, APP_TOKEN, EDGE_TOKEN, PG_DSN<br>
  &nbsp;&nbsp;README.md                          # how to run locally (SQLite/Postgres)<br>
