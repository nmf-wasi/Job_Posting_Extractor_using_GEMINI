#  test of the whole idea

from typing import Literal
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client()


class JobPosting(BaseModel):
    is_job_posting: bool = Field(description="false if the text is not a job posting")
    title: str
    company: str | None = Field(description="null if not stated in the text")
    location: str | None = Field(description="null if not stated in the text")
    required_skills: list[str]
    years_experience: int | None = Field(description="null if not state in the text")
    visa_sponsorship: Literal["yes", "no", "unclear"]


config = types.GenerateContentConfig(
    system_instruction="Extract the job posting into the schema. Never invent facts that are not in the text.",
    response_mime_type="application/json",
    response_schema=JobPosting,
    max_output_tokens=20,
)


def extract(text):
    response = client.models.generate_content(model=MODEL, contents=text, config=config)

    if response.parsed is None:
        print(
            "[WARN] could not parse. finsih_reason: ",
            response.candidates[0].finish_reason,
        )
        print(f"raw text: {response.text}")
        return None
    return response.parsed


postings = [
    "Notion is hiring a Junior Backend Engineer in Dublin. Python, FastAPI, SQL required. 1+ years experience. We sponsor work visas.",
    "ML Engineer at Kakao, Seoul. PyTorch and NLP experience essential, 3 years minimum.",
    "Startup looking for a developer, remote. Must know JavaScript.",
    "What's the capital of London?",
]


for p in postings:
    result = extract(p)
    print(type(result))
    print(result)
    print()
