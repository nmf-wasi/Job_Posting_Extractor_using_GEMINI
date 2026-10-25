from app.llm import LLMUnavailable, LLMBadOutput
from app.schemas import JobPosting


def test_valid_posting(client, use_fake):
    def fake(text):
        return JobPosting(
            is_job_posting=True,
            title="ML Engineer",
            company="Kakao",
            location="Seoul",
            required_skills=["PyTorch"],
            years_experience=3,
            visa_sponsorship="unclear",
        )

    use_fake(fake)

    response = client.post("/llm/extract", json={"text": "anything"})
    assert response.status_code == 200
    assert response.json()["company"] == "Kakao"


def test_llm_unavailable_returns_503(client, use_fake):
    def fake(text):
        raise LLMUnavailable("quota")

    use_fake(fake)
    response = client.post("/llm/extract", json={"text": "anything"})
    assert response.status_code == 503


def make_posting(**overrirdes):
    """make_posting() gives a valid posting, and make_posting(is_job_posting=False) gives the same one with one field changed. (If you added remote, put it in data.)"""
    data = dict(
        is_job_posting=True,
        title="ML Engineer",
        company="Kakao",
        location="Seoul",
        required_skills=["PyTorch"],
        years_experience=3,
        visa_sponsorship="unclear",
    )

    data.update(overrirdes)
    return JobPosting(**data)


def test_not_a_job_posting(client, use_fake):
    def fake(text):
        return make_posting(
            is_job_posting=False,
            title="",
            company=None,
            location=None,
            require_skills=[],
            years_experience=None,
        )

    use_fake(fake)
    response = client.post("/llm/extract", json={"text": "anything"})
    assert response.status_code == 422


def test_bad_llm_output(client, use_fake):
    """The model returns unusable output, so the API returns 502"""

    def fake(text):
        raise LLMBadOutput("MAX_TOKENS")

    use_fake(fake)

    response = client.post("/llm/extract", json={"text": "anything"})
    assert response.status_code == 502


def test_empty_text_returns_422(client):
    """Empty text returns 422, with no fake"""
    response = client.post("/llm/extract", json={"text": ""})
    assert response.status_code == 422


def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
