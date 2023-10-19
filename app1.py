#importing all the necessary libraries and python files
import streamlit as st
from UI import TextFieldsManager
from s3 import Input_PDF_or_Text_Processor
from text_extraction import TextractExtractor, PDFMinerExtractor

st.set_page_config(layout="wide")

bucket_name = 'heme-eval'
s3_folder = 'first-eval/'

def main():
    text_fields_manager = TextFieldsManager()
    submit, user_input_list = text_fields_manager.run()

    if submit:
        with st.spinner("Loading"):
            # st.write(user_input_list)
            st.write("------------------------------")
            st.write("User Input Dictionaries:")
            # for i, user_input_dict in enumerate(user_input_list):
            #     st.write(f"Upload {i + 1}:", user_input_dict)
            # st.write("------------------------------")
            # st.write("------------------------------")
            # num=1
            # for data in user_input_list:
            #     st.write(num)
            #     st.write(data["uploaded_files"])
            #     st.write(data["text_extraction"])
            #     st.write(data["llm"])
            #     st.write(data["gold_std"])
            #     num = num+1
                
            st.write("*******************************")
            input_processor = Input_PDF_or_Text_Processor()
            # folder_key, pdf_name, bucket_name, s3_folder = input_processor.upload_pdf_to_s3(data["uploaded_files"])

            # st.write("Bucket name: ", bucket_name, s3_folder)
            # st.write("Bucket name: ", s3_folder)
            #input_to_s3.upload_pdf_to_s3(data["uploaded_files"], s3_folder, bucket_name)

            # for data in user_input_list:
            #     input_processor = Input_PDF_or_Text_Processor()  # Create an instance of Input_PDF_or_Text_Processor
            #     folder_key, pdf_name, bucket_name, s3_folder = input_processor.upload_pdf_to_s3(data["uploaded_files"])
            #     st.write("Bucket name: ", bucket_name, s3_folder)
            #     st.write("Bucket name: ", s3_folder)
            for data in user_input_list:
                if "uploaded_files" in data and data["uploaded_files"]:
                    folder_key, pdf_name= input_processor.upload_pdf_to_s3(data["uploaded_files"], s3_folder, bucket_name)
                    st.write("folder_key: ", folder_key)
                    st.write("Bucket name: ", pdf_name)
                else:
                    st.error("No uploaded files found in data.")




    #extracted_text = text_extractor.get_raw_text_list(bucket_name, document_name)




    
if __name__ == "__main__":
    main()
