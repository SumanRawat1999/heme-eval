AI_SUMMARY_PROMPT_2 = """"
    1. You are an `Experienced Doctor`.
    2. Your task is to extract all the parameters, their values and reference ranges from the given `pathology laboratory test report` - without losing any vital information.
    3. DO NOT extract any personal information from the given text content.
    4. You will be provided with a pathology laboratory test report.
    5. Give a response in the following format:
    parameter name: parameter value with unit and reference range,
    parameter name: parameter value with unit and reference range,...
    6. Do not make mistakes in format, return the response exactly as per the above format.
    7. only consider valid pathology laboratory test parameters their values and reference ranges, do not take other fields.
    8. Do not return the patient's name, doctor's name, lab name, address or any personal information in your response.
    9. Give me every parameter one line after the other in a numerical series.
    """


AI_SUMMARY_PROMPT = """"
    1. You are an `Experienced Doctor`.
    2. Your task is to extract all the parameters, their values and reference ranges from the given `pathology laboratory test report` - without losing any vital information.
    3. DO NOT extract any personal information from the given text content.
    4. You will be provided with a pathology laboratory test report.
    5. Give a response in the following format:
    parameter name: parameter value with unit and reference range,
    parameter name: parameter value with unit and reference range,...
    6. Do not make mistakes in format, return the response exactly as per the above format.
    7. only consider valid pathology laboratory test parameters their values and reference ranges, do not take other fields.
    8. Do not return the patient's name, doctor's name, lab name, address or any personal information in your response.
    9. Give me every parameter one line after the other in a numerical series.
    10. Note that the parameter's result can either be numerical or text or both, which could be in form of abbreviation or text in capital letters. So, if under result i.e. after colon (:) if there is any data, include that as a parameter. 
    """


EVALUATE_PROMPT_1 = """"
Compare every single parameters from `standard parameters` and `extracted parameters`.
"""

EVALUATE_PROMPT_3 = """
Give me the following:
• Count of total number of parameters there in the `standard parameters` 
• Count of total number of parameters there in the `extracted parameters`
• Count of the `missing parameters`, i.e., `standard parameters` which are not there in `extracted parameters`
• From `standard parameters`, I want you to give me `missing parameters` which are not there in `extracted parameters`

Follow this format for giving me the answers to the above:
1. Count of the total number of standard parameters with the parameters: (like count, each parameter in numerical format as 1,2,3) Also, give an explanation for the number of count
2. Count of the total number of extracted parameters with the parameters: (like count, each parameter in numerical format as 1,2,3) Also, give an explanation for the number of count
3. Count of the total number of missing parameters:
4. A list of all the missing parameters: (If there are no missing parameters then give the answer as "None")
"""

#(textract + GPT)
EVALUATE_PROMPT_4 = """ 
NOTE: `missing parameters` are only parameters of `standard parameters` which are not there in `extracted parameters` and not the other way around. 

Now, give me an answer in this format for the following:
1. The total count of the number of standard parameters: (the count should be a total sum of every single parameters from `standard parameters` only)
2. The total count of the number of extracted parameters: (the count should be a total sum of every single parameters from `extracted parameters` only)
3. The total count of the number of missing parameters: (Find the sum of all the `missing parameters` compare and tell me the  parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
4. A list of all the missing parameters: (To find the list of all the `missing parameters` compare and tell me the  parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
"""

EVALUATE_PROMPT = """ 
NOTE: `missing parameters` are only parameters of `standard parameters` which are not there in `extracted parameters` and not the other way around. 

Now, give me an answer in this format for the following:
1. The total count of the number of standard parameters: (the count should be a total sum of every single parameters from `standard parameters` only)
2. The total count of the number of extracted parameters: (the count should be a total sum of every single parameters from `extracted parameters` which are also a part of `standard parameters`)
3. The total count of the number of missing parameters: (Find the count that is sum of all the `missing parameters` which are all the parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
4. A list of all the missing parameters: (To find the list of all the `missing parameters` compare and tell me the  parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
"""

PDFMINER_EVALUATE_PROMPT = """ 
NOTE: `missing parameters` are only parameters of `standard parameters` which are not there in `extracted parameters` and not the other way around. 

Now, give me an answer in this format for the following:
1. The total count of the number of standard parameters: (the count should be a total sum of every single parameters from `standard parameters` only)
2. The total count of the number of extracted parameters: (it should be a total count of sum of every single parameters from `extracted parameters` which are MUST also a part of `standard parameters`and nothing unecessary)
3. The total count of the number of missing parameters: (Find the sum of all the `missing parameters` compare and tell me only those parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
4. A list of all the missing parameters: (To find the list of all the `missing parameters` compare and tell me the  ONLY those parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
"""




CLAUDE_AI_SUMMARY_PROMPT_1 = """"
1. You are an `Experienced Doctor`.
2. Your task is to extract all the parameters, their values and reference ranges from the given `pathology laboratory test report` - without losing any vital information in the same order as the given text.
    3. DO NOT extract any personal information from the given text content.
    4. You will be provided with a pathology laboratory test report.
    5. Give a response in the following format:
    parameter name: parameter value with unit and reference range,
    parameter name: parameter value with unit and reference range,...
    6. Do not make mistakes in format, return the response exactly as per the above format.
    7. only consider valid pathology laboratory test parameters their values and reference ranges, do not take other fields.
    8. Do not return the patient's name, doctor's name, lab name, address or any personal information in your response.
    9. Give me every parameter one line after the other in a numerical series.
    10. Note that the parameter's result can either be numerical or text or both. So, if under result i.e. after colon (:) if there is any data, include that as a parameter.
    """


CLAUDE_AI_SUMMARY_PROMPT = """"
    1. You are an `Experienced Doctor`.
    2. Your task is to extract all the parameters, their values and reference ranges from the given `pathology laboratory test report` in the same order as text - without losing any vital information in the same order as the given text.
    3. DO NOT extract any personal information from the given text content.
    4. You will be provided with a pathology laboratory test report.
    5. Give a response in the following format only, no other information:
        1. parameter name: parameter value with unit and reference range: (give reference range),
        2. parameter name: parameter value with unit and reference range: (give reference range),
        3. parameter name: parameter value with unit and reference range: (give reference range),...
    6. Do not make mistakes in format, return the response exactly as per the above format.
    7. Only consider valid pathology laboratory test parameters their values and reference ranges, do not take other fields.
    8. Do not return the patient's name, doctor's name, lab name, address or any personal information in your response.
    9. Give me every parameter one line after the other in a numerical series as shown in the format here.
    10. Note that the parameter's result can either be numerical data or text data or both. So, if under result i.e. after colon (:) if there is any data, include that as a parameter but nothing unecessary.
    """

CLAUDE_EVALUATE_PROMPT_1 = """
Note that: `missing parameters` are only `standard parameters` which are not there in `extracted parameters` and not the opposite. 
So, let's say, `extracted parameters` has more parameters than `standard parameters` that extra parameters will not be considered but on the other hand,
if `standard parameters` has more parameter(s) than `extracted parameters` then, it will be considered as `missing parameters`


Now, give me an answer in this format for the following:
1. The total count of the number of standard parameters: (the count should be a total sum of every single parameters from `standard parameters`only)
2. The total count of the number of extracted parameters: (the count should be a total sum of every single parameters from `extracted parameters`only)
3. The total count of the number of missing parameters:
4. A list of all the missing parameters: (If there are no missing parameters then give the answer as "None")
"""


CLAUDE_EVALUATE_PROMPT = """ 
NOTE: `missing parameters` are only parameters of `standard parameters` which are not there in `extracted parameters` and not the other way around.
i.e., make sure you DO NOT include paramters of `extracted parameters` which are not there in `standard parameters`.

Now, give me an answer in this format for the following:
1. The total count of the number of standard parameters: (the count should be a total sum of every single parameters from `standard parameters` only)
2. The total count of the number of extracted parameters: (the count should be a total sum of every single parameters from `extracted parameters` only)
3. The total count of the number of missing parameters: (Find the sum of all the `missing parameters` compare and tell me the  parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
4. A list of all the missing parameters: (To find the list of all the `missing parameters` compare and tell me the  parameter(s) of `standard parameters` which are not there in `extracted parameters`. 
If there are no missing parameters then give the answer as "NA")
"""
