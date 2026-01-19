import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from mcqgenrator.utils import read_file, get_table_data
import streamlit as st
from mcqgenrator.MCQGenrator import generate_quiz, review_quiz
from mcqgenrator.logger import logging

# loading json file

with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

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
