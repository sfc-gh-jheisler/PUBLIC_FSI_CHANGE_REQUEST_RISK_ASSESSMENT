Site
Skip to main content
HomeStreamlit Apps
Selection deleted
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
import streamlit as st
import pandas as pd
import json5 as json
from snowflake.cortex import Complete
from snowflake.snowpark.functions import col, call_udf
from snowflake.snowpark.context import get_active_session

#st.image("https://png.pngtree.com/png-clipart/20231007/ourmid/pngtree-beautiful-flying-atlantic-canary-transparent-background-png-image_10196203.png", width = 100)
st.title("Change Request Risk Assessment")
#get a session
session = get_active_session()

def generate_risk_prediction_prompt(cr_data):
    prompt = f"""
            <role>
            You are an experienced dev ops professional deeply knowledgeable on computer systems that support a very large company and the metadata that is captured about change requests.
            A change request is a formal proposal for an alteration to the computer system that you manage.
            As a dev ops expert, you specialize in using the metadata provided about a change request to predict the liklihood of the change request unintentionally destabalizing the computer system.
            You are going to be provided with change request meta data as a json object held between <cr_data> and your job is to provide a prediction score and reasoning behind the risk score in the <output> section. 
            </role>
        
            <task>: Follow these instructions,
            1) Considering the <cr_data> and your <role>, provide a risk score between 0 to 5 of this change request destabalizing the computer system when deployed. do not exhibit a bias toward high risk. base your risk score only on the data you have been provided. if there is not enough information, please indicate this. Output this as [Risk_Score]. Then,
            2) Considering the <cr_data> and your <role>, provide a reasoning for the risk score in as few words as possible while maintaining all detail needed to understand your reasoning. Output this as [Risk_Score_Reason]
            </task>

            <cr_data>
            {cr_data}
            </cr_data>
        
            <Output> 
            produce valid JSON. Absolutely do not include any additional text before or following the JSON. Output should use following <JSON_format>
            </Output>
            
            <JSON_format>
            {{
                "Risk_Score": (A risk score between 0 to 5 of this change request destabalizing the computer system when deployed),
                "Risk_Score_Reason": (A concise resoning for the Risk_Score),
            }}
            </JSON_format>
            """
    return prompt


#replace this with your table
database = 'GEN_AI'
schema = 'PUBLIC'
table = 'ChangeRequests'

#get the data into pandas
cr_df = session.table(f"{database}.{schema}.{table}")

#Get the user's input
cr_request = st.selectbox('Select a change request', cr_df)

#USER INPUT: select model
df_models = pd.DataFrame(['snowflake-arctic', 'mistral-large', 'mistral-large2', 'reka-flash', 'reka-core',
                   'jamba-instruct', 'jamba-1.5-mini', 'jamba-1.5-large', 'mixtral-8x7b', 
                   'llama2-70b-chat', 'llama3-8b', 'llama3-70b', 'llama3.1-8b', 'llama3.1-70b',
                   'llama3.1-405b', 'llama3.2-1b', 'llama3.2-3b', 'mistral-7b', 'gemma-7b'], 
                  columns=['Model Name'])

user_input_model = st.selectbox("Select Model", df_models, key="CS_model_select_box")


df = session.table(f"{database}.{schema}.{table}").filter(col("CHANGENUMBER")  == cr_request).to_pandas()

if st.button("Run", type="primary"):
    #each row's columns are collapsed into a json object. that is easier to pass to the model
    #NOTICE: I am calling my generate_prompt function and passing my row as json.
    #NOTICE that I am calling complete function here (https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex)
        # VALUE CALLOUT: I could switch out any LLM I have access to (https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#availability)
    df['RISK_ASSESSMENT'] = df.apply(lambda row: Complete(user_input_model, generate_risk_prediction_prompt(row.to_json())), axis = 1)

    #show us the data
    
    try:
        json = json.loads(df.at[0, 'RISK_ASSESSMENT'])
    except ValueError:
        # Code to handle ValueError (if the input is not an integer)
        st.write(f"Whoops! {user_input_model}, the model you selected, did not produce valid output. Please select another model")
    else: 
        st.metric(label="Risk Score", value=json["Risk_Score"])
        st.write(json["Risk_Score_Reason"])
        st.subheader("Raw json")
        st.json(json)

