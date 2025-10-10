from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping

from inputs import scenario_pg, scenario_support, scenario_ta, scenario_cmo, scenario_test


def metadata_table_system_prompt(scenario: str) -> str:
    """
    Generate metadata table system prompt for a specific scenario.
    
    Args:
        scenario: One of 'pg', 'support', 'ta', 'cmo'
    
    Returns:
        Formatted system prompt with scenario-specific inputs
    """
    # Map scenario names to functions
    scenario_functions = {
        'pg': scenario_pg,
        'support': scenario_support,
        'ta': scenario_ta,
        'cmo': scenario_cmo,
        'test': scenario_test,
    }
    
    if scenario not in scenario_functions:
        raise ValueError(f"Unknown scenario: {scenario}. Must be one of: {list(scenario_functions.keys())}")
    
    # Get scenario-specific inputs
    inputs = scenario_functions[scenario]()
    
    # Build the prompt with dynamic inputs
    prompt = f"""Persona: You are a Senior Business Analyst specializing in sales operations and GTM strategy.

Context: You have been provided with the metadata for a data table from a sales dashboard, along with specific business context. Your task is to create a detailed, actionable plan for analyzing this data to meet a stated business goal.

Input Information:

Liveboard TML:
{inputs['Liveboard_TML']}

Key Performance Indicators (KPIs):
{inputs['KPI']}

Important Attributes for Analysis:
{inputs['Attributes']}

Date column to be used for filtering:
{inputs['Date_Column']}

Key Aggregation Metrics:
{inputs['Aggregations']}

Primary Goal of the Analysis:
{inputs['Goal']}

User Context:
{inputs['User_Context']}

Your Task:
Based on the information provided, generate a the metadata of a table with all the information needed. 

If you need a master table with all the required data to apply filters and get the insights needed. 

What are the columns the table would have to provide the analysis needed. 
If tables exist in the Liveboard TML then levarge them to come up with the master table metadata. """ 
    return prompt


def output_format_system_prompt() -> str:
    """
    System prompt for output format specification.
    Ensures LLM output is structured JSON.
    """
    return """
    
    Output as a JSON in a format similar to below

{
  "analysis_plan": [
    {
      "phase_number": "",
      "phase_title": "",
      "goal": "",
      "steps": [
        {
          "step": "",
          "title": "",
          "objective": "",
          "data_requirements": {
            "columns_used": [
              "",
              "",
              "",
              ""
            ],
            "filters": [
              {
                "column": "",
                "condition": "",
                "value": ""
              },
              {
                "column": "",
                "condition": "",
                "value": ""
              },
              {
                "column": "",
                "condition": "",
                "value": ""
              }
            ],
            "grouping_and_aggregations": {
              "group_by": [
                ""
              ],
              "aggregations": [
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                },
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                }
              ]
            }
          },
          "key_insights_questions_answered": ""
        },
        {
          "step": "",
          "title": "",
          "objective": "",
          "data_requirements": {
            "columns_used": [
              "",
              "",
              "",
              "",
              ""
            ],
            "filters": [
              {
                "column": "",
                "condition": "",
                "value": ""
              },
              {
                "column": "",
                "condition": "",
                "value": ""
              }
            ],
            "grouping_and_aggregations": {
              "group_by": [
                "",
                ""
              ],
              "aggregations": [
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                },
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                }
              ]
            }
          },
          "key_insights_questions_answered": ""
        },
        {
          "step": "",
          "title": "",
          "objective": "",
          "data_requirements": {
            "columns_used": [
              "",
              "",
              "",
              "",
              ""
            ],
            "filters": [
              {
                "column": "",
                "condition": "",
                "value": ""
              },
              {
                "column": "",
                "condition": "",
                "value": ""
              }
            ],
            "grouping_and_aggregations": {
              "group_by": [
                "",
                ""
              ],
              "aggregations": [
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                },
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                }
              ]
            }
          },
          "key_insights_questions_answered": ""
        },
        {
          "step": "",
          "title": "",
          "objective": "",
          "data_requirements": {
            "columns_used": [
              "",
              "",
              "",
              "",
              "",
              ""
            ],
            "filters": [
              {
                "column": "",
                "condition": "",
                "value": ""
              },
              {
                "column": "",
                "condition": "",
                "value": ""
              }
            ],
            "grouping_and_aggregations": {
              "group_by": [
                "",
                "",
                ""
              ],
              "aggregations": [
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                },
                {
                  "type": "",
                  "column": "",
                  "alias": ""
                }
              ]
            }
          },
          "key_insights_questions_answered": ""
        }
      ]
    }
  ]
}
    """


def parse_llm_output(output: str) -> Dict[str, Any]:
    """
    Parse LLM output to ensure it's valid JSON.
    Handles common formatting issues and extracts JSON from text.
    
    Args:
        output: Raw LLM output string
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If JSON cannot be parsed
    """
    # Clean the output - remove any text before/after JSON
    output = output.strip()
    
    # Find JSON boundaries
    start_idx = output.find('{')
    end_idx = output.rfind('}')
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        raise ValueError("No valid JSON found in output")
    
    # Extract JSON portion
    json_str = output[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def get_metadata_prompt_with_format(scenario: str) -> tuple[str, str]:
    """
    Get both the metadata system prompt and output format prompt for a scenario.
    
    Args:
        scenario: One of 'pg', 'support', 'ta', 'cmo'
        
    Returns:
        Tuple of (metadata_prompt, output_format_prompt)
    """
    metadata_prompt = metadata_table_system_prompt(scenario)
    table_system_prompt = f""" The output should be only the Meta data of the master table in JSON format. Do not add any new columns. The columns should be from the Liveboard TML context

List the Key attributes, measure and date columns.
Generate it as a JSON for easy parsing"""

    #output_format_prompt = output_format_system_prompt()
    
    return metadata_prompt, table_system_prompt









def plan_splitter() -> str:
    """
    System prompt for splitting high-level analysis plans into data fetch and analysis plans.
    
    Returns:
        The plan splitter system prompt
    """
    return """You are an expert data analysis planner. Your task is to convert a high-level, multi-step analysis plan into a detailed, two-part execution plan: a `data_fetch_plan` and an `analysis_plan`.

The user will provide a JSON object representing the high-level plan. You must adhere to the following rules to transform it:

**Part 1: `data_fetch_plan`**

1.  **Granularity is Key:** You must break down each step from the original plan into the most granular data fetch requests possible.
2.  **Explode 'IN' Clauses:** If a filter condition contains multiple values (e.g., an 'IN' clause with a list of stages like `('M0', 'M1', 'S0')`), you must create a *separate* and complete data fetch step for *each individual value* in that list.
3.  **No Aggregations:** The goal is to fetch raw, row-level data. Do NOT include any aggregations (SUM, COUNT, AVERAGE) in the data fetch requirements.
4.  **Consolidate Columns:** The `columns_to_fetch` for each step must include all columns from the original `columns_used` AND any columns that were previously part of an `aggregations` block. For example, if the original plan had `SUM(ACV)`, the `columns_to_fetch` must now include `ACV`.
5.  **Generate a Natural Language Prompt:** For each granular step, create a `prompt` key. The value must be a clear, self-contained natural language query that an NL-to-SQL agent can execute. It must explicitly mention all columns to fetch and all filter conditions for that specific, granular step.
6.  **Structure:** Each object in the `data_fetch_plan` array must contain:
    *   `step_id`: A unique identifier for the granular step (e.g., "1.1", "1.2").
    *   `original_phase_number`: The phase number from the source plan.
    *   `original_step_title`: The title of the step from the source plan.
    *   `prompt`: The generated natural language prompt.
    *   `data_requirements`: An object containing:
        *   `columns_to_fetch`: A list of all required column names.
        *   `filters`: A list of filter objects for this specific granular step.

**Part 2: `analysis_plan`**

1.  **Describe the 'How':** This section outlines how the fetched data will be used for computation and insight generation. It should mirror the logic of the original plan.
2.  **Reference Fetched Data:** The analysis steps should implicitly or explicitly refer to the data retrieved in the `data_fetch_plan`.
3.  **Include Computations:** This is where the original aggregations and comparisons (like calculating variance) belong. Describe the calculations that need to be performed on the raw data.
4.  **Structure:** The `analysis_plan` should be an array of objects, where each object represents a phase of the analysis and contains the overall `goal` and a list of `steps` describing the post-fetch computations.

Your final output must be a single JSON object with two top-level keys: `data_fetch_plan` and `analysis_plan`.

JSON from user:


"""

def plan_splitter_output_format_system_prompt() -> str:
    """
    System prompt for plan splitter output format specification.
    Ensures LLM output follows the specific JSON schema for data fetch and analysis plans.
    """
    return """
Output as a JSON in the following format:

{
  "data_fetch_plan": [
    {
      "answer_id": "string",
      "original_phase_number": "integer",
      "original_step_title": "string",
      "prompt": "string",
      "data_requirements": {
        "columns_to_fetch": [
          "string"
        ],
        "filters": [
          {
            "column": "string",
            "condition": "string",
            "value": "string | integer"
          }
        ]
      }
    }
  ],
  "analysis_plan": [
    {
      "step": "string",
      "title": "string",
      "objective": "string",
      "source_answer_ids": [
        "string"
      ],
      "depends_on_steps": [
        "string"
      ],
      "computations": {
        "group_by": [
          "string"
        ],
        "aggregations": [
          "object"
        ]
      },
      "key_insights_questions_answered": "string"
    }
  ]
}

"""

def get_plan_splitter_with_format() -> tuple[str, str]:
    """
    Get both the plan splitter system prompt and output format prompt.
    
    Returns:
        Tuple of (plan_splitter_prompt, output_format_prompt)
    """
    plan_splitter_prompt = plan_splitter()
    output_format_prompt = plan_splitter_output_format_system_prompt()
    
    return plan_splitter_prompt, output_format_prompt

def get_plan_prompt_with_format(scenario: str, metadata_output: str = None) -> tuple[str, str]:
    """
    Get both the analysis plan system prompt and output format prompt for a scenario.
    
    Args:
        scenario: One of 'pg', 'support', 'ta', 'cmo'
        metadata_output: LLM output from metadata_table_prompt (optional)
        
    Returns:
        Tuple of (plan_prompt, output_format_prompt)
    """
    # Map scenario names to functions
    scenario_functions = {
        'pg': scenario_pg,
        'support': scenario_support,
        'ta': scenario_ta,
        'cmo': scenario_cmo,
        'test': scenario_test,
    }
    
    if scenario not in scenario_functions:
        raise ValueError(f"Unknown scenario: {scenario}. Must be one of: {list(scenario_functions.keys())}")
    
    # Get scenario-specific inputs
    inputs = scenario_functions[scenario]()
    
    # Build the plan prompt with dynamic inputs
    plan_prompt = f"""Persona: You are a Senior Business Analyst specializing in sales operations and GTM strategy.

Context: You have been provided with the metadata for a data table from a sales dashboard, along with specific business context. Your task is to create a detailed, actionable plan for analyzing this data to meet a stated business goal.

Input Information:

Liveboard TML:
{inputs['Liveboard_TML']}

Key Performance Indicators (KPIs):
{inputs['KPI']}

Important Attributes for Analysis:
{inputs['Attributes']}

Key Aggregation Metrics:
{inputs['Aggregations']}

Primary Goal of the Analysis:
{inputs['Goal']}

User Context:
{inputs['User_Context']}

Master table meta data:
{metadata_output if metadata_output else "{{ $json.output }}"}

Your Task:
Based on the information provided, generate a comprehensive, step-by-step analysis plan.

Requirements for the Plan:
Structure: Organize the plan into logical phases, starting from a high-level overview and progressively drilling down into more granular detail. Avoid generating steps at the lower level of granularity. There is going to be an analysis step that will look at the data and do the agrregation and get insights

Clarity: For each step in your plan, clearly state:

The Objective of that specific analysis step.

The Columns from the Master table that will be used for filtering, grouping, aggregation and the additional columns to fetch for context.
Within each specific analysis step, give the exact filter, aggregation and grouping for the different values individually. The output would be used directly to fetch the data with the exact text you generate. So do not use placeholders. For each value, generate a different sub step that can be directly executed

The specific Aggregations and Groupings to be performed (e.g., "Group by 'Opportunity Owner Team' and 'Opportunity Stage', then calculate the Count of Opportunities and Sum of 'Total Opportunity ACV'").
The Key Insights you expect to derive from that step and the business questions it will answer.
Action-Oriented: The plan should be designed to produce actionable insights that directly address the stated goal.
Assumptions: If necessary, state any assumptions you are making (e.g., the sequential nature of the pipeline stages).
Think step-by-step to construct a plan that a junior analyst could follow to execute the analysis effectively.
Important: For each data fetch step, there should be an analysis step that will use the data fetched to get the insights. Ensure that the analysis step is dependent on the data fetch step.
The output should be in JSON. One output for an analysis step"""
    
    output_format_prompt = output_format_system_prompt()
    
    return plan_prompt, output_format_prompt

def final_prompt(scenario: str, metadata_output: Dict[str, Any]) -> str:
    """
    Generate the final comprehensive analysis plan prompt.
    
    Args:
        scenario: The business scenario (pg, support, ta, cmo)
        metadata_output: The parsed metadata from the LLM
        
    Returns:
        The final prompt string
    """
    # Get scenario-specific inputs
    scenario_functions = {
        'pg': scenario_pg,
        'support': scenario_support,
        'ta': scenario_ta,
        'cmo': scenario_cmo,
        'test': scenario_test,
    }
    
    if scenario not in scenario_functions:
        raise ValueError(f"Unknown scenario: {scenario}. Must be one of: {list(scenario_functions.keys())}")
    
    inputs = scenario_functions[scenario]()
    
    # Extract metadata information
    metadata_info = ""
    if isinstance(metadata_output, dict):
        if 'tables' in metadata_output:
            metadata_info = f"Master Table Metadata: {metadata_output['tables']}"
        elif 'output' in metadata_output:
            metadata_info = f"Master Table Metadata: {metadata_output['output']}"
        else:
            metadata_info = f"Master Table Metadata: {metadata_output}"
    else:
        metadata_info = f"Master Table Metadata: {metadata_output}"
    
    final_prompt_text = f"""Persona: You are a Senior Business Analyst with deep expertise in data analysis. Your audience is a junior analyst who will execute the plan you create. Your tone should be authoritative, clear, and instructive. You must guide the junior analyst through a logical and efficient data exploration process to uncover actionable insights.

Context: You have been provided with metadata for a sales data table, along with key business objectives and context. Your mission is to create a detailed, actionable, and phased plan for analyzing this data to meet a specific business goal.

Input Information:

Liveboard TML: {inputs['Liveboard_TML']}
Key Performance Indicators (KPIs): {inputs['KPI']}
Important Attributes for Analysis: {inputs['Attributes']}
Key Aggregation Metrics: {inputs['Aggregations']}
Primary Goal of the Analysis: {inputs['Goal']}
User Context: {inputs['User_Context']}
Meta table information: {metadata_info}

Your Task:
Based on all the information provided, generate a comprehensive, step-by-step analysis plan. The plan must be structured logically to tell a cohesive story with the data, starting from a high-level overview and drilling down into specifics. The ultimate goal is to produce actionable insights that directly address the Primary Goal of the Analysis.

Requirements for the Plan:

1. Overall Structure:
Organize the entire plan into logical Phases. Each phase should represent a distinct stage of the analysis (e.g., "Phase 1: High-Level Pipeline Health Assessment," "Phase 2: Regional Performance Deep-Dive"). Within each phase, you will define a series of Fetch and Analysis steps.

2. Fetch Steps:
Each Fetch step represents a specific data retrieval action. The goal is to fetch small, targeted datasets to keep the analysis focused and efficient. The fetched data should have the attributes for grouping as well as context as necessary. Each Phase can have multiple Fetch steps
For each granular step, the Fetch Prompt should be a clear, self-contained natural language query that an NL-to-SQL agent can execute. It must explicitly mention all columns to fetch and all filter conditions for that specific, granular step. Ensure that required filters are mentioned in the Fetch Prompt and not left to the analysis step to aggregate
For each Fetch step, you must clearly specify:

Objective: A brief sentence explaining the purpose of this data pull.
Required Data: The specific columns (attributes and measures) needed from the master table. Mention any required aggregations (e.g., SUM of [Amount]) and filters (e.g., Date Range: Last Quarter, [Status] is 'Open').
Fetch Prompt: A precise, natural language query for a data agent to execute. Crucially, you must enclose all column names in square brackets [].

3. Analysis Steps:
Each Analysis step details the computation and the business question to be answered using the data from the immediately preceding Fetch step.
For each Analysis step, you must clearly specify:

Group By: The attribute(s) by which the fetched data should be grouped.
Aggregation: The single metric to be calculated for each group (e.g., Count of [Opportunity ID], Average of [Deal Size]) (if needed).
Context: Additional columns from the fetched table needed to answer the question (if any).
Note: In many tables, you perform the aggrgation on one column, and then you need to do the analysis based on other column as that gives the context. For example, you can filter by [Case NPS Score Segment] = Passives, and then count the number of Account names.
Question: The specific business question this analysis will answer.
Analysis Prompt: A clear instruction for an LLM, which will receive the fetched data and perform the analysis to generate an insight.

Critical Constraints (Follow These Strictly):
Dependency: Each Analysis step must be based on data from only one Fetch step.
Efficiency: A single Fetch step cannot have more than two Analysis steps associated with it. This ensures each data pull is highly focused.
Granularity: Each Analysis step must have only one aggregation and address only one business question.
Assumptions: If you make any assumptions about the data (e.g., "Assuming pipeline stages are sequential"), state them clearly at the beginning of the plan.
Important: Fetch the data at the lowest granularity with necessary filters on attributes such that the analysis step doesnt have to apply any filterining. Do not have multiple group by in the analysis step. You filter the data as per the need and fetch it. Then the analysis step should just do the aggregation.

Example:
Do not have a Fetch prompt like "Fetch all opportunities where [Opportunity Created Date] is 'last week' and [Opportunity Stage] is in ('M0', 'M1', 'S0', 'S1') and [Opportunity ACV] is greater than 0.0 and [Opportunity Type] is either 'existing customer expansion' or 'new customer'. Include columns [Opportunity Owner Team], [Opportunity Stage], and [Opportunity ACV].", Instead have that split into multiple Fetch steps with the filters mentioned for each stage individually. Like ""Fetch all opportunities where [Opportunity Created Date] is 'last week' and [Opportunity Stage] is M0 and [Opportunity ACV] is greater than 0.0 and [Opportunity Type] is either 'existing customer expansion' or 'new customer'. Include columns [Opportunity Owner Team], [Opportunity Stage], and [Opportunity ACV]."
This ensure the analysis step doesnt have to apply any filterining
"""
    
    return final_prompt_text


def final_output_format() -> str:
    """
    Define the JSON schema for the final analysis plan output.
    
    Returns:
        JSON schema string for the final analysis plan
    """
    return """{
"analysisPlan": {
    "primaryGoal": "<string: A concise statement of the main objective for the entire analysis>",
    "assumptions": [
      "<string: State an assumption about the data, e.g., 'The [Close Date] field is accurate.'>",
      "<string: State another assumption if necessary>"
    ],
    "phases": [
      {
        "phaseNumber": "<integer: The sequential number of this analysis phase, e.g., 1>",
        "phaseTitle": "<string: The title of this phase, e.g., 'Baseline Performance Assessment'>",
        "phaseDescription": "<string: A brief description of what this phase aims to achieve>",
        "fetchSteps": [
          {
            "stepId": "<string: A unique identifier for this step, e.g., '1.1'>",
            "title": "<string: The title of this specific data fetch, e.g., 'Fetch 1: Overall Deal Outcomes'>",
            "objective": "<string: The purpose of this data pull>",
            "requiredData": "<string: The specific columns, filters, and aggregations required for this fetch>",
            "fetchPrompt": "<string: The natural language prompt for a data agent to execute the fetch>",
            "analysisSteps": [
              {
                "stepId": "<string: A unique identifier for this analysis, e.g., '1.1.1'>",
                "title": "<string: The title of this analysis, e.g., 'Analysis 1: Calculate Overall Win Rate'>",
                "groupBy": "<string: The attribute(s) to group the data by, e.g., '[Is Won]'>",
                "aggregation": "<string: The single metric to be calculated, e.g., 'Count of [Opportunity ID]'>",
                "question": "<string: The specific business question this analysis will answer>",
                "analysisPrompt": "<string: The clear instruction for an LLM to perform the analysis and generate an insight>"
              },
              {
                "stepId": "<string: A unique identifier for another analysis on the same fetched data, e.g., '1.1.2'>",
                "title": "<string: The title of the second analysis>",
                "groupBy": "<string: The attribute(s) to group by>",
                "aggregation": "<string: The metric to be calculated>",
                "question": "<string: The business question to be answered>",
                "analysisPrompt": "<string: The instruction for the LLM>"
              }
            ]
          }
        ]
      },
      {
        "phaseNumber": "<integer: e.g., 2>",
        "phaseTitle": "<string: Title for the second phase>",
        "phaseDescription": "<string: Description for the second phase>",
        "fetchSteps": [
          {
            "stepId": "<string: e.g., '2.1'>",
            "title": "<string: Title of the fetch step>",
            "objective": "<string: Objective of the fetch>",
            "requiredData": "<string: Data required>",
            "fetchPrompt": "<string: Fetch prompt>",
            "analysisSteps": [
              {
                "stepId": "<string: e.g., '2.1.1'>",
                "title": "<string: Title of the analysis>",
                "groupBy": "<string: Group by attribute(s)>",
                "aggregation": "<string: Aggregation metric>",
                "question": "<string: Business question>",
                "analysisPrompt": "<string: LLM analysis prompt>"
              }
            ]
          }
        ]
      }
    ]
  }
}"""



def analysis_json_extractor(analysis_json: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract analysis data from the analysis JSON file.
    
    Args:
        analysis_json: The analysis results JSON loaded from file
        
    Returns:
        List of dictionaries containing extracted analysis data
    """
    extracted_analyses = []
    
    for step_id, analysis_data in analysis_json.items():
        if isinstance(analysis_data, dict):
            # Extract the required fields
            extracted_data = {
                'stepId': step_id,
                'title': analysis_data.get('title', ''),
                'question': analysis_data.get('question', ''),
                'analysisResponse': analysis_data.get('analysisResponse', ''),
                'status': analysis_data.get('status', 'unknown')
            }
            extracted_analyses.append(extracted_data)
    
    return extracted_analyses


def report_prompt(analysis_data: List[Dict[str, str]], scenario: str, llm_provider: str) -> str:
    """
    Generate a comprehensive report prompt based on analysis results.
    
    Args:
        analysis_data: List of extracted analysis data from analysis_json_extractor
        scenario: The scenario name (support, pg, ta, cmo)
        llm_provider: The LLM provider being used
        
    Returns:
        Formatted report prompt string
    """
    from inputs import get_scenario_inputs
    
    # Get scenario-specific inputs
    scenario_inputs = get_scenario_inputs(scenario)
    user_context = scenario_inputs.get('User Context', '')
    goal = scenario_inputs.get('Goal', '')
    report_format = scenario_inputs.get('Report Format', '')
    
    # Build analysis summary
    analysis_summary = ""
    for i, analysis in enumerate(analysis_data, 1):
        if analysis.get('status') == 'completed' and analysis.get('analysisResponse'):
            analysis_summary += f"\n{i}. {analysis.get('title', 'Unknown Analysis')}\n"
            analysis_summary += f"   Question: {analysis.get('question', 'N/A')}\n"
            analysis_summary += f"   Response: {analysis.get('analysisResponse', 'N/A')}\n"
    
    #print(f"Analysis summary: {analysis_summary}")
    #input("Press Enter to continue...")
    
    #Try2 - Refined the prompt to generate the Executive Summary and Top 5 focus areas based on the report generated
    prompt = f"""You are an expert data analyst and business report writer. Your function is to act as a pure data-to-text engine, converting structured analysis results into a formal business document with perfect fidelity to the requested format and content rules. You must operate with precision and follow all rules without deviation.

--- MASTER RULES ---

ON STRUCTURE: Your TOP PRIORITY is that the output's structure MUST EXACTLY mirror the structure provided in the [Report Format] input. If [Report Format] specifies sections or headings, you MUST replicate them precisely. Do not add any text, headings, or sections that are not explicitly defined. The output must begin with the first specified section and end with the last.
- Executive Summary Exception: If an 'Executive Summary' section is specified in the [Report Format], it must be generated last, after all other analytical sections are complete, and then placed in its correct position in the final output. The process for this is detailed below.



ON DETAIL AND COMPREHENSIVENESS: Your analysis within each section must be exhaustive and deeply detailed.
- General Content: Incorporate every relevant data point, figure, and finding from the [ANALYSIS RESULTS]. Do not over-summarize complex topics into a single sentence.
- Top/Bottom Performers Rule: When the analysis identifies rankings or top/bottom performers (e.g., best-selling products, most active users, bottom regions), DO NOT only mention the single top item. You MUST list the top 3-5 performers, or as many as are identified as significant in the analysis.
- Formatting for Lists: You MUST present these lists of top/bottom performers using bullet points (e.g., using a hyphen '-'). Each bullet point must clearly state the item's name, its specific corresponding values, and any other relevant data points mentioned in the analysis to provide full context.

ON RECOMMENDATIONS: There is an absolute prohibition on providing recommendations. Under NO circumstances are you to include suggestions, opinions, next steps, or any form of forward-looking advice. The report is purely descriptive and analytical. Terminate the report immediately after presenting the final piece of analysis.

--- REPORT GENERATION PROCESS ---

You will follow a strict, multi-step internal process to construct the final report:

Step 1: Analyze Inputs and Plan Structure.
Parse the [Report Format], [USER CONTEXT], [ANALYSIS RESULTS], and [GOAL]. Identify all required sections and determine the final document structure. Note the location designated for the 'Executive Summary', if present.

Step 2: Generate the Main Report Body (First Pass).
Generate all sections of the report as specified in the [Report Format] EXCEPT for the 'Executive Summary'. Write the detailed analysis for all other sections, adhering strictly to the Master Rules. Internally, you can think of leaving a placeholder for the Executive Summary.

Step 3: Synthesize the Executive Summary (Second Pass).
After generating the entire report body (from Step 2), you will internally review the complete text you have just written. Based on this comprehensive review, you will perform the following synthesis tasks:
- A. Identify Top 5 Focus Areas: Based on the most significant, impactful, or recurring themes in your generated report, identify a list of the Top 5 Focus Areas. These should be concise phrases that capture the key takeaways (e.g., "High-Value Customer Segment Performance," "Regional Sales Disparities," "Product Category Growth Trends"). Within each theme, give the top 2 or 3 items that are most significant.
- B. Write the Executive Summary: Write a concise, 4-5 line overview of the report's most critical findings. This summary MUST integrate and conclude with the Top 5 Focus Areas you identified in a clear format (such as a bulleted list).

Step 4: Assemble the Final Report.
Construct the final, complete report by inserting the newly generated Executive Summary (from Step 3) into its correct location as dictated by the [Report Format]. The final output must be a single, seamless document with no placeholders or notes about this internal process.

Default Structure:
If and ONLY IF the [Report Format] input is absent or empty, you will default to the following structure, applying the multi-step generation process described above:

BACKGROUND
A brief section stating the report's purpose, referencing the [Goal] and [User context]. State the period for the analysis if any.

EXECUTIVE SUMMARY
[This section is to be generated in Step 3 and placed here]. It will contain a concise overview and a bulleted list of the Top 5 Focus Areas derived from the Detailed Analysis.

DETAILED ANALYSIS
The main body of the report, synthesizing the [ANALYSIS RESULTS] according to all Master Rules.

---
REPORT FORMAT: {report_format}
USER CONTEXT: {user_context}
ANALYSIS RESULTS: {analysis_summary}
GOAL: {goal}


"""


    return prompt


def report_executive_summary_prompt(analysis_data: List[Dict[str, str]], scenario: str, llm_provider: str) -> str:
    """
    Generate an executive summary prompt based on analysis data.
    
    Args:
        analysis_data: List of extracted analysis data from analysis_json_extractor
        scenario: The scenario name (support, pg, ta, cmo)
        llm_provider: The LLM provider being used
        
    Returns:
        Formatted executive summary prompt string
    """
    # This function can be implemented later if needed
    return ""

def report_system_prompt() -> str:
    """
    Generate the system prompt for report generation.
    
    Returns:
        System prompt string for report generation
    """
    return """You are an expert business analyst and report writer with extensive experience in creating executive-level reports. Your role is to synthesize complex analysis results into clear, actionable insights that drive business decisions.

Key capabilities:
- Transform technical analysis into business-friendly language
- Identify patterns and trends across multiple data points
- Generate actionable recommendations based on data insights
- Create compelling narratives that engage executive audiences
- Balance detail with clarity for maximum impact

Your reports should be:
- Executive-ready and professionally formatted
- Data-driven with specific metrics and evidence
- Action-oriented with clear next steps
- Contextually relevant to the business scenario
- Concise yet comprehensive

Focus on delivering value through insights that directly impact business outcomes."""