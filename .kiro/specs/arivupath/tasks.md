# ArivuPath — Implementation Plan

Tasks are ordered to match the brief's phases. Each references requirements it
satisfies. Check off as completed. Keep the MVP focused on Class 9 Science / Electricity.

## Phase 2 — Spec (this document set)
- [x] 0. Requirements, design, and task breakdown authored in `.kiro/specs/arivupath/`.

## Phase 3 — Strands multi-agent backend (tested independently)
- [ ] 1. Backend scaffold: `pyproject.toml`, `app/config.py` (env-driven, no secrets),
       `.env.example`, FastAPI `main.py`, health route. _(C3, R10.4)_
- [ ] 2. Seed approved Class 9 Science Electricity content (`content/.../lesson.json`,
       `source.md`) with concept IDs and passages, clearly labelled demo content. _(C2, R3)_
- [ ] 3. Pydantic schemas for API + inter-agent contracts. _(R10.2)_
- [ ] 4. Local repository + content store (SQLite + JSON); no fake history. _(R11.3)_
- [ ] 5. `agents/model.py` BedrockModel builder from env; `FakeModel` test double. _(C3, R10.4)_
- [ ] 6. Lesson Understanding Agent + retrieval `@tool`s over approved content. _(R3)_
- [ ] 7. Tamil Teaching Agent (grounded, labelled AI, step-by-step, ta/en). _(R3, R8)_
- [ ] 8. Assessment Agent: generate 5 question types + evaluate conceptually. _(R4)_
- [ ] 9. Learning Gap Detection Agent → structured GapReport. _(R5)_
- [ ] 10. Personalized Learning Path Agent → ordered adaptive plan. _(R6)_
- [ ] 11. Orchestrator (agents-as-tools) with timeouts/fallbacks/min-calls. _(R10)_
- [ ] 12. Agent unit tests (offline FakeModel) + opt-in Bedrock integration test. _(R10.3)_

## Phase 4–5 — Frontend shell + integration
- [ ] 13. Auth: register/login routes, JWT, hashing, role guard. _(R1)_
- [ ] 14. API routers: content, learn, practice, gaps, path, teacher. _(R2–R7)_
- [ ] 15. Safe-output filter wired into AI responses. _(R11.2)_
- [ ] 16. Frontend scaffold: Vite + React + TS, tokens, i18n (ta/en), router,
        AuthContext, axios client. _(R8)_
- [ ] 17. Onboarding + Login + Dashboard pages (real data, empty states). _(R1, R2)_
- [ ] 18. Learn page: chapter select, ask in Tamil/English, grounded answer UI with
        AI-vs-textbook labelling. _(R3, R8)_

## Phase 6 — Assessment, gaps, path
- [ ] 19. Practice page: QuestionCard for all types, feedback, hints, adaptive next. _(R4)_
- [ ] 20. My Progress page: gaps + path with charts and visual indicators. _(R5, R6)_

## Phase 7 — Teacher + offline
- [ ] 21. Teacher dashboard (role-gated): per-student + class-level insights. _(R7)_
- [ ] 22. Offline: IndexedDB cache, service worker, sync queue, online/offline
        banner, AI-requires-internet markers. _(R9, C5)_

## Phase 8 — Full-flow testing
- [ ] 23. End-to-end test of the demo scenario; Tamil rendering; error paths;
        privacy/role checks. _(Success criteria, R11)_

## Phase 9 — Deployment & demo
- [ ] 24. AWS integration impl (DynamoDB/S3/CloudWatch) behind repository interface,
        documented and testable; optional for local demo. _(C7)_
- [ ] 25. Infra templates + AWS deployment docs. _(Deliverable 8)_
- [ ] 26. Root README: architecture, social impact, setup, run, demo script <3 min. _(Deliverables 11, 10)_
