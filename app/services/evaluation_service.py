import google.generativeai as genai
from google import genai
from ..config import GEMINI_KEY
import json
import re

client=genai.Client(api_key=GEMINI_KEY)


def evaluate_interview(jd: str, questions: list[str], answers: list[str]) -> dict:
    prompt = f"""
    Based on the following job description, questions, and candidate answers, evaluate the candidate with and return a JSON with this exact format:

    {{
      "jd": string,
      "score": integer (0-100),
      "questions": list of strings,
      "answers": list of strings,
      "strengths": list of strings,
      "improvements": list of strings,
      "followUps": list of strings
    }}

    Job Description:
    {jd}

    Questions:
    {json.dumps(questions)}

    Answers:
    {json.dumps(answers)}
    """

    resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    text = resp.text.strip()

    # ✅ Remove ```json or other formatting artifacts
    clean_json = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(clean_json)
    except json.JSONDecodeError as e:
        # Fallback in case Gemini returns slightly broken JSON
        raise ValueError(f"Invalid JSON from Gemini: {e}\n\nReceived:\n{text}")
