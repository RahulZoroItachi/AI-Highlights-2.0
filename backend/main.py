#!/usr/bin/env python3
"""
Main workflow script that replicates the n8n workflow:
1. Generate metadata table prompt
2. Send to LLM with output format prompt
3. Parse and validate metadata output
4. Generate analysis plan prompt with metadata
5. Send to LLM and parse plan output
6. Print the final plan
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Override print to ensure output is flushed immediately
original_print = print
def print(*args, **kwargs):
    original_print(*args, **kwargs)
    sys.stdout.flush()

import google.generativeai as genai
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv()

from prompts import (
    get_metadata_prompt_with_format,
    get_plan_prompt_with_format,
    get_plan_splitter_with_format,
)
from invoke_api import execute_data_fetch_from_plan
from analysis import execute_analysis_plan
from run_logger import get_scenario_logger, get_scenario_logger_with_append


def call_gemini_pro(system_prompt: str, output_format_prompt: str, user_message: str = "") -> str:
    """
    Call Google Gemini Pro 2.5 with API key.
    
    Args:
        system_prompt: Main system prompt
        output_format_prompt: Output format specification
        user_message: Optional user message
        
    Returns:
        LLM response as string
    """
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    # Combine prompts
    full_prompt = f"{system_prompt}\n\n{output_format_prompt}"
    if user_message:
        full_prompt += f"\n\nUser Message: {user_message}"
    
    try:
        print("🤖 Calling Gemini Pro 2.5...")
        print(f"🔧 Debug: Prompt length: {len(full_prompt)}")
        print("⏳ Waiting for Gemini response... (this may take 1-3 minutes)")
        
        response = model.generate_content(full_prompt)
        
        print("✅ Gemini response received successfully")
        print(f"🔧 Debug: Response length: {len(response.text) if response.text else 0}")
        return response.text
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        raise


def call_claude_sonnet(system_prompt: str, output_format_prompt: str, user_message: str = "") -> str:
    """
    Call Claude Sonnet 4 with API key.
    
    Args:
        system_prompt: Main system prompt
        output_format_prompt: Output format specification
        user_message: Optional user message
        
    Returns:
        LLM response as string
    """
    # Get API key from environment
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        raise ValueError("CLAUDE_API_KEY environment variable not set")
    
    # Initialize Claude client
    client = Anthropic(api_key=api_key)
    
    # Combine prompts
    full_prompt = f"{system_prompt}\n\n{output_format_prompt}"
    
   

    
    if user_message:
        full_prompt += f"\n\nUser Message: {user_message}"

    #print("***********  ***********")
    #print(full_prompt)
    #print("***********  ***********")
    #input("Enter your message for Claude (leave blank for none): ")
    
    try:
        print("🤖 Calling Claude Sonnet 4...")
        print("⏳ Waiting for Claude response... (this may take 1-3 minutes)")
        
        response = client.messages.create(
            #model="claude-sonnet-4-20250514",
            model="claude-sonnet-4-5-20250929",
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
        
        print("✅ Claude response started, processing stream...")
        
        # Handle streaming response
        full_response = ""
        chunk_count = 0
        last_progress_time = time.time()
        
        for chunk in response:
            if chunk.type == "content_block_delta":
                full_response += chunk.delta.text
                chunk_count += 1
        
        print(f"✅ Claude response completed. Total length: {len(full_response)}")
        return full_response
    except Exception as e:
        print(f"❌ Error calling Claude: {e}")
        raise


def call_llm(system_prompt: str, output_format_prompt: str = "", user_message: str = "", llm_provider: str = "gemini") -> str:
    """
    Unified LLM calling function that routes to the appropriate provider.
    
    Args:
        system_prompt: Main system prompt
        output_format_prompt: Output format specification
        user_message: Optional user message
        llm_provider: Either "gemini" or "claude"
        
    Returns:
        LLM response as string
    """
    if llm_provider.lower() == "gemini":
        return call_gemini_pro(system_prompt, output_format_prompt, user_message)
    elif llm_provider.lower() == "claude":
        return call_claude_sonnet(system_prompt, output_format_prompt, user_message)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}. Use 'gemini' or 'claude'")



def main():
    """Main workflow execution."""
    print("🚀 Starting AI Analysis...")
    print("   Analyzing your ThoughtSpot data with AI insights")
    
    # Validate critical environment variables early
    print("🔧 Checking configuration...")
    required_base_vars = ['THOUGHTSPOT_BASE_URL', 'THOUGHTSPOT_AUTH_TOKEN']
    missing_vars = []
    
    for var in required_base_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Configuration incomplete: Missing {', '.join(missing_vars)}")
        print("💡 Please check your API keys and ThoughtSpot settings in the Settings tab")
        return
    
    print("✅ Configuration validated")
    
    # Configuration - can be overridden by environment variables
    scenario = os.getenv('ANALYSIS_SCENARIO', "support")  # Change this to 'pg', 'ta', 'cmo' as needed
    llm_provider = os.getenv('LLM_PROVIDER', "claude")  # Change to "claude" to use Claude Sonnet 4
    load_previous_plan = os.getenv('LOAD_PREVIOUS_PLAN') or None  # Set to version number to load previous plan, None to generate new
    load_previous_data = os.getenv('LOAD_PREVIOUS_DATA') or None  # Set to version number to load previous data, None to fetch fresh data
    report_analysis_version = os.getenv('REPORT_ANALYSIS_VERSION') or None  # Set to version number to use specific analysis for report, None to use latest
    
    print(f"🔧 Configuration loaded: scenario={scenario}, llm_provider={llm_provider}")
    
    # Validate LLM provider API key
    llm_api_key_var = 'CLAUDE_API_KEY' if llm_provider.lower() == 'claude' else 'GEMINI_API_KEY'
    if not os.getenv(llm_api_key_var):
        print(f"❌ Missing {llm_provider.upper()} API key: {llm_api_key_var}")
        print("💡 Make sure your .env file contains the correct API key")
        return
    
    print(f"✅ {llm_provider.upper()} API key validated")
    
    # Convert string values to int if they're numeric
    if load_previous_plan and load_previous_plan.isdigit():
        load_previous_plan = int(load_previous_plan)
    if load_previous_data and load_previous_data.isdigit():
        load_previous_data = int(load_previous_data)
    if report_analysis_version and report_analysis_version.isdigit():
        report_analysis_version = int(report_analysis_version)
    
    # Initialize run logger for this scenario (will be overridden for partial executions)
    logger = get_scenario_logger(scenario)
    
    # Show available versions for easy selection (concise view)
    previous_runs = logger.list_previous_runs()
    
    if not previous_runs['plans'] and not previous_runs['data'] and not previous_runs['analysis']:
        print("🆕 This is the first run for this scenario")
    else:
        print(f"📊 Previous runs available: {len(previous_runs['plans'])} plans, {len(previous_runs['data'])} data files, {len(previous_runs['analysis'])} analyses")
    
    # Display current configuration
    print(f"\n⚙️ Current Configuration:")
    print(f"  Scenario: {scenario}")
    print(f"  LLM Provider: {llm_provider}")
    print(f"  Load Previous Plan: {load_previous_plan if load_previous_plan is not None else 'None (generate new)'}")
    print(f"  Load Previous Data: {load_previous_data if load_previous_data is not None else 'None (fetch fresh)'}")
    print(f"  Report Analysis Version: {report_analysis_version if report_analysis_version is not None else 'Latest'}")
    
    try:
        # Initialize variables
        fetched_data = None
        llm_response_3 = None
        analysis_results = None
        
        # Determine workflow mode based on flags
        if report_analysis_version is not None:
            # SCENARIO: Analysis version provided - only run reporting
            print("\n📊 REPORT-ONLY MODE: Creating report from previous analysis...")
            print("   Using existing analysis results to generate a new report")
            print("📋 Preparing report...")
            
            # Use append mode to add files to the existing version
            logger = get_scenario_logger_with_append(scenario, report_analysis_version)
            print(f"📁 Using append mode for version {report_analysis_version}")
            
            # Set analysis_results to None to trigger file loading in reporting step
            analysis_results = None
            
        elif load_previous_data is not None:
            # SCENARIO: Data version provided - run analysis and reporting
            print("\n📊 QUICK-RUN MODE: Using previous data...")
            print("   Loading existing data and running fresh analysis")
            print("📋 Preparing analysis...")
            
            # Use append mode to add files to the existing version
            logger = get_scenario_logger_with_append(scenario, load_previous_data)
            print(f"📁 Using append mode for version {load_previous_data}")
            
            fetched_data = logger.load_data(load_previous_data)
            if fetched_data is None:
                print("❌ Failed to load previous data, exiting")
                return
            
            # Load the corresponding plan for analysis
            llm_response_3 = logger.load_plan(load_previous_data)
            if llm_response_3 is None:
                print("❌ Failed to load corresponding plan, exiting")
                return
            
            print("✅ Previous data and plan loaded successfully")
            
            # Check if the loaded plan is already parsed or needs parsing
            from invoke_api import parse_final_analysis_plan
            
            # Check if it's already in the parsed format (has primaryGoal, phases, etc.)
            if 'primaryGoal' in llm_response_3 and 'phases' in llm_response_3:
                print("📊 Loaded plan is already in parsed format")
                execution_plan = llm_response_3
            else:
                print("📊 Parsing loaded plan from raw format")
                execution_plan = parse_final_analysis_plan(llm_response_3)
            
            if not execution_plan:
                print("❌ Failed to parse loaded plan")
                return
            
            # Extract analysis steps from the execution plan with their fetch step mapping
            analysis_steps = []
            phases = execution_plan.get('phases', [])
            for phase in phases:
                # Get analysis steps from the phase level
                phase_analysis_steps = phase.get('analysisSteps', [])
                fetch_steps = phase.get('fetchSteps', [])
                
                # Map analysis steps to their corresponding fetch steps
                for analysis_step in phase_analysis_steps:
                    # Try to find the corresponding fetch step by matching stepId patterns
                    analysis_step_id = analysis_step.get('stepId', '')
                    fetch_step_id = ''
                    
                    # Look for a fetch step that matches the analysis step pattern
                    # e.g., analysis step "1.1.1" should map to fetch step "1.1"
                    if '.' in analysis_step_id:
                        base_id = analysis_step_id.rsplit('.', 1)[0]  # Get "1.1" from "1.1.1"
                        for fetch_step in fetch_steps:
                            if fetch_step.get('stepId', '') == base_id:
                                fetch_step_id = base_id
                                break
                    
                    # Add the fetch step ID to the analysis step
                    analysis_step['fetchStepId'] = fetch_step_id
                    analysis_steps.append(analysis_step)
            
            print(f"📊 Found {len(analysis_steps)} analysis steps in loaded plan")
            
            analysis_results = {}
            
            for analysis_step in analysis_steps:
                step_id = analysis_step.get('stepId', 'unknown')
                fetch_step_id = analysis_step.get('fetchStepId', '')
                
                # Get the corresponding fetched data
                if fetch_step_id in fetched_data:
                    fetch_data = fetched_data[fetch_step_id]
                    if 'error' not in fetch_data:
                        # Prepare data for analysis
                        csv_data = fetch_data.get('raw_csv', '')
                        headers = fetch_data.get('headers', [])
                        parsed_data = fetch_data.get('data', [])
                        
                        if csv_data or parsed_data:
                            analysis_results[step_id] = {
                                'stepId': step_id,
                                'title': analysis_step.get('title', ''),
                                'question': analysis_step.get('question', ''),
                                'fetchStepId': fetch_step_id,
                                'groupBy': analysis_step.get('groupBy', ''),
                                'aggregation': analysis_step.get('aggregation', ''),
                                'analysisPrompt': analysis_step.get('analysisPrompt', ''),
                                'csvData': csv_data,
                                'dataRows': len(parsed_data),
                                'headers': headers,
                                'status': 'ready_for_analysis'
                            }
                        else:
                            analysis_results[step_id] = {
                                'error': 'No data available for analysis',
                                'stepId': step_id,
                                'title': analysis_step.get('title', ''),
                                'question': analysis_step.get('question', ''),
                                'fetchStepId': fetch_step_id
                            }
                    else:
                        analysis_results[step_id] = {
                            'error': f'Fetch step error: {fetch_data["error"]}',
                            'stepId': step_id,
                            'title': analysis_step.get('title', ''),
                            'question': analysis_step.get('question', ''),
                            'fetchStepId': fetch_step_id
                        }
                else:
                    analysis_results[step_id] = {
                        'error': f'No data found for fetch step {fetch_step_id}',
                        'stepId': step_id,
                        'title': analysis_step.get('title', ''),
                        'question': analysis_step.get('question', ''),
                        'fetchStepId': fetch_step_id
                    }
            
            print(f"📊 Prepared {len(analysis_results)} analysis steps from loaded data")
            
        elif load_previous_plan is not None:
            # SCENARIO: Plan version provided - fetch data, run analysis and reporting
            print(f"\n📖 PLAN-LOADED MODE: Loading previous plan version {load_previous_plan}...")
            print("🔄 Skipping plan generation")
            print("📋 Proceeding to data fetch, analysis, and reporting...")
            
            # Use append mode to add files to the existing version
            logger = get_scenario_logger_with_append(scenario, load_previous_plan)
            print(f"📁 Using append mode for version {load_previous_plan}")
            
            execution_plan = logger.load_plan(load_previous_plan)
            if execution_plan is None:
                print("❌ Failed to load previous plan, falling back to full execution")
                load_previous_plan = None  # Reset to full execution
                # Fall through to Scenario 1
            
            if execution_plan is not None:
                print("✅ Previous plan loaded successfully")
                
                # Execute the final analysis plan (fetch data and prepare analysis)
                print("\n🚀 Executing Final Analysis Plan...")
                from invoke_api import execute_final_analysis_plan
                
                execution_results = execute_final_analysis_plan(execution_plan, scenario)
                
                if execution_results:
                    fetched_data = execution_results.get('fetched_data', {})
                    analysis_results = execution_results.get('analysis_results', {})
                    summary = execution_results.get('summary', {})
                    
                    print(f"\n📊 Execution Results Summary:")
                    print(f"  - Fetch Steps: {summary.get('successful_fetch_steps', 0)}/{summary.get('total_fetch_steps', 0)} successful")
                    print(f"  - Analysis Steps: {summary.get('ready_analysis_steps', 0)}/{summary.get('total_analysis_steps', 0)} ready")
                    
                    print(f"\n📊 Data Fetch Results:")
                    for step_id, result in fetched_data.items():
                        if 'error' not in result:
                            print(f"  {step_id}: {result.get('row_count', 0)} rows")
                        else:
                            print(f"  {step_id}: Error - {result['error']}")
                else:
                    print("⚠️ No execution results")
                    fetched_data = {}
                    analysis_results = {}
                
                # Save data to JSON and text files
                if fetched_data:
                    print("\n📊 Saving Data...")
                    try:
                        # Save complete data as JSON
                        json_result = logger.save_data_to_json(fetched_data)
                        print(f"✅ Complete data saved to JSON: {json_result}")
                        
                        # Also save summary as text
                        text_result = logger.save_data_to_text(fetched_data)
                        print(f"✅ Data summary saved to text: {text_result}")
                        
                    except Exception as e:
                        print(f"⚠️ Failed to save data: {e}")
                        print("Continuing with analysis...")
        
        if load_previous_plan is None and load_previous_data is None and report_analysis_version is None:
            # SCENARIO 1: Full execution - generate plan, fetch data, run analysis
            print("\n🆕 FULL ANALYSIS MODE: Creating complete new analysis...")
            print("   This will generate a new plan, fetch data, and run analysis")
            
            # Step 1: Generate the metadata table prompt
            print("\n📋 Step 1: Understanding your data structure...")
            metadata_prompt, table_system_prompt = get_metadata_prompt_with_format(scenario)
            print(f"✅ Analyzed data structure for scenario: {scenario}")
            
            # Step 2: Send to LLM with output format prompt
            print(f"\n🤖 Step 2: Getting AI insights on your data...")
            print("   AI is analyzing your data to understand patterns")
            
            try:
                llm_response_1 = call_llm(metadata_prompt, user_message=table_system_prompt, llm_provider=llm_provider)
                print("✅ AI insights received successfully")
            except Exception as e:
                print(f"❌ Failed to get AI insights: {e}")
                print("💡 This might be a temporary issue. Please try again or check your API connection.")
                raise
            
            # Step 3: Parse and validate metadata output
            print("\n🔍 Step 3: Processing AI insights...")
            try:
                parsed_metadata = llm_response_1
                print("✅ AI insights processed successfully")
            except Exception as e:
                print(f"❌ Error parsing metadata output: {e}")
                return
            
            # Step 4: Generate final analysis plan prompt with metadata
            print("\n📋 Step 4: Generating final analysis plan prompt...")
            from prompts import final_prompt, final_output_format
            final_plan_prompt = final_prompt(scenario, llm_response_1)
            final_output_format_prompt = final_output_format()
            print("✅ Final analysis plan prompt generated with metadata")
            
            # Step 5: Send final prompt to LLM and parse output
            print(f"\n🤖 Step 5: Sending final prompt to {llm_provider.upper()}...")
            llm_response_2_raw = call_llm(final_plan_prompt, final_output_format_prompt, llm_provider=llm_provider)
            print("✅ Final plan LLM response received")
            
            # Parse the JSON string response
            print("\n🔍 Step 5.5: Parsing JSON response...")
            print(f"📊 Raw response length: {len(llm_response_2_raw)}")
            
            import json
            try:
                llm_response_2 = json.loads(llm_response_2_raw)
                print("✅ JSON response parsed successfully")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"🔧 Debug: Error position: {e.pos}")
                if e.pos < len(llm_response_2_raw):
                    error_context_start = max(0, e.pos - 50)
                    error_context_end = min(len(llm_response_2_raw), e.pos + 50)
                    error_context = llm_response_2_raw[error_context_start:error_context_end]
                    print(f"🔧 Debug: Error context: {repr(error_context)}")
                
                print("📊 Trying to use parse_llm_output instead...")
                from prompts import parse_llm_output
                try:
                    llm_response_2 = parse_llm_output(llm_response_2_raw)
                    print("✅ Response parsed using parse_llm_output")
                except Exception as parse_error:
                    print(f"❌ parse_llm_output also failed: {parse_error}")
                    print(f"🔧 Debug: parse_llm_output error type: {type(parse_error).__name__}")
                    
                    # Try to find JSON boundaries manually
                    print("🔧 Debug: Trying manual JSON extraction...")
                    start_idx = llm_response_2_raw.find('{')
                    end_idx = llm_response_2_raw.rfind('}')
                    print(f"🔧 Debug: JSON boundaries - start: {start_idx}, end: {end_idx}")
                    
                    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                        json_portion = llm_response_2_raw[start_idx:end_idx + 1]
                        print(f"🔧 Debug: Extracted JSON length: {len(json_portion)}")
                        print(f"🔧 Debug: Extracted JSON first 100 chars: {repr(json_portion[:100])}")
                        print(f"🔧 Debug: Extracted JSON last 100 chars: {repr(json_portion[-100:])}")
                        
                        try:
                            llm_response_2 = json.loads(json_portion)
                            print("✅ Manual JSON extraction successful")
                        except json.JSONDecodeError as manual_error:
                            print(f"❌ Manual JSON extraction failed: {manual_error}")
                            raise parse_error
                    else:
                        print("🔧 Debug: No valid JSON boundaries found")
                        raise parse_error
            
            # Step 6: Parse final plan and extract execution plan
            print("\n🔍 Step 6: Parsing final plan and extracting execution plan...")
            from invoke_api import parse_final_analysis_plan
            execution_plan = parse_final_analysis_plan(llm_response_2)
            
            if not execution_plan:
                print("❌ Failed to parse final analysis plan")
                return
            
            print("✅ Final analysis plan parsed successfully")
            
            # Save the final plan
            print("\n💾 Saving final plan...")
            plan_file_path = logger.save_plan(execution_plan)
            print(f"📄 Final plan saved to: {plan_file_path}")
            
            # Step 7: Execute final analysis plan (fetch data and prepare analysis)
            print("\n🚀 Step 7: Executing Final Analysis Plan...")
            from invoke_api import execute_final_analysis_plan
            
            execution_results = execute_final_analysis_plan(execution_plan, scenario)
            
            if execution_results:
                fetched_data = execution_results.get('fetched_data', {})
                analysis_results = execution_results.get('analysis_results', {})
                summary = execution_results.get('summary', {})
                
                print(f"\n📊 Execution Results Summary:")
                print(f"  - Fetch Steps: {summary.get('successful_fetch_steps', 0)}/{summary.get('total_fetch_steps', 0)} successful")
                print(f"  - Analysis Steps: {summary.get('ready_analysis_steps', 0)}/{summary.get('total_analysis_steps', 0)} ready")
                
                print(f"\n📊 Data Fetch Results:")
                for step_id, result in fetched_data.items():
                    if 'error' not in result:
                        print(f"  {step_id}: {result.get('row_count', 0)} rows")
                    else:
                        print(f"  {step_id}: Error - {result['error']}")
            else:
                print("⚠️ No execution results")
                fetched_data = {}
                analysis_results = {}
            
            # Step 8: Save data to JSON and text files
            if fetched_data:
                print("\n📊 Step 8: Saving Data...")
                try:
                    # Save complete data as JSON
                    json_result = logger.save_data_to_json(fetched_data)
                    print(f"✅ Complete data saved to JSON: {json_result}")
                    
                    # Also save summary as text
                    text_result = logger.save_data_to_text(fetched_data)
                    print(f"✅ Data summary saved to text: {text_result}")
                    
                except Exception as e:
                    print(f"⚠️ Failed to save data: {e}")
                    print("Continuing with analysis...")

        # Step 9: Execute analysis (skip if in analysis-only mode)
        if analysis_results and report_analysis_version is None:
            print("\n📊 Step 9: Executing Analysis...")
            
            # The analysis results are already prepared from Step 7
            # Now we need to actually call the LLM for each analysis step
            from analysis import call_llm_for_analysis
            
            final_analysis_results = {}
            
            for step_id, analysis_data in analysis_results.items():
                if 'error' in analysis_data:
                    print(f"⚠️ Skipping analysis step {step_id}: {analysis_data['error']}")
                    final_analysis_results[step_id] = analysis_data
                    continue
                
                if analysis_data.get('status') != 'ready_for_analysis':
                    print(f"⚠️ Skipping analysis step {step_id}: Not ready for analysis")
                    final_analysis_results[step_id] = analysis_data
                    continue
                
                print(f"\n🔍 Executing analysis step {step_id}:")
                print(f"  Title: {analysis_data.get('title', 'N/A')}")
                print(f"  Question: {analysis_data.get('question', 'N/A')}")
                
                try:
                    # Call LLM for analysis
                    print(f"🤖 Calling {llm_provider.upper()} for analysis step {step_id}...")
                    print("⏳ Waiting for LLM analysis... (this may take 1-3 minutes)")
                    
                    analysis_prompt = analysis_data.get('analysisPrompt', '')
                    csv_data = analysis_data.get('csvData', '')
                    analysis_response = call_llm_for_analysis(analysis_prompt, csv_data, llm_provider)
                    
                    final_analysis_results[step_id] = {
                        'stepId': step_id,
                        'title': analysis_data.get('title', ''),
                        'question': analysis_data.get('question', ''),
                        'fetchStepId': analysis_data.get('fetchStepId', ''),
                        'analysisResponse': analysis_response,
                        'status': 'completed'
                    }
                    
                    print(f"✅ Analysis step {step_id} completed")
                    
                except Exception as e:
                    print(f"❌ Error executing analysis step {step_id}: {e}")
                    final_analysis_results[step_id] = {
                        'stepId': step_id,
                        'title': analysis_data.get('title', ''),
                        'question': analysis_data.get('question', ''),
                        'fetchStepId': analysis_data.get('fetchStepId', ''),
                        'error': str(e),
                        'status': 'failed'
                    }
            
            print(f"\n📊 Final Analysis Results Summary:")
            for step_id, result in final_analysis_results.items():
                if 'error' not in result and result.get('status') == 'completed':
                    print(f"  {step_id}: {result.get('title', 'Unknown')} - Analysis completed")
                else:
                    print(f"  {step_id}: Error - {result.get('error', 'Unknown error')}")
            
            # Save analysis results to file
            analysis_file_path = logger.save_analysis_results(final_analysis_results)
            print(f"\n💾 Analysis results saved to: {analysis_file_path}")
            
        elif report_analysis_version is not None:
            print("\n📊 Step 9: Skipping analysis execution (analysis-only mode)")
            
        else:
            print("⚠️ No analysis results to execute")
        
        # Step 10: Generate Executive Report
        if analysis_results or report_analysis_version is not None:
            print("\n📊 Step 10: Generating Executive Report...")
            
            # Load analysis results if we have them from execution
            if isinstance(analysis_results, dict) and any('analysisResponse' in result for result in analysis_results.values()):
                # Analysis results are already in the correct format
                analysis_data = []
                for step_id, result in analysis_results.items():
                    if isinstance(result, dict) and 'analysisResponse' in result:
                        analysis_data.append({
                            'stepId': step_id,
                            'title': result.get('title', ''),
                            'question': result.get('question', ''),
                            'analysisResponse': result.get('analysisResponse', ''),
                            'status': result.get('status', 'completed')
                        })
            else:
                # Load analysis results from file if available
                try:
                    # Use the existing logger (preserves append mode if set)
                    previous_runs = logger.list_previous_runs()
                    
                    if previous_runs['analysis']:
                        # Determine which analysis file to load
                        if report_analysis_version is not None:
                            # Load specific analysis version - look for analysis files in the specific version directory
                            version_dir_pattern = f"{scenario}_v{report_analysis_version:03d}"
                            matching_analysis = [f for f in previous_runs['analysis'] if version_dir_pattern in f]
                            
                            if matching_analysis:
                                analysis_file = sorted(matching_analysis)[-1]  # Get latest if multiple matches
                                print(f"📖 Loading analysis results from version {report_analysis_version}: {analysis_file}")
                            else:
                                print(f"⚠️ Analysis version {report_analysis_version} not found, using latest")
                                analysis_file = previous_runs['analysis'][-1]
                                print(f"📖 Fallback: Loading latest analysis file: {analysis_file}")
                        else:
                            # Load the latest analysis file
                            analysis_file = previous_runs['analysis'][-1]
                            print(f"📖 Loading latest analysis results from: {analysis_file}")
                        
                        print(f"🎯 Selected analysis file: {analysis_file}")
                        print(f"📄 File basename: {os.path.basename(analysis_file)}")
                        
                        import json
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            analysis_json = json.load(f)
                        
                        from prompts import analysis_json_extractor
                        analysis_data = analysis_json_extractor(analysis_json)
                        print(f"✅ Loaded {len(analysis_data)} analysis results from file")
                    else:
                        print("⚠️ No analysis files found, skipping report generation")
                        analysis_data = []
                except Exception as e:
                    print(f"⚠️ Error loading analysis results: {e}")
                    analysis_data = []
            
            if analysis_data:
                try:
                    from prompts import report_prompt, report_system_prompt
                    from analysis import call_llm_for_analysis
                    
                    # Generate report prompt
                    report_prompt_text = report_prompt(analysis_data, scenario, llm_provider)
                    system_prompt = report_system_prompt()
                    
                    print("🤖 Generating executive report...")
                    print(f"📊 Processing {len(analysis_data)} analysis results")
                    
                    # Call LLM to generate the report
                    report_response = call_llm_for_analysis(report_prompt_text, "", llm_provider)
                    
                    if report_response:
                        print("✅ Executive report generated successfully")
                        
                        # Save the report to a file using the logger
                        try:
                            report_content = f"EXECUTIVE REPORT - {scenario.upper()}\n"
                            report_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            report_content += "="*80 + "\n\n"
                            report_content += report_response
                            
                            report_path = logger.save_report(report_content)
                            print(f"📄 Report saved to: {report_path}")
                        except Exception as e:
                            print(f"⚠️ Error saving report: {e}")
                            print("📄 Report content:")
                            print("-" * 80)
                            print(report_response)
                            print("-" * 80)
                    else:
                        print("❌ Failed to generate executive report")
                        
                except Exception as e:
                    print(f"❌ Error generating report: {e}")
            else:
                print("⚠️ No analysis data available for report generation")
        else:
            print("⚠️ No analysis results available for report generation")
        
        print("\n🎉 Workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        raise


if __name__ == "__main__":
    main()
