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
st.title("MCQs Creator Application with LangChain ⛓️")

# Create a form using st.form
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Uplaod a PDF or txt file")

    # Input Fields
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)

    # Subject
    subject = st.text_input("Insert Subject", max_chars=20)

    # Quiz Tone
    tone = st.text_input("Complexity Level Of Questions",
                         max_chars=20, placeholder="Simple")

    # Add Button
    button = st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                quiz_response = generate_quiz(
                    text, mcq_count, subject, tone, json.dumps(RESPONSE_JSON))
                review_response = review_quiz(subject, quiz_response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                if isinstance(quiz_response, dict):
                    # Extract the quiz data from the response
                    if quiz_response is not None:
                        table_data = get_table_data(quiz_response)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index+1
                            st.table(df)
                            # Display the review in atext box as well
                            st.text_area(label="Review",
                                         value=review_response)
                        else:
                            st.error("Error in the table data")

                else:
                    st.write(quiz_response)
