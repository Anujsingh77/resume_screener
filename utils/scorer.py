"""
Candidate scoring engine.
Combines skill overlap + TF-IDF similarity + experience heuristics.
"""

import re


def extract_experience_years(text: str) -> float:
    """Heuristically estimate years of experience from resume text."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return float(m.group(1))

    # count year spans like "2019 – 2023"
    spans = re.findall(r'\b(20\d\d|19\d\d)\b', text)
    if len(spans) >= 2:
        years = sorted([int(y) for y in spans])
        span = years[-1] - years[0]
        return float(min(span, 20))  # cap at 20
    return 0.0


def extract_education(text: str) -> str:
    """Detect highest education level."""
    text_lower = text.lower()
    if any(k in text_lower for k in ['ph.d', 'phd', 'doctorate']):
        return 'PhD'
    if any(k in text_lower for k in ["master's", 'masters', 'm.s.', 'mba', 'm.tech', 'me ']):
        return "Master's"
    if any(k in text_lower for k in ["bachelor's", 'bachelors', 'b.s.', 'b.e.', 'b.tech', 'b.sc']):
        return "Bachelor's"
    if 'diploma' in text_lower:
        return 'Diploma'
    return 'Not specified'


def score_candidate(
    name: str,
    resume_text: str,
    resume_skills: list,
    jd_skills: list,
    tfidf_score: float
) -> dict:
    """
    Compute a 0-100 score and generate reasoning for a candidate.

    Weights:
      - Skill overlap  : 50%
      - TF-IDF cosine  : 35%
      - Experience     : 15%
    """
    # ── Skill overlap ──────────────────────────────────────────────────────
    if jd_skills:
        matched = [s for s in resume_skills if s in jd_skills]
        missing = [s for s in jd_skills if s not in resume_skills]
        skill_ratio = len(matched) / len(jd_skills)
    else:
        matched = resume_skills[:10]
        missing = []
        skill_ratio = 0.5  # neutral if JD has no detectable skills

    skill_score = skill_ratio * 100  # 0-100

    # ── TF-IDF similarity ──────────────────────────────────────────────────
    tfidf_component = tfidf_score * 100  # 0-100

    # ── Experience heuristic ───────────────────────────────────────────────
    exp_years = extract_experience_years(resume_text)
    # normalize: 5+ years → full score
    exp_score = min(exp_years / 5.0, 1.0) * 100

    # ── Weighted total ─────────────────────────────────────────────────────
    total = (skill_score * 0.50) + (tfidf_component * 0.35) + (exp_score * 0.15)
    total = round(min(max(total, 0), 100))

    # ── Verdict ────────────────────────────────────────────────────────────
    if total >= 75:
        verdict = "Strong fit"
    elif total >= 55:
        verdict = "Good fit"
    elif total >= 35:
        verdict = "Partial fit"
    else:
        verdict = "Weak fit"

    # ── Reasoning ──────────────────────────────────────────────────────────
    strengths = []
    gaps = []

    if matched:
        strengths.append(f"Matches {len(matched)} required skill(s): {', '.join(matched[:5])}.")
    if tfidf_score > 0.3:
        strengths.append("Resume content closely aligns with the job description.")
    if exp_years >= 3:
        strengths.append(f"Has approximately {int(exp_years)} years of relevant experience.")

    if missing:
        gaps.append(f"Missing {len(missing)} skill(s): {', '.join(missing[:5])}.")
    if tfidf_score < 0.1:
        gaps.append("Low overall text similarity with job description.")
    if exp_years < 1:
        gaps.append("Limited or no detectable experience mentioned.")

    education = extract_education(resume_text)

    return {
        "name": name,
        "score": total,
        "verdict": verdict,
        "matched_skills": matched,
        "missing_skills": missing[:8],
        "experience_years": round(exp_years, 1),
        "education": education,
        "tfidf_similarity": round(tfidf_score * 100, 1),
        "skill_match_pct": round(skill_ratio * 100, 1),
        "strengths": " ".join(strengths) if strengths else "Candidate shows some relevant background.",
        "gaps": " ".join(gaps) if gaps else "No major gaps detected.",
    }
