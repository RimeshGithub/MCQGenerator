import os
import PyPDF2
import json
import traceback


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
