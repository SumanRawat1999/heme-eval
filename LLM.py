import os
import streamlit as st
import openai
from anthropic import Anthropic,HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
from prompts import AI_SUMMARY_PROMPT

load_dotenv()

#import openai and anthropic api key
openai.api_key = os.environ["openai_api_key"]
anthropic_api_key = os.environ["anthropic_api_key"]

def get_chatgpt_response(AI_SUMMARY_PROMPT,input_text):
    """
    Fetches a response from the GPT-4 model using OpenAI's ChatCompletion.
    
    Args:
    - pre_text (str): The user's input text.

    Returns:
    - str: The model's response.
    """
    
    try:
        gpt4_res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": AI_SUMMARY_PROMPT},
                {"role": "user", "content": input_text}
            ],
            temperature=0
        )
        
        return gpt4_res["choices"][0]["message"]["content"]

    except openai.error.OpenAIError as api_error:
        st.error(f"Error during OpenAI API call: {api_error}")
        return ""
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ""
    
def get_anthropic_response(AI_SUMMARY_PROMPT, input_text):
    final_prompt = f"{AI_SUMMARY_PROMPT}/n{input_text}"
    # Initialize Anthropic client
    anthropic = Anthropic(api_key=anthropic_api_key)

    # Create a completion
    completion = anthropic.completions.create(temperature=0,
        model="claude-2",
        max_tokens_to_sample=2000,
        prompt=f"{HUMAN_PROMPT} {final_prompt} {AI_PROMPT}",
    )
    
    # Return the completion text
    return completion.completion