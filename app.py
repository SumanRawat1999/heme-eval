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
from botocore.exceptions import BotoCoreError, ClientError
import uuid # to create random unique names for files
from text_extraction import TextractExtractor, PDFMinerExtractor
from LLM import get_chatgpt_response
from prompts import AI_SUMMARY_PROMPT

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


# Code for UI
st.title("AI PARAMETER EXTRACTION EVALUATION")
uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)
text_extraction = st.multiselect("Select a text extraction tool",["Textract","PDFMiner"])
llm = st.multiselect("Select a LLM",["GPT-4", "Claude-2"])
submit = st.button("Submit")


# Uploading PDFs to S3
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


def main():
    if submit:
        with st.spinner("Loading"):

            # Call upload_pdf_to_s3 and get the folder_key and pdf_file.name
            folder_key, pdf_name = upload_pdf_to_s3(uploaded_files, s3_folder, bucket_name)
            
            # Construct the document_name for process_textract_extraction
            document_name = f"{folder_key}original/{pdf_name}"

            if "Textract" in text_extraction and "GPT-4" in llm:

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

                # Call to create an AI_SUMMARY response from GPT-4
                gpt_response = get_chatgpt_response(AI_SUMMARY_PROMPT,file_data)
                st.write(gpt_response)

            else:
            # Display an error message if one or both options are not selected
                st.error("Please select a text extraction tool and an LLM.")


            # elif text_extraction == "PDFMiner":
            #     pdfminer_extractor = PDFMinerExtractor()
            #     extracted_text = pdfminer_extractor.extract_text(bucket_name, document_name)
            #     st.write(extracted_text)
            #     string_to_file(extracted_text,"raw.txt")

    

if __name__ == "__main__":
    main()
