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
from botocore.exceptions import BotoCoreError, ClientError
from text_extraction import TextractExtractor, PDFMinerExtractor
from LLM import get_chatgpt_response, get_anthropic_response
# from prompts import AI_SUMMARY_PROMPT, EVALUATE_PROMPT, CLAUDE_AI_SUMMARY_PROMPT, CLAUDE_EVALUATE_PROMPT, PDFMINER_EVALUATE_PROMPT
from streamlit import session_state as state
from UI import TextFieldsManager
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.tables import TableStyleValue


# Loading the variables from .env file
load_dotenv()

# Import openai api key
openai.api_key = os.environ["openai_api_key"]

# Set up logging
logger = logging.getLogger(__name__)

# Import aws credentials
aws_default_region = os.environ.get('AWS_DEFAULT_REGION')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

# AWS: Bucket name and key 
bucket_name = 'heme-eval'
s3_folder = 'first-eval/'

# Create an S3 client
s3 = boto3.client(service_name='s3',region_name=aws_default_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key)

st.set_page_config(layout="wide")


def upload_pdf_to_s3(uploaded_files, s3_folder, bucket_name):
    
    if uploaded_files:
        for pdf_file in uploaded_files:
            try:
                # Generate a unique folder name for each PDF file using a timestamp and a random number
                timestamp = int(time.time() * 1000)  # High-resolution timestamp
                random_number = str(uuid.uuid4().int & (1<<31) - 1)  # Random number
                folder_key = f"{s3_folder}{timestamp}-{random_number}/"
                pdf_name = pdf_file.name
                # Create the folder: "original" in S3
                s3.put_object(Bucket=bucket_name, Key=f"{folder_key}original/")
                # Upload the PDF file to the "original" folder
                s3.upload_fileobj(pdf_file, bucket_name, f"{folder_key}original/{pdf_file.name}")
                return folder_key, pdf_name
            
            except Exception as e:
                st.error(f"Error uploading {pdf_file.name}: {str(e)}")


def string_to_file(input_string, filename):
    """
    This function takes an input string and a filename, writes the input string into the file, 
    and handles exceptions that may occur during the file operation.
    
    Parameters:
    input_string (str): The string to write to the file.
    filename (str): The name of the file to write the string to.

    Returns:
    bool: True if successful in writing the string to the file, False otherwise.

    Raises:
    IOError: An error occurred accessing the file.
    Exception: An unexpected error occurred.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(input_string)
        return True
    except IOError as e:
        st.error(f"IO Error occurred: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error occurred: {str(e)}")
        return False


# Creating a file inside S3 bucket for text from UI
def raw_file_folder_s3(s3_folder, bucket_name):
    
    try:
        # Generate a unique folder name for each PDF file using a timestamp and a random number
        timestamp = int(time.time() * 1000)  # High-resolution timestamp
        random_number = str(uuid.uuid4().int & (1<<31) - 1)  # Random number
        folder_key = f"{s3_folder}{timestamp}-{random_number}/"
        #st.write(folder_key)
        # Create the folder: "original" in S3
        s3.put_object(Bucket=bucket_name, Key=f"{folder_key}original/")
        return folder_key
    
    except Exception as e:
        st.error(f"Error uploading: {str(e)}")


def upload_text_file_to_s3(bucket_name, folder_key):
    
    try:
        # Create the folder: "raw_text" in S3
        s3.put_object(Bucket=bucket_name, Key=f"{folder_key}raw_text/")
        # Upload the text file to the "raw_text" folder
        s3.upload_file("raw.txt", bucket_name, f"{folder_key}raw_text/raw.txt")
        s3_file_name = f"{folder_key}raw_text/raw.txt"
        return s3_file_name
    
    except Exception as e:
        st.error(f'Error uploading file to S3: {e}')


def read_file_from_s3(bucket, s3_file_name):
    """
    This function retrieves a file from an S3 bucket.

    Parameters:
    bucket (str): The name of the S3 bucket.
    s3_file_name (str): The name of the file in S3 bucket.

    Returns:
    str: The content of the file as a string.
    """
    try:
        
        logger.debug(f"Connecting to S3 bucket: {bucket}")

        # Fetch the file from the specified S3 bucket
        response = s3.get_object(Bucket=bucket, Key=s3_file_name)
        
        # Read the file data and decode it
        file_data = response['Body'].read().decode('utf-8')
        
        logger.debug(f"Successfully read file: {s3_file_name} from bucket: {bucket}")

        return file_data

    except Exception as e:
        logger.exception(f"Failed to read file: {s3_file_name} from bucket: {bucket}. Error: {str(e)}")
        raise


def generate_random_key(length):
    # Define the character set from which to generate the key
    character_set = string.ascii_letters + string.digits
    
    # Use secrets.choice to generate a random key of the specified length
    random_key = ''.join(secrets.choice(character_set) for _ in range(length))
    
    return random_key




















# ########################### VERSION 1: PDF generation ###############################################


# # Function to convert DataFrame to PDF
# def _draw_as_table(df, pagesize):
#     alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
#     alternating_colors = alternating_colors[:len(df)]
#     fig, ax = plt.subplots(figsize=pagesize)
#     ax.axis('tight')
#     ax.axis('off')
#     the_table = ax.table(cellText=df.values,
#                          rowLabels=df.index,
#                          colLabels=df.columns,
#                          rowColours=['lightblue'] * len(df),
#                          colColours=['lightblue'] * len(df.columns),
#                          cellColours=alternating_colors,
#                          cellLoc='left',
#                          loc='center')
#     return fig

# # Function to create PDF from DataFrame
# def dataframe_to_pdf(df, filename, numpages=(1, 1), pagesize=(11, 8.5)):
#     with PdfPages(filename) as pdf:
#         nh, nv = numpages
#         rows_per_page = len(df) // nh
#         cols_per_page = len(df.columns) // nv
#         for i in range(0, nh):
#             for j in range(0, nv):
#                 page = df.iloc[(i * rows_per_page):min((i + 1) * rows_per_page, len(df)),
#                                (j * cols_per_page):min((j + 1) * cols_per_page, len(df.columns))]
#                 fig = _draw_as_table(page, pagesize)
#                 if nh > 1 or nv > 1:
#                     fig.text(0.5, 0.5 / pagesize[0],
#                              "Part-{}x{}: Page-{}".format(i + 1, j + 1, i * nv + j + 1),
#                              ha='center', fontsize=8)
#                 pdf.savefig(fig, bbox_inches='tight')
#                 plt.close()


# Function to enable file download
def get_binary_file_downloader_html(pdf_filename, pdf_bytes):
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f"<a href='data:application/pdf;base64,{b64}' download='{pdf_filename}'>Download PDF File</a>"
    return href


#  #####################################################################################################




# Define a custom function to set the cell height based on the content length
def set_max_cell_height(val, max_height=300):
    if isinstance(val, str):
        return f'height: {max(len(val), max_height)}px'
    return ''


# Create a Streamlit download link for the PDF
# def download_link(pdf_data, filename):
#     st.markdown(
#         f'<a href="data:application/pdf;base64,{pdf_data}" download="{filename}">Click here to download the PDF</a>',
#         unsafe_allow_html=True,
#     )


def generate_pdf(data_frame, filename):
    # Use landscape page orientation and set page size to fit the table
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    elements = []

    # Convert the DataFrame to a list of lists
    data = [list(data_frame.columns)] + data_frame.values.tolist()

    # Calculate the width of the table based on the number of columns
    num_cols = len(data[0])
    col_width = doc.width / num_cols
    table = Table(data, colWidths=[col_width] * num_cols)

    # Define the table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # All cells center-aligned
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),  # Data row background color
        ('TEXTCOLOR', (0, 1), (-1, -1), (0, 0, 0)),  # Data row text color
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Gridlines
        ('WORDWRAP', (0, 1), (-1, -1)),  # Enable text wrapping in data rows
    ])
    table.setStyle(style)
    elements.append(table)

    # Build the PDF
    doc.build(elements)
















def main():
    text_fields_manager = TextFieldsManager()
    submit, user_input_list = text_fields_manager.run()
    
    if submit:
        with st.spinner("Loading"):
            # st.write(len(user_input_list))
            #st.write("------------------------------")
            # st.write("User Input Dictionaries:")
            # st.write(user_input_list)
            # for i, user_input_dict in enumerate(user_input_list):
            #     st.write(f"Upload {i + 1}:", user_input_dict)
            # st.write("------------------------------")
            # st.write("------------------------------")
            # num=1
            # for data in user_input_list:
            #     st.write(num)
            #     st.write(data["uploaded_files"])
            # #     st.write(data["uploaded_text"])
            #     st.write(data["text_extraction"])
            #     st.write(data["llm"])
            #     st.write(data["gold_std"])
            #     st.write(data["user_prompt_1"])
            #     num = num+1
                
            # st.write("*******************************")

            
            # Creating a dataframe
            data_list = []

            #num = 1
            for num, data in enumerate(user_input_list, start=1):
                response_data = {
                    "Input": None,
                    "Post process output": None,
                    "Gold standard output": None,
                    "LLM evaluation": None,
                    "Human Eval": None
                }
                
                if "uploaded_files" in data and data["uploaded_files"]:

                    if "Textract" in data["text_extraction"] and "GPT-4" in data["llm"]:
                        folder_key, pdf_name = upload_pdf_to_s3(data["uploaded_files"], s3_folder, bucket_name)
                        # st.write("FOlder name: ",folder_key)
                        # st.write("PDF name: ",pdf_name)
                        # Construct the document_name for process_textract_extraction
                        document_name = f"{folder_key}original/{pdf_name}"

                        #counter = 1
                        # Call to extract text from PDF using Textract
                        text_extractor = TextractExtractor()
                        extracted_text = text_extractor.get_raw_text_list(bucket_name, document_name)
                        extracted_text = str(extracted_text)

                        # Call to save all the extracted text from PDF to "raw.txt" locally
                        string_to_file(extracted_text,"raw.txt")

                        # Call to upload the "raw.txt" file to S3
                        s3_file_name = upload_text_file_to_s3(bucket_name,folder_key)
                        raw_text_path = f"{folder_key}raw_text/raw.txt"

                        # Call to read the "raw.txt" file from the folder: "raw_text" in S3
                        file_data = read_file_from_s3(bucket_name,raw_text_path)

                        # Call to create "post process output" from LLM
                        eval_response_1 = get_chatgpt_response(data["user_prompt_1"],file_data)

                        # Call to create an evaluation based on prompt_2 from LLM
                        input_parameters = f"extracted parameters: {eval_response_1}/nstandard parameters: {data['gold_std']}"
                        eval_response_2 = get_chatgpt_response(data["user_prompt_2"], input_parameters)

                        col1,col2,col3,col4,col5 = st.columns(5)
                        with col1:
                            input_text = st.text_area(f"Input {num}", extracted_text, height=200, key=f"Text counter {generate_random_key(11)}")
                        with col2:
                            ai_summary = st.text_area(f"Post process output {num}", eval_response_1, height=200, key=f"Text counter {generate_random_key(12)}")
                        with col3:
                            gold_parameters = st.text_area(f"Gold standard output {num}", data["gold_std"], height=200, key=f"Text counter {generate_random_key(13)}")
                        with col4:
                            llm_eval = st.text_area(f"LLM evaluation {num}", eval_response_2, height=200, key=f"Text counter {generate_random_key(14)}")
                        with col5:
                            human_eval = st.text_area(f"Human Eval {num}", data["human_eval"], height=200, key=f"Text counter {generate_random_key(15)}")                  
                        


                    if "Textract" in data["text_extraction"] and "Claude-2" in data["llm"]:      
                        folder_key, pdf_name = upload_pdf_to_s3(data["uploaded_files"], s3_folder, bucket_name)
                        # st.write("FOlder name: ",folder_key)
                        # st.write("PDF name: ",pdf_name)
                        # Construct the document_name for process_textract_extraction
                        document_name = f"{folder_key}original/{pdf_name}"

                        # Call to extract text from PDF using Textract
                        text_extractor = TextractExtractor()
                        extracted_text = text_extractor.get_raw_text_list(bucket_name, document_name)
                        extracted_text = str(extracted_text)

                        # Call to save all the extracted text from PDF to "raw.txt" locally
                        string_to_file(extracted_text,"raw.txt")

                        # Call to upload the "raw.txt" file to S3
                        s3_file_name = upload_text_file_to_s3(bucket_name,folder_key)
                        raw_text_path = f"{folder_key}raw_text/raw.txt"

                        # Call to read the "raw.txt" file from the folder: "raw_text" in S3
                        file_data = read_file_from_s3(bucket_name,raw_text_path)

                        # Call to create "post process output" from LLM
                        eval_response_1 = get_anthropic_response(data["user_prompt_1"],file_data)

                        # Call to create an evaluation based on prompt_2 from LLM
                        input_parameters = f"extracted parameters: {eval_response_1}/nstandard parameters: {data['gold_std']}"
                        eval_response_2 = get_anthropic_response(data["user_prompt_2"], input_parameters)
                        
                        col1,col2,col3,col4,col5 = st.columns(5)
                        with col1:
                            input_text = st.text_area(f"Input {num}", extracted_text, height=200, key=f"Text counter {generate_random_key(11)}")
                        with col2:
                            ai_summary = st.text_area(f"Post process output {num}", eval_response_1, height=200, key=f"Text counter {generate_random_key(12)}")
                        with col3:
                            gold_parameters = st.text_area(f"Gold standard output {num}", data["gold_std"], height=200, key=f"Text counter {generate_random_key(13)}")
                        with col4:
                            llm_eval = st.text_area(f"LLM evaluation {num}", eval_response_2, height=200, key=f"Text counter {generate_random_key(14)}")
                        with col5:
                            human_eval = st.text_area(f"Human Eval {num}", data["human_eval"], height=200, key=f"Text counter {generate_random_key(15)}")



                    if "PDFMiner" in data["text_extraction"] and "GPT-4" in data["llm"]:
                            folder_key, pdf_name = upload_pdf_to_s3(data["uploaded_files"], s3_folder, bucket_name)
                            # st.write("FOlder name: ",folder_key)
                            # st.write("PDF name: ",pdf_name)
                            # Construct the document_name for process_textract_extraction
                            document_name = f"{folder_key}original/{pdf_name}"


                            # Call to extract text from PDF using Textract
                            text_extractor = PDFMinerExtractor()
                            extracted_text = text_extractor.extract_text(bucket_name, document_name)
                            extracted_text = str(extracted_text)

                            # Call to save all the extracted text from PDF to "raw.txt" locally
                            string_to_file(extracted_text,"raw.txt")

                            # Call to upload the "raw.txt" file to S3
                            s3_file_name = upload_text_file_to_s3(bucket_name,folder_key)
                            raw_text_path = f"{folder_key}raw_text/raw.txt"

                            # Call to read the "raw.txt" file from the folder: "raw_text" in S3
                            file_data = read_file_from_s3(bucket_name,raw_text_path)

                            # Call to create "post process output" from LLM
                            eval_response_1 = get_chatgpt_response(data["user_prompt_1"],file_data)

                            # Call to create an evaluation based on prompt_2 from LLM
                            input_parameters = f"extracted parameters: {eval_response_1}/nstandard parameters: {data['gold_std']}"
                            eval_response_2 = get_chatgpt_response(data["user_prompt_2"], input_parameters)
                                
                            col1,col2,col3,col4,col5 = st.columns(5)
                            with col1:
                                input_text = st.text_area(f"Input {num}", extracted_text, height=200, key=f"Text counter {generate_random_key(11)}")
                            with col2:
                                ai_summary = st.text_area(f"Post process output {num}", eval_response_1, height=200, key=f"Text counter {generate_random_key(12)}")                   
                            with col3:
                                gold_parameters = st.text_area(f"Gold standard output {num}", data["gold_std"], height=200, key=f"Text counter {generate_random_key(13)}")
                            with col4:
                                llm_eval = st.text_area(f"LLM evaluation {num}", eval_response_2, height=200, key=f"Text counter {generate_random_key(14)}")
                            with col5:
                                human_eval = st.text_area(f"Human Eval {num}", data["human_eval"], height=200, key=f"Text counter {generate_random_key(15)}")



                    if "PDFMiner" in data["text_extraction"] and "Claude-2" in data["llm"]:     
                        folder_key, pdf_name = upload_pdf_to_s3(data["uploaded_files"], s3_folder, bucket_name)
                        # st.write("FOlder name: ",folder_key)
                        # st.write("PDF name: ",pdf_name)
                        # Construct the document_name for process_textract_extraction
                        document_name = f"{folder_key}original/{pdf_name}"


                        # Call to extract text from PDF using Textract
                        text_extractor = PDFMinerExtractor()
                        extracted_text = text_extractor.extract_text(bucket_name, document_name)
                        extracted_text = str(extracted_text)

                        # Call to save all the extracted text from PDF to "raw.txt" locally
                        string_to_file(extracted_text,"raw.txt")

                        # Call to upload the "raw.txt" file to S3
                        s3_file_name = upload_text_file_to_s3(bucket_name,folder_key)
                        raw_text_path = f"{folder_key}raw_text/raw.txt"

                        # Call to read the "raw.txt" file from the folder: "raw_text" in S3
                        file_data = read_file_from_s3(bucket_name,raw_text_path)

                        # Call to create "post process output" from LLM
                        eval_response_1 = get_anthropic_response(data["user_prompt_1"],file_data)

                        # Call to create an evaluation based on prompt_2 from LLM
                        input_parameters = f"extracted parameters: {eval_response_1}/nstandard parameters: {data['gold_std']}"
                        eval_response_2 = get_anthropic_response(data["user_prompt_2"], input_parameters)

                        col1,col2,col3,col4,col5 = st.columns(5)
                        with col1:
                            input_text = st.text_area(f"Input {num}", extracted_text, height=200, key=f"Text counter {generate_random_key(11)}")
                        with col2:
                            ai_summary = st.text_area(f"Post process output {num}", eval_response_1, height=200, key=f"Text counter {generate_random_key(12)}")
                        with col3:
                            gold_parameters = st.text_area(f"Gold standard output {num}", data["gold_std"], height=200, key=f"Text counter {generate_random_key(13)}")
                        with col4:
                            llm_eval = st.text_area(f"LLM evaluation {num}", eval_response_2, height=200, key=f"Text counter {generate_random_key(14)}")
                        with col5:
                            human_eval = st.text_area(f"Human Eval {num}", data["human_eval"], height=200, key=f"Text counter {generate_random_key(15)}")




                if "uploaded_text" in data and data["uploaded_text"]:
                    # folder_key= raw_file_folder_s3(s3_folder, bucket_name)
                    # #st.write("FOlder name: ",folder_key)

                    if "GPT-4" in data["llm"]:
                        folder_key= raw_file_folder_s3(s3_folder, bucket_name)
                        # st.write("FOlder name : ",folder_key)


                        # Call to save all the extracted text from PDF to "raw.txt" locally
                        string_to_file(data["uploaded_text"],"raw.txt")

                        # Call to upload the "raw.txt" file to S3
                        s3_file_name = upload_text_file_to_s3(bucket_name,folder_key)
                        raw_text_path = f"{folder_key}raw_text/raw.txt"

                        # Call to read the "raw.txt" file from the folder: "raw_text" in S3
                        file_data = read_file_from_s3(bucket_name,raw_text_path)

                        # Call to create "post process output" from LLM
                        eval_response_1 = get_chatgpt_response(data["user_prompt_1"],file_data)

                        # Call to create an evaluation based on prompt_2 from LLM
                        input_parameters = f"extracted parameters: {eval_response_1}/nstandard parameters: {data['gold_std']}"
                        eval_response_2 = get_chatgpt_response(data["user_prompt_2"], input_parameters)

                        col1,col2,col3,col4,col5 = st.columns(5)
                        with col1:
                            input_text = st.text_area(f"Input {num}", data["uploaded_text"], height=200, key=f"Text counter {generate_random_key(11)}")
                        with col2:
                            ai_summary = st.text_area(f"Post process output {num}", eval_response_1, height=200, key=f"Text counter {generate_random_key(12)}")
                        with col3:
                            gold_parameters = st.text_area(f"Gold standard output {num}", data["gold_std"], height=200, key=f"Text counter {generate_random_key(13)}")
                        with col4:
                            llm_eval = st.text_area(f"LLM evaluation {num}", eval_response_2, height=200, key=f"Text counter {generate_random_key(14)}")
                        with col5:
                            human_eval = st.text_area(f"Human Eval {num}", data["human_eval"], height=200, key=f"Text counter {generate_random_key(15)}")




                    if "Claude-2" in data["llm"]:
                        folder_key= raw_file_folder_s3(s3_folder, bucket_name)
                        # st.write("FOlder name : ",folder_key)

                        # Call to save all the extracted text from PDF to "raw.txt" locally
                        string_to_file(data["uploaded_text"],"raw.txt")

                        # Call to upload the "raw.txt" file to S3
                        s3_file_name = upload_text_file_to_s3(bucket_name,folder_key)
                        raw_text_path = f"{folder_key}raw_text/raw.txt"

                        # Call to read the "raw.txt" file from the folder: "raw_text" in S3
                        file_data = read_file_from_s3(bucket_name,raw_text_path)

                        # Call to create "post process output" from LLM
                        eval_response_1 = get_anthropic_response(data["user_prompt_1"],file_data)

                        # Call to create an evaluation based on prompt_2 from LLM
                        input_parameters = f"extracted parameters: {eval_response_1}/nstandard parameters: {data['gold_std']}"
                        eval_response_2 = get_anthropic_response(data["user_prompt_2"], input_parameters)

                        col1,col2,col3,col4,col5 = st.columns(5)
                        with col1:
                            input_text = st.text_area(f"Input {num}", data["uploaded_text"], height=200, key=f"Text counter {generate_random_key(11)}")
                        with col2:
                            ai_summary = st.text_area(f"Post process output {num}", eval_response_1, height=200, key=f"Text counter {generate_random_key(12)}")
                        with col3:
                            gold_parameters = st.text_area(f"Gold standard output {num}", data["gold_std"], height=200, key=f"Text counter {generate_random_key(13)}")
                        with col4:
                            llm_eval = st.text_area(f"LLM evaluation {num}", eval_response_2, height=200, key=f"Text counter {generate_random_key(14)}")
                        with col5:
                            human_eval = st.text_area(f"Human Eval {num}", data["human_eval"], height=200, key=f"Text counter {generate_random_key(15)}")



                # Update the response_data dictionary with the processed data
                response_data["Input"] = input_text
                response_data["Post process output"] = ai_summary
                response_data["Gold standard output"] = gold_parameters
                response_data["LLM evaluation"] = llm_eval
                response_data["Human Eval"] = human_eval

                # Append the dictionary to the data list
                data_list.append(response_data)


            # Create a pandas DataFrame from the list of dictionaries
            df = pd.DataFrame(data_list)

            # Reset the index to start from 1 instead of 0
            df.index = range(1, len(df) + 1)

            custom_css = f"""
            <style>
            table th {{
                text-align: center !important;
            }}
            table td {{
                text-align: justify !important;
                white-space: normal !important;
                vertical-align: top !important;
                {df.applymap(set_max_cell_height).to_html(classes='col-1', escape=False)}
            }}
            </style>
            """

            # Apply the custom CSS
            st.markdown(custom_css, unsafe_allow_html=True)

            st.table(df)

            # Save the PDF and provide the download link
            pdf_filename = "data_table.pdf"
            generate_pdf(df, pdf_filename)
            with open(pdf_filename, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.markdown(get_binary_file_downloader_html(pdf_filename, pdf_bytes), unsafe_allow_html=True)



            

























            # ######################### PDF Generation: version 1 #############################
            
            # # Generate the PDF
            # pdf_filename = "output.pdf"
            # dataframe_to_pdf(df, pdf_filename)

            # # Trigger the download of the PDF
            # with open(pdf_filename, "rb") as pdf_file:
            #     pdf_bytes = pdf_file.read()
            #     st.markdown(get_binary_file_downloader_html(pdf_filename, pdf_bytes), unsafe_allow_html=True)
         



    
if __name__ == "__main__":
    main()
