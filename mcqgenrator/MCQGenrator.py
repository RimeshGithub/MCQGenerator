import json
from langchain_ai21 import ChatAI21
from dotenv import load_dotenv
import os

# from mcqgenrator.utils import read_file


load_dotenv()  # loads .env into environment
api_key = os.getenv("AI21_API_KEY")

# -------- QUIZ GENERATION FUNCTION --------


def generate_quiz(text, number, subject, tone, response_json):
    prompt = f"""
Text:
{text}

You are an expert MCQ maker. Given the above text, create a quiz of {number}
multiple choice questions for {subject} students in a {tone} tone.

Rules:
- Questions must NOT be repeated
- Questions must strictly come from the text
- Create exactly {number} MCQs

Format your response exactly like this JSON:

{json.dumps(response_json, indent=2)}
"""
    response = ChatAI21(
        api_key=api_key,
        model="jamba-large",
        max_tokens=2000,
        temperature=0.3
    )

    return response.invoke(prompt).content


# -------- QUIZ REVIEW FUNCTION --------
def review_quiz(subject, quiz):
    prompt = f"""
You are an expert English grammarian and educator.

Given the following MCQs for {subject} students:
- Analyze the complexity (max 50 words)
- Check clarity and student understanding
- Suggest improvements if needed
- Adjust tone to student level

Quiz:
{quiz}

Expert Review:
"""
    response = ChatAI21(
        api_key=api_key,
        model="jamba-mini",
        max_tokens=500,
        temperature=0.3
    )

    return response.invoke(prompt).content


# -------- RUN PIPELINE --------
# response_json_format = {
#     "1": {
#         "question": "",
#         "options": {
#             "a": "",
#             "b": "",
#             "c": "",
#             "d": ""
#         },
#         "answer": ""
#     }
# }

# quiz = generate_quiz(
#     text=read_file("test.txt"),
#     number=3,
#     subject="Data Science",
#     tone="hard",
#     response_json=response_json_format
# )

# review = review_quiz(
#     subject="Data Science",
#     quiz=quiz
# )

# print("QUIZ OUTPUT:\n", quiz)
# print("\nREVIEW OUTPUT:\n", review)
