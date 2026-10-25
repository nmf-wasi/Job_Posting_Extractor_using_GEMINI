from pydantic import BaseModel, Field
from typing import Literal


class JobPosting(BaseModel):
    is_job_posting: bool = Field(description="false if the text is not a job posting")
    title: str
    company: str | None = Field(description="null if not stated in the text")
    location: str | None = Field(description="null if not stated in the text")
    required_skills: list[str]
    years_experience: int | None = Field(description="null if not state in the text")
    visa_sponsorship: Literal["yes", "no", "unclear"]


class ExtractRequest(BaseModel):
    text:str=Field(min_length=1, max_length=10000)
    