# Backend and Database Pipeline Plan

This plan turns the static OSM checking mockup into a real, auditable evaluation system. Keep the current project as a training/demo application unless you receive explicit legal, security, and board-level approval for handling real examination data.

## 1. Recommended system modules

1. **Authentication and roles**
   - Use separate roles for `admin`, `evaluator`, and `moderator`.
   - Enforce multi-factor authentication and session expiry for evaluator accounts.
   - Never store plain-text passwords; use a managed identity provider where possible.
2. **Bundle assignment**
   - Import anonymized answer-script metadata into bundles.
   - Assign bundles to evaluators with due dates, status tracking, and conflict-of-interest checks.
3. **Script viewer service**
   - Store scanned pages in private object storage.
   - Serve pages through short-lived signed URLs, not public file paths.
4. **Evaluation service**
   - Save draft marks question-by-question.
   - Validate each mark against the question maximum before saving.
   - Require final confirmation before submission.
5. **Moderation and audit**
   - Route flagged scripts and random samples to moderators.
   - Record every save, submit, approve, return, and mark change in an append-only audit log.

## 2. Data flow pipeline

```text
Scan upload -> OCR/page validation -> anonymization -> bundle creation
  -> evaluator assignment -> draft marking -> validation -> final submit
  -> moderation sampling/flag review -> locked results export -> archive
```

## 3. Database tables

The prototype schema in `backend/schema.sql` includes these core tables:

- `users`: evaluator, moderator, and admin identities.
- `script_bundles`: subject/exam bundles assigned to evaluators.
- `answer_scripts`: anonymized script records and workflow status.
- `script_pages`: page ordering and private image references.
- `questions`: question maxima and rubric text.
- `evaluations`: one evaluator's draft/submitted evaluation for a script.
- `marks`: question-wise marks linked to an evaluation.
- `annotations`: page-level notes, ticks, highlights, or review comments.
- `audit_events`: immutable trail for compliance and moderation.

For production, add encryption-at-rest, backups, row-level authorization, and a strict data-retention policy.

## 4. API endpoints in this scaffold

The local standard-library API in `backend/app.py` provides a small starting point:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check that the API is running. |
| `GET` | `/api/scripts` | List assigned demo scripts. |
| `GET` | `/api/scripts/{id}` | Load script pages, questions, evaluation, and marks. |
| `PATCH` | `/api/scripts/{id}/marks` | Save draft question-wise marks and remarks. |
| `POST` | `/api/scripts/{id}/submit` | Submit the demo evaluation. |

## 5. Development pipeline

1. **Local development**
   - Run the frontend with `python3 -m http.server 8000`.
   - Run the API with `python3 backend/app.py`.
   - Use SQLite for local demos only.
2. **Testing**
   - Unit test mark validation, status transitions, and audit-event creation.
   - Integration test API endpoints with a temporary database.
   - Add accessibility and visual regression checks for the frontend.
3. **Staging**
   - Replace local SQLite with PostgreSQL.
   - Replace demo page paths with private object storage signed URLs.
   - Enable realistic anonymized test data only.
4. **Production readiness**
   - Add identity provider integration, MFA, RBAC, audit exports, backup drills, monitoring, and incident response.
   - Complete privacy review and threat modeling before any real exam data enters the system.

## 6. Next implementation steps

- Connect `script.js` to `GET /api/scripts` and `PATCH /api/scripts/{id}/marks`.
- Add login/session middleware before exposing any non-demo data.
- Add automated tests around `backend/app.py` using a temporary SQLite database.
- Move script images to protected storage and store only signed URL references in API responses.
