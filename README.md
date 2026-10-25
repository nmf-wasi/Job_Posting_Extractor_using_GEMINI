# Job Posting Extractor API

A small FastAPI service that turns the text of a job posting into validated JSON, using Gemini structured outputs. Send messy text, get typed fields back, or a clear error when the input or the model output can't be used.

## Example

```bash
curl -X POST http://127.0.0.1:8000/llm/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Notion is hiring a Junior Backend Engineer in Dublin. Python, FastAPI, SQL required. 1+ years experience. We sponsor work visas."}'
```

```json
{
  "is_job_posting": true,
  "title": "Junior Backend Engineer",
  "company": "Notion",
  "location": "Dublin",
  "required_skills": ["Python", "FastAPI", "SQL"],
  "years_experience": 1,
  "visa_sponsorship": "yes"
}
```

Fields that are not in the text come back as `null` (or `"unclear"` for visa sponsorship) instead of being invented.

## Endpoints

| Route | Description |
|---|---|
| `POST /llm/extract` | Extract structured fields from a job posting |
| `GET /health` | Health check |

### Status codes for `/llm/extract`

| Code | Meaning |
|---|---|
| 200 | Extraction succeeded |
| 422 | Empty or invalid request body, or the text is not a job posting |
| 502 | The model returned unusable output (for example, a truncated response) |
| 503 | Gemini is unavailable or over quota, retry later |

## Setup

```bash
git clone https://github.com/nmf-wasi/Job_Posting_Extractor_using_GEMINI
cd Job_Posting_Extractor_using_GEMINI
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your Gemini API key in .env
uvicorn app.src.main:app --reload
```

Interactive docs are at `http://127.0.0.1:8000/docs`.

## Tests

```bash
pytest
```

The tests never call Gemini. The route gets its extractor through a FastAPI dependency (`get_extractor`), and the tests override it with a fake that returns a posting or raises an error. That lets them check the validation, the `is_job_posting` check and the error-to-status-code mapping in about a second, with no API key and no quota.

## Design

- Only `app/llm.py` talks to Gemini. Everything else sees a `JobPosting` or one of two exceptions (`LLMBadOutput`, `LLMUnavailable`)
- The Gemini client is created on first use, so importing the app (and running the tests) does not need an API key
- The `JobPosting` schema is passed to Gemini as `response_schema`, and the same class is the API's response model
- Nullable fields and an `is_job_posting` flag give the model an honest way to say "not in the text" or "this is not a posting"
- The route is a plain `def`, not `async def`, because the Gemini call is synchronous

## Project layout

```
app/
  src/main.py          app, /health, router registration
  routers/extract.py   POST /llm/extract and error mapping
  llm.py               Gemini call (the only file that talks to Gemini)
  schemas.py           JobPosting, ExtractRequest
  tests/               pytest suite with a fake extractor
pytest.ini
requirements.txt
.env.example
```

## Known limitations

- The model decides what counts as a job posting, so edge cases (for example "X is not hiring...") depend on its judgment
- The tests use a fake extractor, so the logic inside `llm.py` (turning Gemini errors and unparseable output into the two exceptions) is not covered by automated tests
- The free tier has request limits, which show up as 503 responses
- No authentication, rate limiting or database