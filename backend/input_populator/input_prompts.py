"""
Prompt templates and LLM calling functions for TML analysis and extraction.
"""

import json
import os
from anthropic import Anthropic
import openai
import google.generativeai as genai


def call_llm_for_analysis(system_prompt: str, user_prompt: str, llm_provider: str = "claude") -> str:
    """
    Call LLM for analysis.
    
    Args:
        system_prompt: System prompt/instructions
        user_prompt: User prompt with data to analyze
        llm_provider: LLM provider ("claude", "openai", or "gemini")
        
    Returns:
        LLM analysis response
    """
    if llm_provider.lower() == "claude":
        return call_claude_for_analysis(system_prompt, user_prompt)
    elif llm_provider.lower() == "openai":
        return call_openai_for_analysis(system_prompt, user_prompt)
    elif llm_provider.lower() == "gemini":
        return call_gemini_for_analysis(system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def call_claude_for_analysis(system_prompt: str, user_prompt: str) -> str:
    """Call Claude for analysis."""
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        raise ValueError("CLAUDE_API_KEY environment variable not set")
    
    client = Anthropic(api_key=api_key)
    
    try:
        print("🤖 Calling Claude for analysis...")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=64000,
            temperature=0.7,
            stream=True,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        
        # Handle streaming response
        full_response = ""
        for chunk in response:
            if chunk.type == "content_block_delta":
                full_response += chunk.delta.text
        
        return full_response
    except Exception as e:
        print(f"❌ Error calling Claude: {e}")
        raise


def call_openai_for_analysis(system_prompt: str, user_prompt: str) -> str:
    """Call OpenAI GPT for analysis."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        print("🤖 Calling OpenAI for analysis...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.7,
            max_tokens=16000,
            stream=True
        )
        
        # Handle streaming response
        full_response = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        
        return full_response
    except Exception as e:
        print(f"❌ Error calling OpenAI: {e}")
        raise


def call_gemini_for_analysis(system_prompt: str, user_prompt: str) -> str:
    """Call Google Gemini for analysis."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    try:
        print("🤖 Calling Gemini for analysis...")
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        raise


def get_kpi_extraction_prompt(extracted_json: dict) -> tuple[str, str]:
    """
    Get the system and user prompts for KPI extraction from extracted visualization JSON.
    
    Args:
        extracted_json: The extracted visualization JSON data
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = """
    You are an expert business intelligence analyst specializing in dashboard analysis and KPI identification.
    Analyze the extracted visualization data to identify the most critical business metrics and KPIs that would be valuable for analysis and reporting.
    Focus on metrics that directly impact business performance and decision-making.
    """
    
    # Convert JSON to string safely to avoid f-string formatting issues
    extracted_json_str = json.dumps(extracted_json, indent=2)
    
    user_prompt = """

ROLE
You are an expert data analyst specializing in business intelligence and KPI extraction.

OBJECTIVE
Your task is to analyze a JSON object containing metadata about data visualizations. Your goal is to identify and rank the most important measures, and from those, extract the top 10 Key Performance Indicators (KPIs).

DEFINITIONS
Measure: A quantifiable metric being analyzed. It can be a direct column (e.g., [Sales]) or a formula-based calculation (e.g., sum([Profit]) / sum([Sales])). The core measure is the column or formula being aggregated.

Filter: A condition applied to the data to narrow down the results. These are found in the answer_search_query.

Key Performance Indicator (KPI): A KPI is defined as a specific Measure combined with a unique set of non-date-based Filters.
* Different non-date filters on the same measure create different KPIs (e.g., "Sales for 'Electronics'" and "Sales for 'Furniture'" are two distinct KPIs).
* Different date-based filters on the same measure are considered part of the same KPI (e.g., "Sales for 'Electronics' last quarter" and "Sales for 'Electronics' this year" both map to the KPI "Sales for 'Electronics'").

STEP-BY-STEP INSTRUCTIONS

PHASE 1: IDENTIFY AND SCORE THE TOP MEASURES

1. Iterate Through Visualizations: Process each JSON object within the visualizations array of the provided data.
2. Identify Measures: For each visualization, identify all measures used. You will find them within the answer_search_query string (e.g., sum([Gross Sales]), count([Users])) and defined in the answer_formulas array.
3. Calculate a Score for Each Measure: Maintain a running score for every unique measure you identify. For each visualization a measure appears in, update its total score based on the chart_type:
    * If chart_type is 'KPI', add 10 points to the measure's score.
    * If chart_type is 'TABLE', add 7 points to the measure's score.
    * For any other chart_type (e.g., 'COLUMN', 'PIE'), add 3 points to the measure's score.
4. Determine Top 10 Measures: After processing all visualizations, rank all unique measures by their total calculated score in descending order. Select the top 10 measures from this ranked list.

PHASE 2: EXTRACT AND RANK THE TOP 10 KPIS

1. Re-scan for Top Measures: Go through the visualizations array again, but this time, only focus on visualizations that use one of the top 10 measures identified in Phase 1.
2. Extract and Normalize Filters: For each of these visualizations:
    * Analyze the answer_search_query to identify all filter conditions.
    * Crucially, ignore any filters that are date-based. You can identify these by looking for keywords like date, month, year, quarter, timestamp, or date-related functions.
    * The remaining non-date filters (e.g., [Category] = 'Electronics', [Status] != 'Cancelled') define the unique characteristic of the KPI.
3. Construct Unique KPIs: A unique KPI is formed by the combination of a top measure and its unique set of normalized (non-date) filters.
4. Rank and Select KPIs: Create a final list of all unique KPIs you have constructed. Rank this list based on the score of the underlying measure from Phase 1. Select the top 10 KPIs from this final ranked list.

OUTPUT FORMAT

Produce a single JSON object as the output. This object should contain one key, "top_10_kpis", which is an array of 10 JSON objects. Each object in the array represents a single KPI and must have the following structure:

{
  "top_10_kpis": [
    {
      "kpi_name": "",
      "measure": "",
      "formula": "",
      "filters": [
        "[Filter 1] = ''",
        "[Filter 2] = ''"
      ],
      "chart_type_source": "",
      "table_name": "",
      "table_id": "",
      "description": ""
    },
    {
      "kpi_name": "",
      "measure": "",
      "formula": "",
      "filters": [
        "[Filter 1] = ''",
        "[Filter 2] = ''"
      ],
      "chart_type_source": "",
      "table_name": "",
      "table_id": "",
      "description": ""
    }
  ]
}

FIELD EXPLANATIONS FOR THE OUTPUT:

kpi_name: A concise, human-readable name for the KPI. Generate this based on the measure, aggregation, and filters. DO NOT INCLUDE THE DATE FILTERS IN THE KPI NAME.
measure: The base measure name (e.g., [Gross Sales]).
formula: The full aggregated formula found in the search query (e.g., sum([Gross Sales])).
filters: An array of strings, where each string is a non-date filter applied to the measure. If there are no non-date filters, this should be an empty array [].
chart_type_source: The chart_type from a prominent visualization where this KPI was found (preferably 'KPI' or 'TABLE' if available).
table_name: The name of the table where this KPI was found (preferably 'GTM RevOps' if available).
table_id: The id of the table where this KPI was found (preferably 'GTM RevOps' if available).
description: A brief, auto-generated sentence describing what the KPI represents.
    

    Extracted Visualization Data:
    """ + extracted_json_str + """
    """
    
    return system_prompt, user_prompt

def get_goal_extraction_prompt(analysis_result: dict) -> tuple[str, str]:
    """
    Get the system and user prompts for goal extraction from analysis result.
    
    Args:
        analysis_result: The complete analysis result containing KPIs, attributes, etc.
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = """
    You are an expert business intelligence analyst specializing in goal identification and business objective analysis.
    Analyze the provided analysis result to identify the primary business goal that this dashboard serves.
    Provide a single, clear sentence that describes the main business objective or purpose of this dashboard.
    """
    
    # Convert JSON to string safely to avoid f-string formatting issues
    analysis_result_str = json.dumps(analysis_result, indent=2)
    
    user_prompt = """
ROLE
You are an expert business analyst specializing in goal identification and strategic objective analysis.

OBJECTIVE
Your task is to analyze the provided dashboard analysis result (containing KPIs, attributes, and metadata) to identify the primary business goal that this dashboard is designed to support and measure.

ANALYSIS APPROACH
1. Examine the KPIs to understand what business metrics are being tracked
2. Look at the liveboard name and context to understand the business domain
3. Analyze the measures, formulas, and filters to identify the main business process being monitored
4. Consider the overall theme and purpose of the dashboard
5. If you identify KPIs from a specific industry, use your world knowledge to understand the business goal.

OUTPUT FORMAT
Provide a single, clear sentence that describes the main business goal or objective of this dashboard.

Example outputs:
- "Track and optimize marketing campaign performance to drive customer acquisition and revenue growth."
- "Monitor sales pipeline health and booking performance to achieve quarterly revenue targets."
- "Measure customer support efficiency and satisfaction to improve service quality."

Do not include JSON, bullet points, or complex formatting. Just provide one clear sentence that captures the primary business goal.

Analysis Result Data:
""" + analysis_result_str + """
"""
    
    return system_prompt, user_prompt

def get_user_context_extraction_prompt(analysis_result: dict) -> tuple[str, str]:
    """
    Get the system and user prompts for user context extraction from analysis result.
    
    Args:
        analysis_result: The complete analysis result containing KPIs, attributes, etc.
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = """
    You are an expert business intelligence analyst specializing in understanding dashboard user context and target audience.
    Analyze the provided analysis result to identify who would be the primary users of this dashboard and in what context they would use it.
    Provide a single, clear sentence that describes the user context and how they would interact with this dashboard.
    """
    
    # Convert JSON to string safely to avoid f-string formatting issues
    analysis_result_str = json.dumps(analysis_result, indent=2)
    
    user_prompt = """
ROLE
You are an expert business analyst specializing in user experience and dashboard audience analysis.

OBJECTIVE
Your task is to analyze the provided dashboard analysis result (containing KPIs, attributes, and metadata) to identify the primary user context - What does the user want to achieve by using this dashboard. What steps does the user take to analyse the dashboard manually.

ANALYSIS APPROACH
1. Examine the KPIs to understand what business roles would need these metrics
2. Look at the liveboard name and business domain to identify the target department/function
3. Analyze the complexity and granularity of data to determine user seniority level
4. Consider the types of decisions these metrics would support
5. If you identify KPIs from a specific industry, use your world knowledge to understand typical user roles and contexts.

KEY POINTS TO FOCUS ON:
1. If there are pivot tables, the attributes visualized will have a hierarchical structure. Use this to understand the user context. 
2. Users build dashboard to analyse data manually. Use this to understand the user context.
3. Users build dashboard to make decisions. For that they need to explore not just the most important values, but also the secondary values.

IMPORTANT:
This is going to be the prompt the LLM along with the important KPIs and attributes to come up with a plan of what the user wants to achieve by using this dashboard. So be as detailed as possible and include all the steps they take to achieve them. Clearly state what are the nuances with the data like what they need to ignore, consider, etc. This is the MOST CRITICSL input for the system to analyse the dashboard.

OUTPUT FORMAT
Provide a single, clear sentence that describes the user context, including who uses the dashboard and in what situation. Make sure to include the steps they take to achieve them.

Example outputs:
- "Marketing executives and campaign managers use this dashboard during weekly planning meetings to assess campaign performance and allocate budget."
- "Sales directors and regional managers review this dashboard monthly to track pipeline health and forecast quarterly revenue achievement."
- "Customer support team leads monitor this dashboard daily to ensure service quality and identify areas needing immediate attention."

Do not include JSON, bullet points, or complex formatting. Just provide one clear sentence that captures the primary user context and usage scenario.

Analysis Result Data:
""" + analysis_result_str + """
"""
    
    return system_prompt, user_prompt

def kpi_refinement_prompt(kpis_json: dict) -> tuple[str, str]:
    print("KPI refinement prompt not implemented")
    return "", ""
'''
def kpi_refinement_prompt(kpis_json: dict) -> tuple[str, str]:
    """
    Get the system and user prompts for KPI refinement from extracted KPIs JSON.
    
    Args:
        kpis_json: The extracted KPIs JSON data to refine
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = """
    You are an expert business intelligence analyst specializing in KPI refinement and deduplication.
    Your task is to analyze KPIs, assign scores based on their source visualization types, identify duplicates, and return a refined list.
    """
    
    user_prompt = f"""
    TASK: Refine and deduplicate KPIs based on scoring and duplicate detection rules.

    SCORING RULES:
    Assign scores to each KPI based on the chart_type it comes from:
    - KPI Chart: 10 points
    - Table: 7 points  
    - Other charts: 3 points

    DUPLICATE DETECTION RULES:
    Two KPIs are considered duplicates if they have:
    1. The SAME measure/field name
    2. The SAME set of filters (exact match, order doesn't matter)

    DEDUPLICATION PROCESS:
    1. First, assign scores to all KPIs based on their source chart type
    2. Identify groups of duplicate KPIs using the duplicate detection rules
    3. For each group of duplicates, keep only the KPI with the HIGHEST score
    4. If scores are tied, keep the first one encountered
    5. Return the final deduplicated list with scores

    ANALYSIS INSTRUCTIONS:
    1. Go through each KPI in the provided JSON
    2. Assign a score based on the chart type (you may need to infer this from the KPI context)
    3. Group KPIs that are duplicates based on measure and filters
    4. Keep the highest scoring KPI from each duplicate group
    5. Return the refined list

    IMPORTANT NOTES:
    - Compare filters as sets (order doesn't matter)
    - Empty filter arrays should be treated as equivalent
    - Measure names should be compared case-insensitively
    - Keep the original KPI structure but add a "score" field

    INPUT KPIs TO REFINE:
    {json.dumps(kpis_json, indent=2)}

    REQUIRED OUTPUT FORMAT:
    Return a single valid JSON object with the refined KPIs. Each KPI should include the original fields plus a "score" field.

    {{
      "KPI_1": {{
        "name": "Original KPI Name",
        "measure": "measure_name",
        "formula": "formula_if_any",
        "filters": ["filter1", "filter2"],
        "description": "description",
        "score": 10,
        "chart_type": "KPI"
      }},
      "KPI_2": {{
        "name": "Another KPI Name", 
        "measure": "different_measure",
        "formula": "different_formula",
        "filters": ["filter3"],
        "description": "description",
        "score": 7,
        "chart_type": "TABLE"
      }}
    }}
    """
    
    return system_prompt, user_prompt
'''
def get_attributes_extraction_prompt(extracted_json: dict) -> tuple[str, str]:
    """
    Get the system and user prompts for attributes and date extraction from extracted visualization JSON.
    
    Args:
        extracted_json: The extracted visualization JSON data
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = """
    You are a data modeling expert specializing in dimensional analysis. 
    Analyze the extracted visualization data and identify the most important dimensions and attributes that would be useful for data slicing, filtering, and grouping in business analysis.
    Focus on attributes that provide meaningful business insights when used for analysis.
    """
    
    # Convert JSON to string safely to avoid f-string formatting issues  
    extracted_json_str = json.dumps(extracted_json, indent=2)
    
    user_prompt = """
    Your task is to act as an expert data analyst specializing in BI dashboard analysis. I will provide you with extracted visualization data that contains structured information about charts, tables, and their configurations.

    Your goal is to analyze this data and identify the most important attributes for analysis. Focus on dimensional attributes that are used for slicing, dicing, and grouping data.

    ANALYSIS INSTRUCTIONS:
    1. Look at the "visualizations" array in the provided data
    2. For each visualization (viz_id), examine:
       - The visible_columns (for tables)
       - The axis_configs (for charts - x, y, color dimensions)
       - The answer_search_query for filtering and grouping attributes
       - Any dimensional fields used for slicing data
       - The chart_type (TABLE, charts, etc.)
       - The tab_name (tab name)

    3. For each attribute - Score and rank  based on their usage and importance:
       - Attributes used for color coding/slicing : Score 10
       - Attributes used as X-axis dimensions  : Score 7
       - Attributes used in Table : Score 5
       - Attributes used in filters and grouping : Score 2

    WHAT TO FOCUS ON:
    - Dimensional attributes (not measures/metrics)
    - Fields used for grouping, filtering, and slicing
    - Categorical fields like Status, Type, Category, Region, etc.
    - Date/time fields for temporal analysis

    WHAT TO IGNORE:
    - Numeric measures and calculated fields
    - Aggregation functions (SUM, COUNT, AVG, etc.)
    - Formula expressions

    DATE FIELD IDENTIFICATION:
    - Look for fields with "Date", "Time", "Created", "Modified" in their names
    - Consider fields used for temporal filtering or time-series analysis
    - Pick the most commonly used or most important date field

    Required Output Format:
    Your response must be a single, valid JSON object and nothing else. Do not add any explanatory text, markdown formatting, or code block syntax around the JSON.

    {{
      "Attribute": [
        "Top Attribute 1",
        "Top Attribute 2", 
        "Top Attribute 3",
        "Top Attribute 4",
        "Top Attribute 5"
      ],
      "Date": "Most Important Date Field"
    }}

    Extracted Visualization Data:
    """ + extracted_json_str + """
    """
    
    return system_prompt, user_prompt