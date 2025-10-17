"""
Analysis module for processing CSV data and generating insights.
Handles LLM-based analysis of fetched data using analysis prompts.
"""

import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai
from anthropic import Anthropic
import openai

# Load environment variables
load_dotenv()


def call_llm_for_analysis(system_prompt: str, csv_data: str, llm_provider) -> str:
    """
    Call LLM for analysis with CSV data.
    
    Args:
        system_prompt: Analysis prompt/instructions
        csv_data: CSV data to analyze
        llm_provider: Either "gemini", "claude", or "openai"
        
    Returns:
        LLM analysis response
    """
    if llm_provider.lower() == "gemini":
        return call_gemini_for_analysis(system_prompt, csv_data)
    elif llm_provider.lower() == "claude":
        return call_claude_for_analysis(system_prompt, csv_data)
    elif llm_provider.lower() == "openai":
        return call_openai_for_analysis(system_prompt, csv_data)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def call_gemini_for_analysis(system_prompt: str, csv_data: str) -> str:
    """Call Google Gemini for analysis."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Combine system prompt with CSV data
    full_prompt = f"{system_prompt}\n\nCSV Data to analyze:\n{csv_data}"
    
    try:
        print("🤖 Calling Gemini for analysis...")
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        raise


def call_claude_for_analysis(system_prompt: str, csv_data: str) -> str:
    """Call Claude for analysis."""
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        raise ValueError("CLAUDE_API_KEY environment variable not set")
    
    client = Anthropic(api_key=api_key)
    
    # Combine system prompt with CSV data
    full_prompt = f"{system_prompt}\n\nCSV Data to analyze:\n{csv_data}"
    
    try:
        print("🤖 Calling Claude for analysis...")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=64000,
            temperature=0.7,
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
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


def call_openai_for_analysis(system_prompt: str, csv_data: str) -> str:
    """Call OpenAI GPT for analysis."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        print("🤖 Calling OpenAI for analysis...")
        
        # If csv_data is empty or just whitespace, send everything in the user message
        # This happens during report generation where all content is in system_prompt
        if not csv_data or not csv_data.strip():
            messages = [
                {
                    "role": "user",
                    "content": system_prompt
                }
            ]
        else:
            # For analysis steps, send system prompt and data separately
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"CSV Data to analyze:\n{csv_data}"
                }
            ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
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


def execute_analysis_plan(analysis_plan: List[Dict[str, Any]], fetched_data: Dict[str, Any], llm_provider: str = "gemini") -> Dict[str, Any]:
    """
    Execute analysis plan by sending CSV data and analysis prompts to LLM.
    
    Args:
        analysis_plan: List of analysis steps from the plan
        fetched_data: Data fetched from APIs (keyed by answer_id)
        llm_provider: LLM provider to use for analysis
        
    Returns:
        Dictionary of analysis results keyed by step
    """
    results = {}
    
    print(f"\n📊 Executing analysis plan with {len(analysis_plan)} steps...")
    
    for step in analysis_plan:
        step_id = step.get('step', 'unknown')
        title = step.get('title', 'Unknown Analysis')
        objective = step.get('objective', '')
        source_answer_ids = step.get('source_answer_ids', [])
        key_insights_questions = step.get('key_insights_questions_answered', '')
        
        print(f"\n🔍 Processing analysis step {step_id}: {title}")
        print(f"  Objective: {objective}")
        print(f"  Source data from: {source_answer_ids}")
        
        # Collect CSV data from source answer IDs
        combined_csv_data = ""
        for answer_id in source_answer_ids:
            if answer_id in fetched_data:
                data_info = fetched_data[answer_id]
                if 'raw_csv' in data_info:
                    combined_csv_data += f"\n--- Data from {answer_id} ---\n"
                    combined_csv_data += data_info['raw_csv']
                    combined_csv_data += "\n"
                else:
                    print(f"⚠️ No raw CSV data found for {answer_id}")
            else:
                print(f"⚠️ No data found for source answer ID: {answer_id}")
        
        if not combined_csv_data.strip():
            print(f"❌ No CSV data available for step {step_id}")
            results[step_id] = {
                'error': 'No CSV data available',
                'step_id': step_id,
                'title': title
            }
            continue
        
        # Create analysis prompt
        analysis_prompt = f"""
Analysis Task: {title}

Objective: {objective}

Key Questions to Answer:
{key_insights_questions}

Instructions:
1. Analyze the provided CSV data thoroughly
2. Answer the key questions listed above
3. Provide specific insights, trends, and patterns
4. Include relevant numbers, percentages, and statistics
5. Highlight any concerning trends or positive developments
6. Provide actionable recommendations if applicable

Format your response in a clear, structured manner with headings and bullet points where appropriate.
"""
        
        try:
            # Call LLM for analysis
            print(f"🤖 Calling {llm_provider.upper()} for analysis...")
            print(f"📊 Data size: {len(combined_csv_data)} characters")
            print("⏳ Waiting for LLM analysis... (this may take 1-3 minutes)")
            
            analysis_result = call_llm_for_analysis(analysis_prompt, combined_csv_data, llm_provider)
            
            results[step_id] = {
                'step_id': step_id,
                'title': title,
                'objective': objective,
                'source_answer_ids': source_answer_ids,
                'analysis_result': analysis_result,
                'csv_data_length': len(combined_csv_data)
            }
            
            print(f"✅ Analysis completed for step {step_id}")
            
        except Exception as e:
            print(f"❌ Error analyzing step {step_id}: {e}")
            results[step_id] = {
                'error': str(e),
                'step_id': step_id,
                'title': title
            }
    
    return results