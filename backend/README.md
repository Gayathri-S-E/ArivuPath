# ArivuPath Backend

Tamil-first multi-agent AI learning companion — FastAPI + Strands Agents SDK over
Amazon Bedrock. See `../.kiro/specs/arivupath/` for requirements, design, and tasks.

## Quick start (local, no AWS needed)

```bash
py -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
copy .env.example .env          # edit values; leave BEDROCK_* unset for now
uvicorn app.main:app --reload
```

- With `BEDROCK_ENABLED=0` the app runs fully; AI endpoints return an explicit
  "AI unavailable" error instead of a fabricated answer.
- To enable live AI, set `AWS_REGION`, `BEDROCK_MODEL_ID`, `BEDROCK_ENABLED=1`
  and provide AWS credentials (env vars or IAM role) with Bedrock access.

## Tests

```bash
pytest -m "not integration"     # offline: uses a deterministic fake model
pytest -m integration           # live Bedrock smoke test (needs real creds)
```
