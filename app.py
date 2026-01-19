import os
import json
import traceback
import streamlit as st
import PyPDF2
from langchain_ai21 import ChatAI21

api_key = os.environ.get("AI21_API_KEY")

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


def read_file(file_path: str):
    if file_path.endswith(".pdf"):
        try:
            text = ""
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            return text

        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise Exception(
            "Unsupported file format. Only PDF and TXT are supported.")


def get_table_data(quiz_str):
    """
    Converts a quiz JSON string into a list of dicts suitable for display in Streamlit.
    Options will appear on separate lines.
    """
    try:
        # Convert the quiz string to dictionary
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        for key, value in quiz_dict.items():
            mcq = value["mcq"]

            # Create choices as HTML line breaks
            options_html = "<br>".join(
                [f"{option} -> {option_value}" for option,
                    option_value in value["options"].items()]
            )

            correct = value["correct"]

            quiz_table_data.append({
                "MCQ": mcq,
                "Choices": options_html,
                "Correct": correct
            })

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False

# loading json file


RESPONSE_JSON = {
    "1": {
        "no": "1",
        "mcq": "multiple choice questions",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here"
        },

        "correct": "correct answer"
    },

    "2": {
        "no": "2",
        "mcq": "multiple choice questions",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here"
        },

        "correct": "correct answer"
    },

    "3": {
        "no": "3",
        "mcq": "multiple choice questions",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here"
        },

        "correct": "correct answer"
    }
}

# creating a title for the app
st.title("MCQs Generator")

# Create a form using st.form
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Upload a PDF or txt file")

    txt = st.text_area("Text content (alternative to file upload)")

    # Input Fields
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=10)

    # Subject
    subject = st.text_input("Subject Name", max_chars=30)

    # Quiz Tone
    tone = st.text_input("Complexity Level of Questions",
                         max_chars=30, placeholder="Simple")

    # Add Button
    button = st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input

    if button and (uploaded_file is not None or txt) and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = txt or read_file(uploaded_file)
                quiz_response = generate_quiz(
                    text, mcq_count, subject, tone, RESPONSE_JSON)
                review_response = review_quiz(subject, quiz_response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                if quiz_response is not None:
                    quiz_table_data = get_table_data(quiz_response)

                    if quiz_table_data is not None:
                        st.markdown("\n---")
                        for i, row in enumerate(quiz_table_data):
                            st.markdown(f"**Q{i+1}:** {row['MCQ']}")
                            st.markdown(
                                f"**Choices:**  \n{row['Choices']}", unsafe_allow_html=True)
                            st.markdown(
                                f"**Correct Answer:** {row['Correct']}")
                            st.markdown("\n")

                        # Display the review in a text box as well
                        st.markdown("---")
                        st.markdown("**Quiz Review:**\n" +
                                    review_response)

                    else:
                        st.error("Error in the table data")

                else:
                    st.write(quiz_response)
