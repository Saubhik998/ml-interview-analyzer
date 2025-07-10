import google.generativeai as genai
from ..config import GEMINI_KEY

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_first_question(jd: str) -> str:
    prompt = f"""
You are an expert technical interviewer.

Based on the following job description, ask the **first** interview question to a candidate.

Only return the question. No numbering. No formatting. No extra explanation.

Job Description:
\"\"\"{jd}\"\"\"


"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error generating first question:", e)
        return "Could you briefly introduce yourself?"