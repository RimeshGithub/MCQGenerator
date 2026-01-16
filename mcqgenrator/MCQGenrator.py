import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv

from mcqgenrator.utils import read_file, get_table_data
from mcqgenrator.logger import logging

# LangChain imports
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

# Hugging Face LangChain LLM
from langchain_huggingface import HuggingFaceEndpoint

# Load environment variables
load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print("HF TOKEN loaded:", HF_TOKEN is not None)

# -------- LLM SETUP (Hugging Face) --------
llm = HuggingFaceEndpoint(
    repo_id="google/flan-t5-large",  # text2text model (BEST for instructions)
    task="text2text-generation",
    huggingfacehub_api_token=HF_TOKEN,
    temperature=0.3,
    max_new_tokens=512
)

# -------- QUIZ GENERATION PROMPT --------
quiz_template = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.

Make sure:
- Questions are NOT repeated
- Questions strictly conform to the text
- Exactly {number} MCQs are created

Format your response exactly like RESPONSE_JSON below.

### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=quiz_template
)

quiz_chain = LLMChain(
    llm=llm,
    prompt=quiz_generation_prompt,
    output_key="quiz",
    verbose=True
)

# -------- QUIZ REVIEW PROMPT --------
review_template = """
You are an expert English grammarian and writer.

Given a Multiple Choice Quiz for {subject} students:
- Analyze complexity (max 50 words)
- Check if students can understand the questions
- If not suitable, suggest improvements
- Adjust tone to match student ability

Quiz_MCQs:
{quiz}

Expert Review:
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=review_template
)

review_chain = LLMChain(
    llm=llm,
    prompt=quiz_evaluation_prompt,
    output_key="review",
    verbose=True
)

# -------- SEQUENTIAL CHAIN --------
generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True
)

response = generate_evaluate_chain({
    "text": "Artificial Intelligence is the simulation of human intelligence...",
    "number": 5,
    "subject": "Computer Science",
    "tone": "simple",
    "response_json": {
        "1": {
            "question": "",
            "options": {
                "a": "",
                "b": "",
                "c": "",
                "d": ""
            },
            "answer": ""
        }
    }
})

print(response["quiz"])
print(response["review"])
