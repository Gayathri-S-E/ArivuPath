# ArivuPath — Requirements

> அறிவுப்பாதை · "Every Student Deserves a Personal Learning Path."
>
> Tamil-first, multi-agent AI learning companion for rural government-school students
> in Madurai district, Tamil Nadu. MVP curriculum: **Class 9 Science → Electricity**.

## 1. Introduction

ArivuPath is a personalized learning platform that uses a multi-agent AI system
(built on the **Strands Agents SDK** over **Amazon Bedrock**) to understand a
student's learning gaps, explain lessons in simple Tamil and English, generate and
evaluate practice questions, and produce an adaptive learning path. It targets
Tamil-medium and first-generation learners in Classes 6–10, starting with a single
fully working demonstration curriculum.

The system is **not** a generic chatbot. It is a structured learning and assessment
platform with distinct, cooperating specialist agents and a verifiable workflow.

## 2. Glossary

| Term | Meaning |
|---|---|
| Lesson | A chapter unit of approved curriculum content (e.g. "Electricity"). |
| Concept | A sub-topic within a lesson (e.g. "Electric current", "Ohm's law"). |
| Assessment | A set of generated questions targeting specific concepts. |
| Learning gap | A concept the student has not demonstrated understanding of. |
| Learning path | An ordered, adaptive sequence of activities for one student. |
| Approved content | Textbook/curriculum material supplied or seeded, never AI-invented. |
| Agent | A Strands `Agent` with a focused responsibility and tools. |

## 3. Non-negotiable constraints (from project brief)

- C1. The backend MUST genuinely use the Strands Agents SDK with a multi-agent
  architecture — never a single chatbot, never hardcoded AI responses.
- C2. Curriculum facts MUST come from approved/seeded content, never invented by
  the model. AI explanations MUST be visibly distinguished from textbook content.
- C3. No AWS credentials, API keys, or model IDs hardcoded. Use env vars / IAM.
- C4. Tamil is a first-class language with correct Unicode rendering, not a
  word-for-word translation layer.
- C5. Offline/cached responses MUST never be presented as live AI output.
- C6. Student PII (minors) protected; role-based access; store only what is needed.
- C7. Do not claim an AWS integration unless it is implemented and testable.
- C8. MVP stays focused on Class 9 Science / Electricity; architecture stays
  extensible but we do not build all classes before the MVP works.

---

## 4. Functional requirements

### R1 — Student onboarding & authentication
**User story:** As a student, I want to register and sign in securely, so that my
learning progress is private and tied to me.

#### Acceptance criteria
1. WHEN a new student submits name, class (6–10), medium (Tamil/English), subject,
   and learning preferences THEN the system SHALL create a student profile and a
   secure credential.
2. The system SHALL authenticate using signed tokens (JWT) and SHALL NOT store
   plaintext passwords (hashed with a strong algorithm).
3. The system SHALL assign a role of `student` or `teacher`; teacher accounts are
   provisioned, not self-registered into teacher role.
4. The system SHALL collect only the minimum PII required and SHALL NOT expose one
   student's data to another student.
5. WHEN authentication fails THEN the system SHALL return a generic error without
   revealing whether the account exists.

### R2 — Learning dashboard
**User story:** As a student, I want a clean dashboard, so that I can see where I am
and what to do next.

#### Acceptance criteria
1. The dashboard SHALL display a Tamil/English welcome, current class/subject,
   "Continue Learning", recent assessments, recommended next lesson, learning
   streak, and areas needing improvement.
2. All displayed progress values SHALL be derived from stored real activity, never
   fabricated.
3. WHEN the student has no history THEN the dashboard SHALL show an onboarding
   empty-state rather than fake data.

### R3 — AI lesson learning
**User story:** As a student, I want to open a chapter and ask questions in Tamil or
English, so that I understand the concept.

#### Acceptance criteria
1. The student SHALL select class, subject, and chapter from approved content.
2. WHEN the student asks a question THEN the orchestrator SHALL route it through the
   Lesson Understanding Agent (retrieval over approved content) and the Tamil
   Teaching Agent (explanation) and return a step-by-step answer.
3. The response SHALL cite which concept/section of approved content it is grounded
   in, and SHALL mark the explanation as AI-generated.
4. IF no approved content matches THEN the system SHALL say so rather than invent
   facts.
5. The student MAY request an English explanation or a real-life example.

### R4 — Guided practice & assessment
**User story:** As a student, I want practice questions with feedback, so that I can
check and build my understanding.

#### Acceptance criteria
1. The Assessment Agent SHALL generate MCQ, true/false, fill-in-the-blank,
   short-answer, and concept-based questions for a selected concept set.
2. WHEN the student answers THEN the system SHALL show correctness, explain why,
   offer a hint when wrong, and adapt the next question's difficulty.
3. Evaluation SHALL assess conceptual understanding, not only count marks.
4. Each answered question SHALL be persisted with the concept it targeted and the
   outcome.

### R5 — Learning gaps
**User story:** As a student, I want to see what I've mastered and what needs work,
so that I can focus my effort.

#### Acceptance criteria
1. The Learning Gap Detection Agent SHALL analyze assessment history and produce a
   structured report: concepts understood, concepts needing revision, repeated
   mistakes, and suggested revision activities.
2. The report SHALL distinguish likely memorization from conceptual understanding.
3. The UI SHALL present gaps with simple visual indicators and progress charts.

### R6 — Personalized learning path
**User story:** As a student, I want a roadmap tailored to me, so that I always know
the next best step.

#### Acceptance criteria
1. The Personalized Learning Path Agent SHALL combine lesson, teaching, and
   assessment data into an ordered activity plan (understand → Tamil explanation →
   example → practice → review → short assessment).
2. The path SHALL adapt when new performance data arrives.
3. Improvement SHALL be tracked across multiple sessions.

### R7 — Teacher insights
**User story:** As a teacher, I want visibility into my students, so that I can
support those who are struggling.

#### Acceptance criteria
1. A teacher-only view SHALL show per-student progress, frequently misunderstood
   concepts, class-level gaps, assessment summaries, and at-risk students.
2. Access SHALL be restricted to authenticated teacher-role accounts and only to
   their authorized students.

### R8 — Tamil-first experience
#### Acceptance criteria
1. The entire UI SHALL be available in Tamil and English with a language toggle.
2. Tamil SHALL render with correct Unicode and readable typography sized for
   Classes 6–10.
3. Tamil explanations SHALL be natural and age-appropriate, using correct Tamil
   educational terminology.

### R9 — Offline & low connectivity
#### Acceptance criteria
1. The student SHALL be able to download approved lesson content and saved practice
   questions for offline use.
2. Offline activity SHALL be stored locally and synced when connectivity returns.
3. The UI SHALL clearly mark which features require the internet, and SHALL never
   present a cached answer as a live AI response.

### R10 — Multi-agent backend (Strands)
#### Acceptance criteria
1. Five specialist agents (Lesson Understanding, Tamil Teaching, Assessment,
   Learning Gap Detection, Personalized Learning Path) and one Orchestrator SHALL
   be implemented as Strands agents.
2. Agents SHALL exchange structured data (typed schemas), with error handling,
   timeouts, and explicit fallbacks.
3. Each agent SHALL be independently testable.
4. The system SHALL run against Amazon Bedrock when credentials are configured, and
   SHALL degrade gracefully (clear error, no fake AI output) when they are not.

### R11 — Data & safety
#### Acceptance criteria
1. Content served as fact SHALL come only from approved/seeded sources or be clearly
   labelled demonstration content.
2. The system SHALL apply safe-output handling so students do not receive
   inappropriate content.
3. Student history SHALL never be fabricated; assessment records reflect real
   activity only.

---

## 5. Out of scope for MVP
- Classes/subjects beyond Class 9 Science / Electricity (architecture supports them).
- Voice interaction (optional, stubbed interface only if time permits).
- Native mobile apps (responsive web only).
- Production AWS deployment automation beyond documented IaC templates.

## 6. Success criteria (demo)
The hackathon scenario in section 10 of the brief runs end-to-end on the real app:
login → select Class 9 Science → Electricity → ask in Tamil → grounded Tamil
explanation → 5 generated questions → answer → gap report → path recommendation →
dashboard updates. No step is faked or hardcoded.
