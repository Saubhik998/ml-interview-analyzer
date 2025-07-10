import google.generativeai as genai
from ..config import GEMINI_KEY

#  Configure API key globally before using the client
genai.configure(api_key=GEMINI_KEY)

#  Create the GenerativeModel instance after configuration
client = genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_next_question(jd: str, previous_question: str, answer: str) -> str:
    prompt = (
        f"You are an interviewer for the following job:\n\n"
        f"{jd}\n\n"
        f"The previous question was:\n\"{previous_question}\"\n\n"
        f"The candidate answered:\n\"{answer}\"\n\n"
        f"Based on this answer, ask the next relevant interview question, No extra explanation on why you chose this question and be more humane as possible."
    )

    response = client.generate_content(prompt)

    #  Extracting text from the response safely
    return response.text.strip() if hasattr(response, "text") else response.parts[0].text.strip()