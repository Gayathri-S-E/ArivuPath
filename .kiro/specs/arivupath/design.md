# ArivuPath — Design & Architecture

This document maps the requirements onto a concrete, buildable architecture. It is
grounded in the real Strands Agents SDK API (`strands.Agent`, `strands.models.BedrockModel`,
the `@tool` decorator, and the "agents as tools" multi-agent pattern).

## 1. High-level architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Frontend (React + TypeScript, Vite, mobile-first, Tamil-first)   │
│  Home · Learn · Practice · My Progress · Profile · Teacher view   │
│  i18n (ta/en) · offline cache (IndexedDB) · service worker        │
└───────────────┬────────────────────────────────────────────────────┘
                │ REST (JSON) over HTTPS,  JWT auth
┌───────────────▼────────────────────────────────────────────────────┐
│  Backend API (FastAPI, Python)                                     │
│  /auth  /content  /learn  /practice  /gaps  /path  /teacher        │
│  Pydantic schemas · JWT · role guard · rate limit · safe-output    │
└───────────────┬────────────────────────────────────────────────────┘
                │ in-process calls
┌───────────────▼────────────────────────────────────────────────────┐
│  Agent layer (Strands Agents SDK)                                  │
│  Orchestrator  ──uses as tools──▶  5 specialist agents             │
│       │                                                             │
│       ├─ Lesson Understanding Agent   (retrieval tools)            │
│       ├─ Tamil Teaching Agent         (explanation)               │
│       ├─ Assessment Agent             (question gen + eval)        │
│       ├─ Learning Gap Detection Agent (analysis)                  │
│       └─ Personalized Learning Path Agent (planning)              │
│  Model provider: BedrockModel (Claude on Amazon Bedrock)          │
└───────────────┬────────────────────────────────────────────────────┘
                │
┌───────────────▼────────────────────────────────────────────────────┐
│  Data & storage                                                    │
│  Repository interface ── local (SQLite+JSON files)  ── OR ──       │
│                          AWS (DynamoDB profiles/progress, S3       │
│                          textbook content, CloudWatch logs)        │
└──────────────────────────────────────────────────────────────────┘
```

Key decision: **local development must work without AWS**. We use a `Repository`
and `ContentStore` interface with two implementations: a local one (SQLite + JSON
seed files) and an AWS one (DynamoDB + S3). The agent layer requires Bedrock to
produce live AI output; when Bedrock is not configured the API returns an explicit
"AI unavailable" error (never a faked answer, per C1/C5).

## 2. Backend project layout

```
backend/
  app/
    main.py                 # FastAPI app factory, router mounting, CORS
    config.py               # pydantic-settings; reads env; NO secrets in code
    deps.py                 # DI: current user, repo, content store, orchestrator
    security.py             # password hashing, JWT encode/verify
    safety.py               # output moderation / safe-content filter
    schemas/                # Pydantic models (API + inter-agent contracts)
      auth.py  content.py  learning.py  assessment.py  gaps.py  path.py
    routers/
      auth.py  content.py  learn.py  practice.py  gaps.py  path.py  teacher.py
    repository/
      base.py               # Repository + ContentStore ABCs
      local.py              # SQLite + JSON seed implementation
      aws.py                # DynamoDB + S3 implementation (optional)
    agents/
      model.py              # build_model(): BedrockModel from env
      lesson_agent.py       # Agent 1 + its @tool retrieval functions
      teaching_agent.py     # Agent 2
      assessment_agent.py   # Agent 3 (+ structured output schemas)
      gap_agent.py          # Agent 4
      path_agent.py         # Agent 5
      orchestrator.py       # main Strands agent using the 5 as tools
      prompts/              # system prompts (ta/en aware) per agent
  content/
    class9/science/electricity/
      lesson.json           # approved/demo concepts + sections (labelled)
      source.md             # human-readable approved content
  tests/
    test_schemas.py
    test_repository_local.py
    test_agents_offline.py  # agents with a stubbed FakeModel (no Bedrock)
    test_orchestrator.py
    test_api.py
  pyproject.toml
  .env.example
  README.md
```

## 3. Agent design (Strands)

All agents are constructed with a shared `BedrockModel` built in `agents/model.py`:

```python
# agents/model.py  (illustrative)
import boto3
from strands.models import BedrockModel
from app.config import settings

def build_model() -> BedrockModel:
    session = boto3.Session(region_name=settings.aws_region)  # creds via env/IAM
    return BedrockModel(model_id=settings.bedrock_model_id,   # from env, not hardcoded
                        temperature=0.3, boto_session=session)
```

### Orchestrator (agents-as-tools pattern)
The orchestrator is a Strands `Agent` whose **tools are the five specialist agents**.
We wrap each specialist in an `@tool` function so we control inputs/outputs and can
inject retrieval context and enforce timeouts/fallbacks (R10.2). The orchestrator's
system prompt encodes the fixed workflow and the rule to prefer the fewest agent
calls needed.

```python
# orchestrator.py (illustrative shape)
from strands import Agent, tool

@tool
def understand_lesson(chapter_id: str, question: str) -> dict:
    """Retrieve approved content and extract the concepts relevant to the question."""
    return lesson_agent_run(chapter_id, question)   # returns a LessonContext dict

@tool
def teach_in_tamil(concept: str, context: str, language: str = "ta") -> dict:
    """Explain a concept step by step in Tamil (or English) grounded in context."""
    ...

# plus: generate_assessment, evaluate_answers, detect_gaps, build_learning_path

orchestrator = Agent(
    model=build_model(),
    system_prompt=ORCHESTRATOR_PROMPT,
    tools=[understand_lesson, teach_in_tamil, generate_assessment,
           evaluate_answers, detect_gaps, build_learning_path],
)
```

### Grounding (anti-hallucination, C2/R3.4)
The Lesson Understanding Agent does **retrieval over approved content only**
(`content/class9/science/electricity/lesson.json`). Its `@tool` functions return
exact approved passages and concept IDs. The Teaching Agent's prompt forbids adding
facts not present in the supplied context and must label output as an AI explanation.
If retrieval returns nothing, the pipeline surfaces "no approved content found".

### Independent testability (R10.3)
Each specialist exposes a plain function (`lesson_agent_run(...)`, etc.) so tests can
run it in isolation. Tests use a Strands-compatible `FakeModel` to avoid live Bedrock
calls in CI, verifying structure/contracts; a marked integration test exercises real
Bedrock when credentials are present.

### Inter-agent contracts (Pydantic)
- `LessonContext { chapter_id, concepts[], passages[], source_label }`
- `Explanation { language, concept, steps[], examples[], ai_generated: true }`
- `Question { id, type, concept_id, prompt, options?, answer_key, difficulty }`
- `Assessment { questions[] }`
- `AnswerEvaluation { question_id, correct, rationale, concept_understood }`
- `GapReport { understood[], needs_revision[], repeated_mistakes[], suggestions[] }`
- `LearningPath { steps[] (ordered activities), rationale }`

## 4. Data model

| Entity | Local (SQLite) | AWS |
|---|---|---|
| User | `users` table | DynamoDB `Users` (PK=userId) |
| Progress | `progress` table | DynamoDB `Progress` (PK=userId, SK=conceptId) |
| AssessmentRecord | `assessments` table | DynamoDB `Assessments` (PK=userId, SK=ts) |
| Content | JSON files under `content/` | S3 bucket `arivupath-content` |
| Logs | stdout / file | CloudWatch Logs |

Progress and assessment records are written only from real answered questions (R4.4,
R11.3). No seed fake history.

## 5. Frontend design

```
frontend/
  src/
    main.tsx  App.tsx  router.tsx
    i18n/        ta.json  en.json  index.ts   # Tamil-first strings
    api/client.ts                              # axios + JWT interceptor
    auth/AuthContext.tsx  RequireRole.tsx
    offline/db.ts (IndexedDB)  sync.ts  useOnline.ts
    components/  (Card, ProgressBar, Badge, QuestionCard, ChartPanel, LangToggle ...)
    pages/
      Home.tsx  Learn.tsx  Practice.tsx  Progress.tsx  Profile.tsx
      Onboarding.tsx  Login.tsx
      teacher/TeacherDashboard.tsx
    styles/tokens.css  (design tokens below)
  index.html  vite.config.ts  tsconfig.json  package.json
  public/manifest.webmanifest  sw.ts (service worker)
```

Design tokens (section 8 of brief):
```
--violet-700 #5B21B6 (primary)   --lavender-200 #E9E3FB (secondary)
--bg #FFFFFF  --bg-soft #F7F5FD  --yellow-400 #F5C518 (achievement)
--green-600 #16A34A (success)    --red-600 #DC2626 (error)
--font-tamil "Noto Sans Tamil", system-ui;  large readable sizing
```
Navigation: Home · Learn · Practice · My Progress · Profile. Teacher dashboard is a
role-gated separate area. Mobile-first, breakpoint 768px.

Offline: approved lessons and saved questions cached in IndexedDB; a service worker
caches the app shell; a sync queue flushes pending activity when `navigator.onLine`
returns true. A persistent banner marks offline mode, and AI actions are disabled
with a clear message offline (R9.3, C5).

## 6. API surface (summary)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | /auth/register | public | student self-register |
| POST | /auth/login | public | obtain JWT |
| GET  | /content/classes | student | available classes/subjects/chapters |
| GET  | /content/chapter/{id} | student | approved lesson summary + concepts |
| POST | /learn/ask | student | orchestrated Tamil/English explanation |
| POST | /practice/generate | student | generate assessment for concepts |
| POST | /practice/evaluate | student | evaluate answers, adapt difficulty |
| GET  | /gaps/{userId} | student(self)/teacher | gap report |
| GET  | /path/{userId} | student(self)/teacher | learning path |
| GET  | /teacher/overview | teacher | class-level insights |

All responses are typed; errors return `{ "error": "message" }` with proper status.
AI endpoints return an explicit error if Bedrock is unconfigured (never a fake answer).

## 7. Security & safety
- Passwords hashed (bcrypt/argon2); JWT with short expiry + env secret.
- Role guard dependency; students can only read their own data.
- `safety.py` screens agent output before returning to students.
- No secrets in code; `.env.example` documents all variables.
- Minimal PII; content clearly labelled AI vs textbook.

## 8. Testing strategy
- Unit: schemas, repository (local), security.
- Agent: each specialist with `FakeModel` (offline, deterministic contract checks).
- Orchestrator: workflow routing with stubbed tools.
- API: FastAPI `TestClient` happy paths + auth/role failures.
- Integration (opt-in, needs AWS): one real Bedrock call smoke test.
- Frontend: component tests for QuestionCard, LangToggle, offline banner.

## 9. Build & phase order
Phase 3 backend+agents (tested offline) → Phase 4 frontend shell → Phase 5 integrate
→ Phase 6 assessment/gaps/path → Phase 7 teacher + offline → Phase 8 full-flow test
→ Phase 9 deploy docs + demo script. Tracked in `tasks.md`.
