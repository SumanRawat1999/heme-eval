import streamlit as st

class TextFieldsManager:
    def __init__(self):
        self.counter = 1
        self.user_input_list = []
        self.USER_EVALUATE_PROMPT_2 = ""


    def process(self):
        with st.expander('Select the process',expanded=True):
            self.input_type = st.selectbox("Please Choose the type of Input", ['', 'Upload a file', 'Input text'], key=f"123")
            if 'Upload a file' in self.input_type:
                self.text_extraction = st.multiselect('Select a text extraction tool', ['Textract', 'PDFMiner'],max_selections=1, key=f"234")
                
                self.llm = st.multiselect('Select an LLM', ['GPT-4', 'Claude-2'],max_selections=1, key=f"345")

                self.USER_EVALUATE_PROMPT_1 = st.text_area("Enter the prompt for post-process output here", "", height=100, key=f"456")

            elif 'Input text' in self.input_type:
                self.llm = st.multiselect('Select an LLM', ['GPT-4', 'Claude-2'],max_selections=1, key=f"678")

                self.USER_EVALUATE_PROMPT_1 = st.text_area("Enter the prompt here", "", height=100, key=f"789")
            
        return self.input_type

    def add_text_fields(self):
        self.user_input = {}

        if 'Upload a file' in self.input_type:
            col1,col2,col3 = st.columns([3,3,3])
            with col1.expander('Input',expanded=True):
                self.user_input['uploaded_files'] = st.file_uploader("Upload PDF Files", type=['pdf', 'png', 'jpg'], accept_multiple_files=True, key=f"Enter Text {self.counter}")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")

            with col2.expander('Gold standard',expanded=True):
                self.user_input['gold_std'] = st.text_area('Gold standard output', '', height=200, key=f"Enter Text {self.counter + 1}")
            
            with col3.expander('Human Evaluation',expanded=True):
                self.user_input['human_eval'] = st.text_area('Human Evaluation', '', height=200, key=f"Enter Text {self.counter + 2}")
                self.user_input['text_extraction'] = self.text_extraction

                    
            
        if 'Input text'in self.input_type:
            col4,col5,col6 = st.columns([3,3,3])
            with col4.expander('Input',expanded=True):
                self.user_input['uploaded_text'] = st.text_area('Enter the text to be evaluated here', '', height=200, key=f"Enter Text {self.counter + 3}")

            with col5.expander('Gold standard',expanded=True):
                self.user_input['gold_std'] = st.text_area('Gold standard output', '', height=200, key=f"Enter Text {self.counter + 4}")

            with col6.expander('Human Evaluation',expanded=True):
                self.user_input['human_eval'] = st.text_area('Human Evaluation', '', height=200, key=f"Enter Text {self.counter + 5}")
        
        self.user_input['llm'] = self.llm
        self.user_input['user_prompt_1'] = self.USER_EVALUATE_PROMPT_1
        self.user_input['user_prompt_2'] = self.USER_EVALUATE_PROMPT_2

        return self.user_input
        


    def run(self):

        col6, col7, col8 = st.columns(3)

        col7.title("Generic Evaluation")

        self.process()

        submit = False  # Initialize submit with a default value

        if self.input_type in ['Upload a file','Input text']:
            st.subheader("", divider='rainbow') 
            upload_counter = 1
            st.subheader(f'Upload {upload_counter}')   
            user_input_dict = self.add_text_fields()
            self.user_input_list.append(user_input_dict)
            
            
            self.counter += 6
            self.toggle_count=0
            if user_input_dict:
                while st.toggle("Add", key=f"Add Text Fields ({self.counter})"):
                    st.subheader("", divider='rainbow')
                    upload_counter += 1
                    st.subheader(f'Upload {upload_counter}')
                    user_input_dict = self.add_text_fields()
                    if user_input_dict:
                        self.toggle_count+=1
                    self.user_input_list.append(user_input_dict)
                    self.counter += 6

            
            st.subheader("", divider='rainbow')
            self.USER_EVALUATE_PROMPT_2 = st.text_area("Enter the prompt for evaluation here", "", height=100, key=f"890")
            for data in self.user_input_list:
                data['user_prompt_2'] = self.USER_EVALUATE_PROMPT_2
            # self.user_input['user_prompt_2'] = self.USER_EVALUATE_PROMPT_2
            #self.user_input_list.pop()
            submit = st.button("Submit")
        
        return submit, self.user_input_list
