"""Build a scoring profile from the resume.

The curated taxonomy gives every PM-relevant keyword a base weight. If the same
keyword also appears in the resume, its weight is boosted — so the profile adapts
automatically when the resume is updated (it is re-read on every run).
"""
import os

from resume_reader import read_resume_text

CURATED = {
    "skills": {
        "product management": 3, "product strategy": 3, "roadmap": 3, "product owner": 3,
        "backlog": 2, "prioriti": 2, "agile": 2, "scrum": 2, "stakeholder": 2,
        "go-to-market": 2, "gtm": 2, "a/b test": 2, "experimentation": 2, "analytics": 2,
        "kpi": 1, "metrics": 1, "user research": 2, "prd": 2, "requirement": 1,
        "product development": 3, "product lifecycle": 2, "discovery": 1, "wireframe": 1,
    },
    "domains": {
        "fintech": 3, "financial services": 2, "banking": 2, "payments": 2, "cards": 2,
        "lending": 2, "nbfc": 2, "insurance": 1,
        "telematics": 3, "gps": 2, "saas": 2, "platform": 1,
        "ai": 2, "genai": 3, "gen ai": 3, "llm": 3, "rag": 3, "agentic": 3,
        "machine learning": 2, "ml": 1, "data product": 3, "data analytics": 2,
    },
}


def build_profile(resume_path: str) -> dict:
    text = read_resume_text(resume_path).lower() if resume_path else ""
    keywords = {}
    for group in ("skills", "domains"):
        for kw, weight in CURATED[group].items():
            boost = 1 if (text and kw in text) else 0
            keywords[kw] = weight + boost
    return {"keywords": keywords, "resume_present": bool(text)}
