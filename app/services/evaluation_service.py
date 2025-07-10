import google.generativeai as genai
from ..config import GEMINI_KEY
import json
import re

# Configure Gemini API client
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # Or "gemini-pro"

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

    resp = model.generate_content(prompt)
    text = resp.text.strip()

    # Clean up code block formatting if present
    clean_json = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(clean_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from Gemini: {e}\n\nReceived:\n{text}")
