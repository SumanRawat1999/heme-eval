import streamlit as st

class TextFieldsManager:
    def __init__(self):
        self.counter = 1
        self.user_input_list = []


    def process(self):
        with st.expander('Select the process',expanded=True):
            self.input_type = st.selectbox("Please Choose the type of Input", ['', 'Upload a file', 'Input text'], key=f"123")
            if 'Upload a file' in self.input_type:
                self.text_extraction = st.multiselect('Select a text extraction tool', ['Textract', 'PDFMiner'],max_selections=1, key=f"234")
                # st.write("")
                # st.write("")
                
                self.llm = st.multiselect('Select an LLM', ['GPT-4', 'Claude-2'],max_selections=1, key=f"345")
                # st.write("")
                # st.write("")
                # st.write("")
                self.USER_EVALUATE_PROMPT_1 = st.text_area("Enter the prompt for post-process output here", "", height=100, key=f"456")
            elif 'Input text' in self.input_type:

                
                self.llm = st.multiselect('Select an LLM', ['GPT-4', 'Claude-2'],max_selections=1, key=f"678")
                # st.write("")
                # st.write("")
                # st.write("")
                self.USER_EVALUATE_PROMPT_1 = st.text_area("Enter the prompt here", "", height=100, key=f"789")
            # for data in self.user_input_list:
            #     data['user_prompt'] = USER_EVALUATE_PROMPT_1
            
        return self.input_type

    def add_text_fields(self):
        self.user_input = {}

        #input_type = st.selectbox("Please Choose the type of Input", ['', 'Upload a file', 'Input text'], key=f"input{self.counter}")

        if 'Upload a file' in self.input_type:
            col1,col2 = st.columns([3,3])
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
                self.user_input['text_extraction'] = self.text_extraction
                
            
        if 'Input text'in self.input_type:
            col3,col4 = st.columns([3,3])
            with col3.expander('Input',expanded=True):
                self.user_input['uploaded_text'] = st.text_area('Enter the text to be evaluated here', '', height=200, key=f"Enter Text {self.counter + 2}")

            with col4.expander('Gold standard',expanded=True):
                self.user_input['gold_std'] = st.text_area('Gold standard output', '', height=200, key=f"Enter Text {self.counter + 3}")
        
        self.user_input['llm'] = self.llm
        self.user_input['user_prompt'] = self.USER_EVALUATE_PROMPT_1

        return self.user_input
        


    def run(self):

        

        col6, col7, col8 = st.columns(3)

        col7.title("Generic Evaluation")

        self.process()

        if self.input_type in ['Upload a file','Input text']:
            st.subheader("", divider='rainbow') 
            upload_counter = 1
            st.subheader(f'Upload {upload_counter}')   
            user_input_dict = self.add_text_fields()
            self.user_input_list.append(user_input_dict)
            
            self.counter += 4

            if user_input_dict:
                while st.toggle("Add", key=f"Add Text Fields ({self.counter})"):
                    st.subheader("", divider='rainbow')
                    upload_counter += 1
                    st.subheader(f'Upload {upload_counter}')
                    user_input_dict = self.add_text_fields()
                    self.user_input_list.append(user_input_dict)
                    self.counter += 4

        # elif self.input_type in ['Input text']:
        #     st.subheader("", divider='rainbow') 
        #     upload_counter = 1
        #     st.subheader(f'Upload {upload_counter}')   

        #     user_input_dict = self.add_text_fields()
        #     self.user_input_list.append(user_input_dict)
        #     self.counter += 4

        #     if user_input_dict:
        #         while st.toggle("Add", key=f"Add Text Fields ({self.counter})"):
        #             st.subheader("", divider='rainbow')
        #             upload_counter += 1
        #             st.subheader(f'Upload {upload_counter}')
        #             user_input_dict = self.add_text_fields()
        #             self.user_input_list.append(user_input_dict)
        #             self.counter += 4
        
        st.subheader("", divider='rainbow')
        self.USER_EVALUATE_PROMPT_2 = st.text_area("Enter the prompt for evaluation here", "", height=100, key=f"890")
        # for data in self.user_input_list:
        #     data['user_prompt'] = USER_EVALUATE_PROMPT_2
        # self.user_input['USER_EVALUATE_PROMPT_2'] = self.USER_EVALUATE_PROMPT_2
        #self.user_input_list.pop()
        submit = st.button("Submit")
        
        return submit, self.user_input_list
