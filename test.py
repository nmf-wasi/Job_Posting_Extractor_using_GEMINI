from app.llm import extract_job_posting

print(
    extract_job_posting(
        "ML Engineer at Kakao, Seoul. PyTorch and NLP essential, 3 years minimum."
    )
)
