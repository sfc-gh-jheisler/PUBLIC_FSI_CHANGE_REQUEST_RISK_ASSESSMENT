import streamlit as st
import json5 as json
import pandas as pd
from snowflake.snowpark.functions import col, call_udf
from snowflake.snowpark.context import get_active_session

# Page configuration
st.set_page_config(
    page_title="Change Request Risk Assessment",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add legend for risk score colors
st.sidebar.title('Risk Score Legend')

functionality = st.sidebar.selectbox('Select Functionlity', ("Summary", "Ad Hoc"))

legend_cols = st.sidebar.columns(3)
with legend_cols[0]:
    st.color_picker('Low Risk (0-1.9)', '#00FF00', disabled=True)
with legend_cols[1]:
    st.color_picker('Medium Risk (2-3.9)', '#FFFF00', disabled=True)
with legend_cols[2]:
    st.color_picker('High Risk (4-5)', '#FF0000', disabled=True)

if functionality == 'Summary':

###########################
##########SUMMARY##########
###########################
    # Custom CSS for elegant styling
    st.write("""
    <style>
        .stButton button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        div[data-testid="stDecoration"] {
            background-image: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session and get data
    session = get_active_session()
    database = 'GEN_AI_FSI'
    schema = 'DTCC_HACKATHON'
    table = 'CHANGE_REQUEST_RISK_INFERENCE'
    
    def color_risk_score(val):
        """
        Returns a color based on the risk score value:
        - Low risk (0-1.9): Green
        - Medium risk (2-3.9): Yellow
        - High risk (4-5): Red
        """
        if pd.isna(val):
            return ''
        
        # Normalize value between 0 and 1
        #
        
        # Create RGB values for gradient
        if val < 2: 
            r = 0 
            g = 255
            b = 0
        elif val >= 2 and val <4: #yellow
            r = 255
            g = 255
            b  = 0
        else:  # Red
            r = 255
            g = 0 
            b = 0
        
        return f'background-color: rgba({r}, {g}, {b}, 0.2)'
    
    @st.cache_data
    def load_data():
        df = session.table(f"{database}.{schema}.{table}").to_pandas()
        for i in range(len(df)):
            json_data = json.loads(df.at[i, 'RISK_ASSESSMENT'])
            df.at[i, 'RISK_SCORE_AI'] = json_data["Risk_Score"]
            df.at[i, 'RISK_REASON_AI'] = json_data["Risk_Score_Reason"]
        return df
    
    # Load data
    df = load_data()
    
    # Prepare display tables with styling
    display_table = df[['CHANGENUMBER', 'DATE', 'RISK_SCORE_AI', 'RISK_REASON_AI']]
    display_table_detail = df[['CHANGENUMBER', 'DESCRIPTION', 'DATE', 'IMPACT', 
                              'PRIORITY', 'RISK', 'JUSTIFICATION', 'STATE', 
                              'DISPOSITION', 'CATEGORY', 'RISK_SCORE_AI', 'RISK_REASON_AI']]
    
    # App header
    st.title('Risk Assessment Dashboard')
    
    # Add some basic metrics
    st.subheader('Key Metrics')
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        avg_risk = df['RISK_SCORE_AI'].mean()
        st.metric('Average Risk Score', f'{avg_risk:.2f}')
    
    with metric_col2:
        high_risk_count = len(df[df['RISK_SCORE_AI'] > 3])
        st.metric('High Risk Changes', high_risk_count)
    
    with metric_col3:
        total_changes = len(df)
        st.metric('Total Changes', total_changes)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    title = 'Risk Assessment Summary'
    
    st.subheader(title)
    show_details = st.button('Show Detailed View', use_container_width=True)
        
    # Show detailed view if button is clicked
    if show_details:
        title = 'Detailed Risk Assessment'
        st.dataframe(
            display_table_detail.style.applymap(
                color_risk_score,
                subset=['RISK_SCORE_AI']
            ),
            use_container_width=True,
            hide_index=True,
            height=400
    )
    else: 
        st.dataframe(
            display_table.style.applymap(
                color_risk_score,
                subset=['RISK_SCORE_AI']
            ),
            use_container_width=True,
            hide_index=True,
            height=400
        )

else:
##########################
##########AD HOC##########
##########################

    # Custom CSS to enhance the UI
    st.markdown("""
        <style>
        .risk-score {
            font-size: 24px;
            font-weight: bold;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Header with gradient background
    st.title("Change Request Risk Assessment")
    
    # Initialize session
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
                    1) Considering the <cr_data>, <meta_data>, and your <role>, provide a risk score between 0 to 5 of this change request destabalizing the computer system when deployed. do not exhibit a bias toward high risk. base your risk score only on the data you have been provided. if there is not enough information, please indicate this. Output this as [Risk_Score]. Then,
                    2) Considering the <cr_data>, <meta_data>, and your <role>, provide a reasoning for the risk score in as few words as possible while maintaining all detail needed to understand your reasoning. Output this as [Risk_Score_Reason]
                </task>
    
                <meta_data>
                    The folowing is the metadata for the cr_data. the metatdata follows this format: (column_name: data_type : description : sample_values):
                    
                    (Description: VARCHAR(16777216) : A summary of the change : ''Upgrade to the existing DataSync API from version 3.2 to 3.4 in the Production environment. The update includes several key performance optimizations, enhanced security features, and bug fixes that address issues with data consistency and processing time.
                    The major components of this change include:
                    
                    API Version Update: Migrating from DataSync API v3.2 to v3.4 to support faster data ingestion and processing.
                    Security Enhancements: Implementation of OAuth 2.0-based authentication to replace the legacy basic authentication mechanism, improving overall security for API transactions.
                    Error Handling: Enhanced error codes and more descriptive responses for improved debugging in the event of failure.
                    Database Schema Update: Modifications to the backend MySQL database to accommodate new data types introduced in version 3.4.
                    Testing will be performed in the staging environment (v3.4-Stage) before deployment to ensure backwards compatibility with existing systems. No downtime is expected during the deployment, but a rollback plan has been prepared in case of critical issues.'',)
                       
                    (Date: DATE : The date the request was made : 2025-02-03)
                    
                    (Impact: VARCHAR(4000) : How the change will affect the project, including cost, quality, risk, scope, duration, and schedule)
                    
                    (Priority: VARCHAR(400) : How quickly the change should be approved and implemented : ''immediately'', ''within release window'', ''after approval'')
                    
                    (Risk: VARCHAR(400) : The risk level of the change as described by development team : ''low risk'', ''moderate risk'', ''high risk'')
                    
                    (Justification: VARCHAR(4000) : The reason for the change : ''preventative maintenance'', ''patch'', ''planned release as part of project koala'')
                    
                    (State: VARCHAR(400) : The status of the change request : ''new'', ''under review'', ''approved'', ''deferred'', ''rejected'')
                    
                    (Disposition: VARCHAR(400) : An explanation for approved, deferred, or rejected changes : ''no peer review'', ''manager override'', ''uniform agreement'')
                    
                    (Category: VARCHAR(400) : The category of the change : ''planned'', ''unplanned'', ''emergency'')
                    
                    (Change number: VARCHAR(100) : A unique ID for tracking the request :''AB1672'', ''723CS'', ''6D62EE'')
                </meta_data>
                
                <cr_data>
                    {cr_data}
                </cr_data>
            
                <Output> 
                    produce valid JSON. Absolutely do not include any additional text before or following the JSON. Output should use following <JSON_format>
                </Output>
                
                <JSON_format>
                {{
                    "Risk_Score": (A risk score between 0 to 5 of this change request destabalizing the computer system when deployed),
                    "Risk_Score_Reason": (A concise resoning for the Risk_Score and any suggestions to mitigate),
                }}
                </JSON_format>
                """
        return prompt
    
    def my_complete(model, context, temp=0, max_tokens: int = 18000):
        sql = F"""SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model}',
                [
                    {{
                        'role': 'user',
                        'content': '{context}'
                    }}
                ],
                {{
                    'max_tokens': {max_tokens}, 
                    'temperature' : {temp} 
                }}
            ) as inference;"""
        inference_raw = session.sql(sql).to_pandas().loc[0,"INFERENCE"]
        inference_json = json.loads(inference_raw)
        inference_raw = inference_json['choices'][0]['messages']
        return inference_raw
    
    # Database configuration
    database = 'GEN_AI_FSI'
    schema = 'DTCC_HACKATHON'
    table = 'CHANGE_REQUEST_RAW'
    history_table = 'CHANGE_REQUEST_RISK_INFERENCE'
    
    # Get the data into pandas
    cr_df = session.table(f"{database}.{schema}.{table}")
    
    # Create two columns for the input section
    col1, col2 = st.columns(2)
    
    with col1:
        #st.markdown('<div class="info-box">', unsafe_allow_html=True)
        cr_request = st.selectbox(
            'Select a Change Request',
            cr_df,
            help="Choose the change request you want to analyze"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        #st.markdown('<div class="info-box">', unsafe_allow_html=True)
        # Available models
        models = [
            'claude-3-5-sonnet', 'snowflake-arctic', 'mistral-large',
            'mistral-large2', 'reka-flash', 'reka-core', 'jamba-instruct',
            'jamba-1.5-mini', 'jamba-1.5-large', 'mixtral-8x7b',
            'llama2-70b-chat', 'llama3-8b', 'llama3-70b', 'llama3.1-8b',
            'llama3.1-70b', 'llama3.3-70b', 'snowflake-llama-3.3-70b',
            'llama3.1-405b', 'snowflake-llama-3.1-405b', 'llama3.2-1b',
            'llama3.2-3b', 'mistral-7b', 'gemma-7b'
        ]
        
        user_input_model = st.selectbox(
            "Select AI Model",
            models,
            help="Choose the AI model for risk assessment",
            key="CS_model_select_box"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a loading spinner
    with st.spinner("Analyzing risk..."):
        df = session.table(f"{database}.{schema}.{table}").filter(col("CHANGENUMBER") == cr_request).to_pandas()
        
        if st.button("Analyze Risk", type="primary"):
            try:
                df['RISK_ASSESSMENT'] = df.apply(
                    lambda row: my_complete(user_input_model, generate_risk_prediction_prompt(row.to_json())),
                    axis=1
                )
                
                json_data = json.loads(df.at[0, 'RISK_ASSESSMENT'])
                
                # Create three columns for the results
                result_col1, result_col2, result_col3 = st.columns([1,2,1])
                
                with result_col1:
                    #st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    # Color code the risk score
                    risk_score = float(json_data["Risk_Score"])
                    color = "green" if risk_score <= 2 else "orange" if risk_score <= 3.5 else "red"
                    st.markdown(f'<div class="risk-score" style="background-color: {color}; color: white;">'
                              f'Risk Score: {risk_score}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with result_col2:
                    #st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.subheader("Risk Assessment")
                    st.write(json_data["Risk_Score_Reason"])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with result_col3:
                    with st.expander("View Raw JSON"):
                    #if st.button("View Raw JSON"):
                        st.json(json_data)
    
            except ValueError as e:
                st.error(f"Error: {user_input_model} did not produce valid output. Please select another model.")
                st.exception(e)
            except Exception as e:
                st.error("An unexpected error occurred. Please try again.")
                st.exception(e)



# Add footer
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Change Request Risk Assessment Tool v1.0</p>
    </div>
""", unsafe_allow_html=True)