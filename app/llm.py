from app.schemas import JobPosting
from google.genai import errors, types
from google import genai
from dotenv import load_dotenv
from app.schemas import JobPosting
from functools import lru_cache

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client()

config = types.GenerateContentConfig(
    system_instruction=(
        "Extract the job posting into the schema. Never invent facts that are not in the text. "
        "If the text is not a job posting, set is_job_posting to false "
        "and leave the other fields null or empty."
    ),
    response_mime_type="application/json",
    response_schema=JobPosting,
    max_output_tokens=20,
)


class LLMBadOutput(Exception):
    pass


class LLMUnavailable(Exception):
    pass


@lru_cache
def get_client():
    return genai.Client()


def extract_job_posting(text: str) -> JobPosting:
    try:
        response = client.models.generate_content(
            model=MODEL, contents=text, config=config
        )
    except errors.APIError as e:
        if e.code in (429, 500, 503):
            raise LLMUnavailable(str(e.message)) from e
        raise
    if response.parsed is None:
        raise LLMBadOutput(str(response.candidates[0].finish_reason))
    return response.parsed
