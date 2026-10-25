from fastapi import APIRouter, Depends, HTTPException, status
from app.llm import LLMBadOutput, LLMUnavailable, extract_job_posting

from app.schemas import ExtractRequest, JobPosting

router = APIRouter()


def get_extractor():
    return extract_job_posting


@router.post("/extract", response_model=JobPosting)
def extract(request: ExtractRequest, extractor=Depends(get_extractor)):
    try:
        result = extractor(request.text)

    except LLMUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Temmporarily unavailable, retry later!",
        )

    except LLMBadOutput:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model returned unusuable output!",
        )

    if not result.is_job_posting:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Text is not a job posting!",
        )
    return result
