import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64
import io
import openai
from dotenv import load_dotenv
from text_extraction import TextractExtractor, PDFMinerExtractor
from LLM import get_chatgpt_response, get_anthropic_response
import boto3
import logging
import os
#importing all the necessary libraries and python files
import secrets
import string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64
import io
import boto3
import logging
import os
import streamlit as st
import requests
import json
from dotenv import load_dotenv
import time
import openai
import uuid # to create random unique names for files
from prompts import AI_SUMMARY_PROMPT, EVALUATE_PROMPT, CLAUDE_AI_SUMMARY_PROMPT, CLAUDE_EVALUATE_PROMPT
#importing all the necessary libraries and python files
import boto3
import logging
import os
import streamlit as st
import requests
import json
from dotenv import load_dotenv
import time
import openai
import uuid # to create random unique names for files
from botocore.exceptions import BotoCoreError, ClientError
from text_extraction import TextractExtractor, PDFMinerExtractor
from LLM import get_chatgpt_response, get_anthropic_response
from prompts import AI_SUMMARY_PROMPT, EVALUATE_PROMPT, CLAUDE_AI_SUMMARY_PROMPT, CLAUDE_EVALUATE_PROMPT, PDFMINER_EVALUATE_PROMPT
from streamlit import session_state as state
from UI import TextFieldsManager
#from s3 import Input_PDF_or_Text_Processor
from text_extraction import TextractExtractor, PDFMinerExtractor

# # Input field for the user to enter a number
# user_input = st.number_input("Enter a number")

# # Initialize result with 0
# result = 0

# # Display the initial result in a text_area
# result_text_area = st.text_area("Looped text", result)

def preserve():
    st.session_state.hello

df = pd.DataFrame(np.random.randn(5, 3))
text_area = st.text_area("Enter a text", "", key = "lsfdnjbvwjnk")

"session_state object,", st.session_state

if st.toggle("hello"):
    # if user_input:
    # # Create a for loop to update and display the result
    #     for i in range(1, int(user_input) + 1):
    #         result = user_input * i
    #         result_text_area.text(f"Result after {i} iterations: {result}")

    bonjour = st.text_area("text", text_area, key ="skvsljsflshnihboil")

    hello = st.text_area("Enter 1st number", "", key="1234",on_change= preserve)
    hola = st.text_area("Enter 2nd number", "", key="456",on_change = preserve)
    namaste = st.text_area("Enter 3rd number", "", key="789", on_change = preserve)

    if hello and hola and namaste:
        try:
            hello = int(hello)
            hola = int(hola)
            namaste = int(namaste)
        except ValueError:
            st.write("Please enter valid integer values.")
    else:
        st.write("Please enter values in all three text areas.")

    data = [[hello, hola, namaste]]
    df2 = pd.DataFrame(data, columns=[0, 1, 2])
    df = pd.concat([df, df2], ignore_index=True)
    st.dataframe(df)

    # Function to convert DataFrame to PDF
    def _draw_as_table(df, pagesize):
        alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
        alternating_colors = alternating_colors[:len(df)]
        fig, ax = plt.subplots(figsize=pagesize)
        ax.axis('tight')
        ax.axis('off')
        the_table = ax.table(cellText=df.values,
                            rowLabels=df.index,
                            colLabels=df.columns,
                            rowColours=['lightblue'] * len(df),
                            colColours=['lightblue'] * len(df.columns),
                            cellColours=alternating_colors,
                            loc='center')
        return fig

    # Function to create PDF from DataFrame
    def dataframe_to_pdf(df, filename, numpages=(1, 1), pagesize=(11, 8.5)):
        with PdfPages(filename) as pdf:
            nh, nv = numpages
            rows_per_page = len(df) // nh
            cols_per_page = len(df.columns) // nv
            for i in range(0, nh):
                for j in range(0, nv):
                    page = df.iloc[(i * rows_per_page):min((i + 1) * rows_per_page, len(df)),
                                (j * cols_per_page):min((j + 1) * cols_per_page, len(df.columns))]
                    fig = _draw_as_table(page, pagesize)
                    if nh > 1 or nv > 1:
                        fig.text(0.5, 0.5 / pagesize[0],
                                "Part-{}x{}: Page-{}".format(i + 1, j + 1, i * nv + j + 1),
                                ha='center', fontsize=8)
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()

    # Streamlit app
    st.markdown("# Download DataFrame as PDF")
    st.dataframe(df)

    # Function to enable file download
    def get_binary_file_downloader_html(pdf_filename, pdf_bytes):
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f"<a href='data:application/pdf;base64,{b64}' download='{pdf_filename}'>Download PDF File</a>"
        return href

    if st.toggle("Generate PDF"):
        # Prompt user for PDF filename
        pdf_filename = st.text_input("Enter PDF filename (e.g., my_table.pdf)", "my_table.pdf")
        if st.toggle("Download PDF") and pdf_filename:
            # Generate PDF
            dataframe_to_pdf(df, pdf_filename)
            st.success(f"PDF '{pdf_filename}' generated successfully!")
            
            # Allow user to download the PDF
            with open(pdf_filename, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.markdown(get_binary_file_downloader_html(pdf_filename, pdf_bytes), unsafe_allow_html=True)




