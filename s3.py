import boto3
import logging
import os
import streamlit as st
import time
import uuid
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

class Input_PDF_or_Text_Processor:
    def __init__(self):
        load_dotenv()
        self.aws_default_region = os.environ.get('AWS_DEFAULT_REGION')
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = 'heme-eval'
        self.s3_folder = 'first-eval/'

        self.s3 = boto3.client(
            service_name='s3',
            region_name=self.aws_default_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )


    def upload_pdf_to_s3(self, uploaded_files,s3_folder, bucket_name):
        if uploaded_files:
            for pdf_file in uploaded_files:
                try:
                    timestamp = int(time.time() * 1000)
                    random_number = str(uuid.uuid4().int & (1 << 31) - 1)
                    self.folder_key = f"{s3_folder}{timestamp}-{random_number}/"
                    self.pdf_name = self.pdf_file.name
                    self.s3.put_object(Bucket=bucket_name, Key=f"{self.folder_key}original/")
                    self.s3.upload_fileobj(pdf_file, bucket_name, f"{self.folder_key}original/{self.pdf_name}")
                    return self.folder_key, self.pdf_name
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


        Here, this function is used to:
        create a raw.txt file locally where the raw text extracted from Textract or user input text will be saved.
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

    
    def raw_file_folder_s3(self, uploaded_text):
        """ 
        This function is used to:
        1: Create a random number folder inside the S3 bucket. 
        2: Create a folder called raw.txt
        """
        if uploaded_text: 
            try:
                timestamp = int(time.time() * 1000)
                random_number = str(uuid.uuid4().int & (1 << 31) - 1)
                folder_key = f"{self.s3_folder}{timestamp}-{random_number}/"
                st.write(folder_key)
                self.s3.put_object(Bucket=self.bucket_name, Key=f"{folder_key}original/")
                return folder_key
            except Exception as e:
                st.error(f"Error uploading input text: {str(e)}")


    def upload_text_file_to_s3(self, folder_key):
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=f"{folder_key}raw_text/")
            self.s3.upload_file("raw.txt", self.bucket_name, f"{folder_key}raw_text/raw.txt")
            s3_file_name = f"{folder_key}raw_text/raw.txt"
            return s3_file_name
        except Exception as e:
            st.error(f'Error uploading file to S3: {e}')


    def read_file_from_s3(self,bucket, s3_file_name):
        """
        This function retrieves a file from an S3 bucket.

        Parameters:
        bucket (str): The name of the S3 bucket.
        s3_file_name (str): The name of the file in S3 bucket.

        Returns:
        str: The content of the file as a string.

        Here, this function is used to retrieve/ read files from S3. So used to read saved text from raw.txt
        """
        try:
            
            logger.debug(f"Connecting to S3 bucket: {bucket}")

            # Fetch the file from the specified S3 bucket
            response = self.s3.get_object(Bucket=bucket, Key=s3_file_name)
            
            # Read the file data and decode it
            file_data = response['Body'].read().decode('utf-8')
            
            logger.debug(f"Successfully read file: {s3_file_name} from bucket: {bucket}")

            return file_data

        except Exception as e:
            logger.exception(f"Failed to read file: {s3_file_name} from bucket: {bucket}. Error: {str(e)}")
            raise
