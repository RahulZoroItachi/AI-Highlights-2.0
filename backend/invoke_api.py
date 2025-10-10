#!/usr/bin/env python3
"""
API invocation module for ThoughtSpot integration.
Handles data fetching and analysis execution based on the split plans.
"""

import json
import os
import requests
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv
from inputs import scenario_pg, scenario_support, scenario_ta, scenario_cmo

# Load environment variables
load_dotenv()


class ThoughtSpotAPI:
    """ThoughtSpot API client for data fetching and analysis."""
    
    def __init__(self):
        """Initialize the ThoughtSpot API client."""
        self.base_url = os.getenv('THOUGHTSPOT_BASE_URL')
        self.auth_token = os.getenv('THOUGHTSPOT_AUTH_TOKEN')
        
        if not self.base_url:
            raise ValueError("Missing required environment variable: THOUGHTSPOT_BASE_URL")
        if not self.auth_token:
            raise ValueError("Missing required environment variable: THOUGHTSPOT_AUTH_TOKEN")
        
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_worksheet_id(self, scenario: str) -> str:
        """
        Get worksheet ID for a specific scenario.
        
        Args:
            scenario: One of 'pg', 'support', 'ta', 'cmo'
            
        Returns:
            Worksheet ID for the scenario
        """
        scenario_functions = {
            'pg': scenario_pg,
            'support': scenario_support,
            'ta': scenario_ta,
            'cmo': scenario_cmo,
        }
        
        if scenario not in scenario_functions:
            raise ValueError(f"Unknown scenario: {scenario}. Must be one of: {list(scenario_functions.keys())}")
        
        inputs = scenario_functions[scenario]()
        return inputs.get('Worksheet_ID', '')
    
    def create_answer(self, prompt: str, scenario: str) -> Dict[str, Any]:
        """
        Create an answer using ThoughtSpot's AI/answer/create endpoint.
        
        Args:
            prompt: Natural language query for data fetching
            scenario: Scenario to determine worksheet ID
            
        Returns:
            API response containing answer details
        """
        worksheet_id = self.get_worksheet_id(scenario)
        
        url = f"{self.base_url}/api/rest/2.0/ai/answer/create"
        
        payload = {
            "query": prompt,
            "metadata_identifier": worksheet_id
        }
        
        try:
            print(f"🤖 Creating answer with prompt: {prompt[:100]}...")
            print(f"📋 Using worksheet ID: {worksheet_id}")
            print("⏳ Sending request to ThoughtSpot... (this may take 30-60 seconds)")
            
            # Print curl command for debugging
            curl_command = f"""curl -X POST '{url}' \\
  -H 'Accept: application/json' \\
  -H 'Authorization: Bearer {self.headers['Authorization'].replace('Bearer ', '')}' \\
  -H 'Content-Type: application/json' \\
  -d '{json.dumps(payload)}'"""
            #print(f"🔧 CURL Command for API 1 (Create Answer):")
            #print(curl_command)
            #print()
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Answer created successfully")
            #print(f"📊 Response: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating answer: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            raise
    
    def get_answer_data(self, session_identifier: str, generation_number: int = None) -> Dict[str, Any]:
        """
        Get answer data using ThoughtSpot's report/answer endpoint.
        
        Args:
            session_identifier: Session identifier from the answer creation
            generation_number: Generation number from the answer creation
            
        Returns:
            Answer data including results and metadata
        """
        url = f"{self.base_url}/api/rest/2.0/report/answer"
        
        # This is a POST request with body parameters
        # Note: Do not include metadata_identifier for this API
        body = {
            "session_identifier": session_identifier,
            "file_format": "CSV"
        }
        
        if generation_number:
            body["generation_number"] = generation_number
        
        try:
            print(f"📊 Fetching data for session: {session_identifier}")
            print("⏳ Retrieving data from ThoughtSpot... (this may take 30-60 seconds)")
            
            # Try with form-encoded data instead of JSON
            headers = {
                'Authorization': self.headers['Authorization']
            }
            
            # Print curl command for debugging
            curl_command = f"""curl -X POST '{url}' \\
  -H 'Authorization: Bearer {self.headers['Authorization'].replace('Bearer ', '')}' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'session_identifier={session_identifier}&file_format=CSV&generation_number={generation_number}'"""
            #print(f"🔧 CURL Command for API 2 (Fetch Data):")
            #print(curl_command)
            #print()
            
            response = requests.post(url, headers=headers, data=body, timeout=30)
            response.raise_for_status()
            
            # The response will be mixed text and CSV data
            raw_response = response.text
            print(f"✅ Data fetched successfully: {len(raw_response)} characters")
            #print(f"📊 Response: {raw_response}")
            
            # Extract CSV portion from the mixed response
            lines = raw_response.strip().split('\n')
            
            # Skip first 4 rows (context) and start from 5th row (index 4) which contains headers
            if len(lines) >= 5:
                # Extract CSV data starting from the 5th row (index 4)
                csv_lines = lines[4:]  # Skip first 4 rows, start from 5th row
                csv_data = '\n'.join(csv_lines)
                print(f"📊 Extracted CSV from row 5 onwards: {len(csv_data)} characters")
                print(f"📊 Total lines in response: {len(lines)}, CSV lines: {len(csv_lines)}")
            else:
                print("⚠️ Response has fewer than 5 rows, using entire response")
                csv_data = raw_response
            
            # Parse CSV data into a more usable format
            import io
            import csv
            
            try:
                csv_reader = csv.DictReader(io.StringIO(csv_data))
                rows = list(csv_reader)
                
                # Get headers from the CSV
                headers = csv_reader.fieldnames if csv_reader.fieldnames else []
                
                result = {
                    "data": rows,
                    "raw_csv": csv_data,
                    "headers": headers,
                    "row_count": len(rows)
                }
                
                #print(f"📊 Parsed {len(rows)} rows from CSV data")
                #print(f"📋 Headers: {headers}")
                #print(f"📋 CSV Data: {csv_data}")
                #input("Enter your message for Claude (leave blank for none): ")
                return result
                
            except Exception as e:
                print(f"⚠️ Error parsing CSV: {e}")
                # Return raw data if parsing fails
                result = {
                    "data": [],
                    "raw_csv": csv_data,
                    "headers": [],
                    "row_count": 0,
                    "parse_error": str(e)
                }
                return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching answer data: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            raise
    
    def execute_data_fetch_plan(self, data_fetch_plan: List[Dict[str, Any]], scenario: str) -> Dict[str, Any]:
        """
        Execute a complete data fetch plan.
        
        Args:
            data_fetch_plan: List of data fetch steps from the split plan
            scenario: Scenario to determine worksheet ID
            
        Returns:
            Dictionary mapping answer_ids to their data
        """
        results = {}
        
        print(f"\n🚀 Executing data fetch plan with {len(data_fetch_plan)} steps...")
        
        for step in data_fetch_plan:
            answer_id = step.get('answer_id', 'unknown')
            prompt = step.get('prompt', '')
            
            print(f"\n🔍 Processing step {answer_id}:")
            print(f"  Prompt: {prompt[:100]}...")
            
            if not prompt:
                print(f"⚠️ Skipping step {answer_id}: No prompt provided")
                continue
            
            try:
                # Create answer
                answer_response = self.create_answer(prompt, scenario)
                
                # Extract session_identifier and generation_number from response
                session_identifier = answer_response.get('session_identifier')
                generation_number = answer_response.get('generation_number')
                
                if not session_identifier:
                    print(f"❌ No session_identifier returned for step {answer_id}")
                    print(f"Response keys: {list(answer_response.keys())}")
                    continue
                
                print(f"📊 Using session_identifier: {session_identifier}")
                if generation_number:
                    print(f"📊 Using generation_number: {generation_number}")
                
                # Get answer data
                data_response = self.get_answer_data(session_identifier, generation_number)
                #print(f"📊 Data response: {data_response}")
                #input("Enter your message for Claude (leave blank for none): ")
                # Store results
                results[answer_id] = {
                    'answer_id': answer_id,  # This is the answer_id from the data fetch plan (e.g., "1.1", "2.1", "3.1")
                    'step_id': answer_id,
                    'original_phase_number': step.get('original_phase_number'),
                    'original_step_title': step.get('original_step_title'),
                    'raw_csv': data_response.get('raw_csv', ''),
                    'headers': data_response.get('headers', []),
                    'row_count': data_response.get('row_count', 0),
                    'session_identifier': session_identifier,
                    'generation_number': generation_number
                }
                
                print(f"✅ Step {answer_id} completed: {len(data_response.get('data', []))} rows")
                #print(f"📊 Data response: {data_response}")
                #input("Enter your message for Claude (leave blank for none): ")
                #break
            except Exception as e:
                print(f"❌ Error executing step {answer_id}: {e}")
                results[answer_id] = {
                    'answer_id': answer_id,
                    'step_id': answer_id,
                    'original_phase_number': step.get('original_phase_number'),
                    'original_step_title': step.get('original_step_title'),
                    'raw_csv': '',
                    'headers': [],
                    'row_count': 0,
                    'error': str(e)
                }
        
        #print(f"📊 Results: {results}")
        #input("Enter your message for Claude (leave blank for none): ")
        return results
    
    def execute_analysis_plan(self, analysis_plan: List[Dict[str, Any]], fetched_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis plan using the fetched data.
        
        Args:
            analysis_plan: List of analysis steps from the split plan
            fetched_data: Data from execute_data_fetch_plan
            
        Returns:
            Analysis results
        """
        results = {}
        
        print(f"\n📊 Executing analysis plan with {len(analysis_plan)} steps...")
        
        for step in analysis_plan:
            step_id = step.get('step', 'unknown')
            title = step.get('title', 'Untitled')
            source_answer_ids = step.get('source_answer_ids', [])
            
            print(f"\n🔍 Processing analysis step: {title}")
            
            # Collect data from source answers
            source_data = []
            for answer_id in source_answer_ids:
                if answer_id in fetched_data:
                    source_data.extend(fetched_data[answer_id].get('data', []))
                else:
                    print(f"⚠️ Source answer {answer_id} not found in fetched data")
            
            # Perform analysis based on step requirements
            analysis_result = self._perform_analysis(step, source_data)
            
            results[step_id] = {
                'title': title,
                'objective': step.get('objective', ''),
                'source_answer_ids': source_answer_ids,
                'data_count': len(source_data),
                'analysis': analysis_result,
                'key_insights': step.get('key_insights_questions_answered', '')
            }
            
            print(f"✅ Analysis step {step_id} completed")
        
        return results
    
    def _perform_analysis(self, step: Dict[str, Any], data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform analysis on the provided data based on step requirements.
        
        Args:
            step: Analysis step configuration
            data: Raw data to analyze
            
        Returns:
            Analysis results
        """
        if not data:
            return {'error': 'No data available for analysis'}
        
        computations = step.get('computations', {})
        group_by = computations.get('group_by', [])
        aggregations = computations.get('aggregations', [])
        
        # Simple analysis - group and aggregate data
        if group_by:
            grouped_data = {}
            for row in data:
                key = tuple(str(row.get(col, '')) for col in group_by)
                if key not in grouped_data:
                    grouped_data[key] = []
                grouped_data[key].append(row)
            
            # Apply aggregations
            result = {}
            for key, group in grouped_data.items():
                key_str = ' | '.join(key)
                result[key_str] = self._apply_aggregations(group, aggregations)
            
            return {
                'grouped_by': group_by,
                'groups': result,
                'total_groups': len(grouped_data)
            }
        else:
            # No grouping - return summary statistics
            return {
                'total_rows': len(data),
                'columns': list(data[0].keys()) if data else [],
                'summary': 'No specific grouping or aggregation defined'
            }
    
    def _apply_aggregations(self, data: List[Dict[str, Any]], aggregations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply aggregations to a group of data.
        
        Args:
            data: Group of data to aggregate
            aggregations: List of aggregation configurations
            
        Returns:
            Aggregated results
        """
        results = {}
        
        for agg in aggregations:
            agg_type = agg.get('type', '').lower()
            column = agg.get('column', '')
            alias = agg.get('alias', f"{agg_type}_{column}")
            
            if not column:
                continue
            
            values = [row.get(column) for row in data if row.get(column) is not None]
            
            if not values:
                results[alias] = None
                continue
            
            if agg_type == 'count':
                results[alias] = len(values)
            elif agg_type == 'sum':
                try:
                    results[alias] = sum(float(v) for v in values if v != '')
                except (ValueError, TypeError):
                    results[alias] = None
            elif agg_type == 'average':
                try:
                    numeric_values = [float(v) for v in values if v != '']
                    results[alias] = sum(numeric_values) / len(numeric_values) if numeric_values else None
                except (ValueError, TypeError):
                    results[alias] = None
            elif agg_type == 'max':
                try:
                    results[alias] = max(float(v) for v in values if v != '')
                except (ValueError, TypeError):
                    results[alias] = None
            elif agg_type == 'min':
                try:
                    results[alias] = min(float(v) for v in values if v != '')
                except (ValueError, TypeError):
                    results[alias] = None
            else:
                results[alias] = f"Unsupported aggregation: {agg_type}"
        
        return results


def execute_data_fetch_from_plan(llm_response: str, scenario: str) -> Dict[str, Any]:
    """
    Execute data fetch plan from the raw LLM response.
    
    Args:
        llm_response: Raw LLM response string containing JSON
        scenario: Scenario to determine worksheet ID
        
    Returns:
        Fetched data results
    """
    try:
        # Parse the LLM response to extract JSON
        import json
        
        # Parse the LLM response - handle both string and object inputs
        if isinstance(llm_response, str):
            try:
                # Try to parse as JSON first
                parsed_plan_splitter = json.loads(llm_response)
            except json.JSONDecodeError:
                # If not valid JSON, use the parse_llm_output function
                parsed_plan_splitter = llm_response
        else:
            # Already a dict/object
            parsed_plan_splitter = llm_response
        
        # Handle different JSON structures:
        # 1. Array with "output" wrapper: [{"output": {...}}]
        # 2. Direct object: {"data_fetch_plan": [...], "analysis_plan": [...]}
        if isinstance(parsed_plan_splitter, list) and len(parsed_plan_splitter) > 0:
            if 'output' in parsed_plan_splitter[0]:
                parsed_plan_splitter = parsed_plan_splitter[0]['output']
                print("📊 Extracted data from 'output' wrapper")
        elif isinstance(parsed_plan_splitter, dict):
            # Check if it's already in the correct format
            if 'data_fetch_plan' in parsed_plan_splitter:
                print("📊 Using direct object format")
            else:
                print("📊 Unknown object format, attempting to use as-is")
        
        # Initialize API client
        api = ThoughtSpotAPI()
        
        # Extract data fetch plan
        print(f"📊 Parsed plan keys: {list(parsed_plan_splitter.keys())}")
        data_fetch_plan = parsed_plan_splitter.get('data_fetch_plan', [])
        #analysis_plan = parsed_plan_splitter.get('analysis_plan', [])
        print(f"📋 Data fetch plan length: {len(data_fetch_plan)}")
        #print(f"📋 Analysis plan length: {len(analysis_plan)}")
        
        if not data_fetch_plan:
            print("⚠️ No data fetch plan found in parsed output")
            print(f"Available keys: {list(parsed_plan_splitter.keys())}")
            return {}
        
        # Execute data fetch plan
        print(f"\n🚀 Executing data fetch plan for scenario: {scenario}")
        fetched_data = api.execute_data_fetch_plan(data_fetch_plan, scenario)
        
        return fetched_data
        
    except Exception as e:
        print(f"❌ Error executing data fetch plan: {e}")
        return {}


def extract_analysis_plan_from_split_plan(llm_response: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract analysis plan from the split plan response using the same logic as data fetch plan.
    
    Args:
        llm_response: Raw LLM response string or parsed dict containing the split plan
        
    Returns:
        List of analysis plan steps
    """
    try:
        # Parse the LLM response - handle both string and object inputs
        if isinstance(llm_response, str):
            try:
                # Try to parse as JSON first
                parsed_plan_splitter = json.loads(llm_response)
            except json.JSONDecodeError:
                # If not valid JSON, use the parse_llm_output function
                parsed_plan_splitter = llm_response
        else:
            # Already a dict/object
            parsed_plan_splitter = llm_response
        
        # Handle different JSON structures:
        # 1. Array with "output" wrapper: [{"output": {...}}]
        # 2. Direct object: {"data_fetch_plan": [...], "analysis_plan": [...]}
        if isinstance(parsed_plan_splitter, list) and len(parsed_plan_splitter) > 0:
            if 'output' in parsed_plan_splitter[0]:
                parsed_plan_splitter = parsed_plan_splitter[0]['output']
                print("📊 Extracted analysis plan from 'output' wrapper")
        elif isinstance(parsed_plan_splitter, dict):
            # Check if it's already in the correct format
            if 'analysis_plan' in parsed_plan_splitter:
                print("📊 Using direct object format for analysis plan")
            else:
                print("📊 Unknown object format for analysis plan")
        
        # Extract analysis plan
        print(f"📊 Parsed plan keys: {list(parsed_plan_splitter.keys())}")
        analysis_plan = parsed_plan_splitter.get('analysis_plan', [])
        print(f"📋 Analysis plan length: {len(analysis_plan)}")
        
        return analysis_plan
        
    except Exception as e:
        print(f"❌ Error extracting analysis plan: {e}")
        return []


def parse_final_analysis_plan(final_plan_response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse the final analysis plan response to extract fetch steps and analysis steps.
    
    Args:
        final_plan_response: Raw LLM response string or parsed dict containing the final analysis plan
        
    Returns:
        Dictionary with structured data for execution
    """
    
    #print(f"📊 Final plan response: {final_plan_response}")
    try:
        # Parse the LLM response - handle both string and object inputs
        if isinstance(final_plan_response, str):
            try:
                # Try to parse as JSON first
                parsed_plan = json.loads(final_plan_response)
            except json.JSONDecodeError:
                # If not valid JSON, use the parse_llm_output function
                parsed_plan = final_plan_response
        else:
            # Already a dict/object
            parsed_plan = final_plan_response
        
        # Handle different JSON structures:
        # 1. Array with "output" wrapper: [{"output": {...}}]
        # 2. Direct object: {"analysisPlan": {...}}
        if isinstance(parsed_plan, list) and len(parsed_plan) > 0:
            if 'output' in parsed_plan[0]:
                parsed_plan = parsed_plan[0]['output']
                print("📊 Extracted final plan from 'output' wrapper")
        elif isinstance(parsed_plan, dict):
            # Check if it's already in the correct format
            if 'analysisPlan' in parsed_plan:
                print("📊 Using direct analysisPlan format")
            else:
                print("📊 Unknown object format for final plan")
        
        # Extract the analysis plan
        analysis_plan = parsed_plan.get('analysisPlan', {})
        
        # Structure the data for execution
        execution_plan = {
            'primaryGoal': analysis_plan.get('primaryGoal', ''),
            'assumptions': analysis_plan.get('assumptions', []),
            'phases': [],
            'fetchSteps': [],
            'analysisSteps': [],
            'fetchToAnalysisMapping': {}  # Maps fetch stepId to analysis stepIds
        }
        
        # Process each phase
        phases = analysis_plan.get('phases', [])
        for phase in phases:
            phase_data = {
                'phaseNumber': phase.get('phaseNumber'),
                'phaseTitle': phase.get('phaseTitle', ''),
                'phaseDescription': phase.get('phaseDescription', ''),
                'fetchSteps': [],
                'analysisSteps': []
            }
            
            # Process fetch steps within this phase
            fetch_steps = phase.get('fetchSteps', [])
            for fetch_step in fetch_steps:
                fetch_data = {
                    'stepId': fetch_step.get('stepId', ''),
                    'title': fetch_step.get('title', ''),
                    'objective': fetch_step.get('objective', ''),
                    'requiredData': fetch_step.get('requiredData', ''),
                    'fetchPrompt': fetch_step.get('fetchPrompt', ''),
                    'phaseNumber': phase.get('phaseNumber'),
                    'phaseTitle': phase.get('phaseTitle', '')
                }
                
                # Add to global fetch steps list
                execution_plan['fetchSteps'].append(fetch_data)
                phase_data['fetchSteps'].append(fetch_data)
                
                # Process analysis steps for this fetch step
                analysis_steps = fetch_step.get('analysisSteps', [])
                fetch_step_id = fetch_step.get('stepId', '')
                execution_plan['fetchToAnalysisMapping'][fetch_step_id] = []
                
                for analysis_step in analysis_steps:
                    analysis_data = {
                        'stepId': analysis_step.get('stepId', ''),
                        'title': analysis_step.get('title', ''),
                        'groupBy': analysis_step.get('groupBy', ''),
                        'aggregation': analysis_step.get('aggregation', ''),
                        'question': analysis_step.get('question', ''),
                        'analysisPrompt': analysis_step.get('analysisPrompt', ''),
                        'fetchStepId': fetch_step_id,  # Link to parent fetch step
                        'phaseNumber': phase.get('phaseNumber'),
                        'phaseTitle': phase.get('phaseTitle', '')
                    }
                    
                    # Add to global analysis steps list
                    execution_plan['analysisSteps'].append(analysis_data)
                    phase_data['analysisSteps'].append(analysis_data)
                    
                    # Add to mapping
                    execution_plan['fetchToAnalysisMapping'][fetch_step_id].append(analysis_step.get('stepId', ''))
            
            execution_plan['phases'].append(phase_data)
        
        print(f"📊 Parsed final plan:")
        print(f"  - Primary Goal: {execution_plan['primaryGoal']}")
        print(f"  - Phases: {len(execution_plan['phases'])}")
        print(f"  - Fetch Steps: {len(execution_plan['fetchSteps'])}")
        print(f"  - Analysis Steps: {len(execution_plan['analysisSteps'])}")
        print(f"  - Fetch-to-Analysis Mappings: {len(execution_plan['fetchToAnalysisMapping'])}")
        
        return execution_plan
        
    except Exception as e:
        print(f"❌ Error parsing final analysis plan: {e}")
        return {}


def execute_final_analysis_plan(execution_plan: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """
    Execute the final analysis plan by fetching data and performing analysis.
    
    Args:
        execution_plan: Parsed execution plan from parse_final_analysis_plan
        scenario: Scenario to determine worksheet ID
        
    Returns:
        Dictionary with fetched data and analysis results
    """
    try:
        print(f"\n🚀 Executing final analysis plan for scenario: {scenario}")
        print(f"📋 Primary Goal: {execution_plan.get('primaryGoal', 'N/A')}")
        
        # Initialize API client
        api = ThoughtSpotAPI()
        
        # Store fetched data with stepId as key
        fetched_data = {}
        analysis_results = {}
        
        # Execute fetch steps
        fetch_steps = execution_plan.get('fetchSteps', [])
        print(f"\n📊 Executing {len(fetch_steps)} fetch steps...")
        
        for i, fetch_step in enumerate(fetch_steps, 1):
            step_id = fetch_step.get('stepId', 'unknown')
            fetch_prompt = fetch_step.get('fetchPrompt', '')
            
            print(f"\n🔍 [{i}/{len(fetch_steps)}] Processing fetch step {step_id}:")
            print(f"  Title: {fetch_step.get('title', 'N/A')}")
            print(f"  Objective: {fetch_step.get('objective', 'N/A')}")
            print(f"  Prompt: {fetch_prompt[:100]}...")
            print(f"⏳ Starting data fetch... (this may take a few minutes)")
            
            if not fetch_prompt:
                print(f"⚠️ Skipping step {step_id}: No fetch prompt provided")
                continue
            
            try:
                print(f"⏳ Creating answer for step {step_id}... (API call in progress)")
                # Create answer
                answer_response = api.create_answer(fetch_prompt, scenario)
                
                if 'error' in answer_response:
                    print(f"❌ Error creating answer for step {step_id}: {answer_response['error']}")
                    fetched_data[step_id] = {
                        'error': answer_response['error'],
                        'stepId': step_id,
                        'title': fetch_step.get('title', ''),
                        'objective': fetch_step.get('objective', ''),
                        'phaseNumber': fetch_step.get('phaseNumber'),
                        'phaseTitle': fetch_step.get('phaseTitle', '')
                    }
                    continue
                
                print(f"⏳ Fetching data for step {step_id}... (retrieving results)")
                # Get answer data
                session_identifier = answer_response.get('session_identifier')
                generation_number = answer_response.get('generation_number')
                
                if not session_identifier or not generation_number:
                    print(f"❌ Missing session identifiers for step {step_id}")
                    fetched_data[step_id] = {
                        'error': 'Missing session identifiers',
                        'stepId': step_id,
                        'title': fetch_step.get('title', ''),
                        'objective': fetch_step.get('objective', ''),
                        'phaseNumber': fetch_step.get('phaseNumber'),
                        'phaseTitle': fetch_step.get('phaseTitle', '')
                    }
                    continue
                
                # Fetch the actual data
                data_response = api.get_answer_data(session_identifier, generation_number)
                
                if 'error' in data_response:
                    print(f"❌ Error fetching data for step {step_id}: {data_response['error']}")
                    fetched_data[step_id] = {
                        'error': data_response['error'],
                        'stepId': step_id,
                        'title': fetch_step.get('title', ''),
                        'objective': fetch_step.get('objective', ''),
                        'phaseNumber': fetch_step.get('phaseNumber'),
                        'phaseTitle': fetch_step.get('phaseTitle', '')
                    }
                    continue
                
                # Store the fetched data
                fetched_data[step_id] = {
                    'stepId': step_id,
                    'title': fetch_step.get('title', ''),
                    'objective': fetch_step.get('objective', ''),
                    'phaseNumber': fetch_step.get('phaseNumber'),
                    'phaseTitle': fetch_step.get('phaseTitle', ''),
                    'session_identifier': session_identifier,
                    'generation_number': generation_number,
                    'raw_csv': data_response.get('raw_csv', ''),
                    'headers': data_response.get('headers', []),
                    'data': data_response.get('data', []),
                    'row_count': data_response.get('row_count', 0)
                }
                
                print(f"✅ Step {step_id}: Fetched {data_response.get('row_count', 0)} rows")
                
            except Exception as e:
                print(f"❌ Error executing fetch step {step_id}: {e}")
                fetched_data[step_id] = {
                    'error': str(e),
                    'stepId': step_id,
                    'title': fetch_step.get('title', ''),
                    'objective': fetch_step.get('objective', ''),
                    'phaseNumber': fetch_step.get('phaseNumber'),
                    'phaseTitle': fetch_step.get('phaseTitle', '')
                }
        
        # Execute analysis steps
        analysis_steps = execution_plan.get('analysisSteps', [])
        print(f"\n📊 Executing {len(analysis_steps)} analysis steps...")
        
        for i, analysis_step in enumerate(analysis_steps, 1):
            step_id = analysis_step.get('stepId', 'unknown')
            fetch_step_id = analysis_step.get('fetchStepId', '')
            
            print(f"\n🔍 [{i}/{len(analysis_steps)}] Processing analysis step {step_id}:")
            print(f"  Title: {analysis_step.get('title', 'N/A')}")
            print(f"  Question: {analysis_step.get('question', 'N/A')}")
            print(f"  Depends on fetch step: {fetch_step_id}")
            print("⏳ Preparing analysis... (processing data)")
            
            # Get the corresponding fetched data
            if fetch_step_id not in fetched_data:
                print(f"❌ No data found for fetch step {fetch_step_id}")
                analysis_results[step_id] = {
                    'error': f'No data found for fetch step {fetch_step_id}',
                    'stepId': step_id,
                    'title': analysis_step.get('title', ''),
                    'question': analysis_step.get('question', ''),
                    'fetchStepId': fetch_step_id
                }
                continue
            
            fetch_data = fetched_data[fetch_step_id]
            if 'error' in fetch_data:
                print(f"❌ Fetch step {fetch_step_id} had an error: {fetch_data['error']}")
                analysis_results[step_id] = {
                    'error': f'Fetch step error: {fetch_data["error"]}',
                    'stepId': step_id,
                    'title': analysis_step.get('title', ''),
                    'question': analysis_step.get('question', ''),
                    'fetchStepId': fetch_step_id
                }
                continue
            
            # Prepare data for analysis
            csv_data = fetch_data.get('raw_csv', '')
            headers = fetch_data.get('headers', [])
            parsed_data = fetch_data.get('data', [])
            
            if not csv_data and not parsed_data:
                print(f"❌ No data available for analysis step {step_id}")
                analysis_results[step_id] = {
                    'error': 'No data available for analysis',
                    'stepId': step_id,
                    'title': analysis_step.get('title', ''),
                    'question': analysis_step.get('question', ''),
                    'fetchStepId': fetch_step_id
                }
                continue
            
            # Create analysis prompt with data context
            analysis_prompt = f"""
Data Context:
- Fetch Step: {fetch_step_id} - {fetch_step.get('title', '')}
- Data Rows: {len(parsed_data)}
- Headers: {', '.join(headers)}

Analysis Requirements:
- Group By: {analysis_step.get('groupBy', '')}
- Aggregation: {analysis_step.get('aggregation', '')}
- Question: {analysis_step.get('question', '')}

Analysis Prompt: {analysis_step.get('analysisPrompt', '')}

CSV Data:
{csv_data}
"""
            
            try:
                # Call LLM for analysis (you'll need to implement this)
                # For now, we'll store the prepared data
                analysis_results[step_id] = {
                    'stepId': step_id,
                    'title': analysis_step.get('title', ''),
                    'question': analysis_step.get('question', ''),
                    'fetchStepId': fetch_step_id,
                    'groupBy': analysis_step.get('groupBy', ''),
                    'aggregation': analysis_step.get('aggregation', ''),
                    'analysisPrompt': analysis_step.get('analysisPrompt', ''),  # Original analysis prompt without CSV data
                    'csvData': csv_data,  # Separate CSV data for the LLM call
                    'dataRows': len(parsed_data),
                    'headers': headers,
                    'status': 'ready_for_analysis'
                }
                
                print(f"✅ Step {step_id}: Prepared for analysis with {len(parsed_data)} rows")
                
            except Exception as e:
                print(f"❌ Error preparing analysis step {step_id}: {e}")
                analysis_results[step_id] = {
                    'error': str(e),
                    'stepId': step_id,
                    'title': analysis_step.get('title', ''),
                    'question': analysis_step.get('question', ''),
                    'fetchStepId': fetch_step_id
                }
        
        return {
            'execution_plan': execution_plan,
            'fetched_data': fetched_data,
            'analysis_results': analysis_results,
            'summary': {
                'total_fetch_steps': len(fetch_steps),
                'successful_fetch_steps': len([f for f in fetched_data.values() if 'error' not in f]),
                'total_analysis_steps': len(analysis_steps),
                'ready_analysis_steps': len([a for a in analysis_results.values() if 'error' not in a])
            }
        }
        
    except Exception as e:
        print(f"❌ Error executing final analysis plan: {e}")
        return {}


def main():
    """Example usage of the ThoughtSpot API client."""
    try:
        # Initialize API client
        api = ThoughtSpotAPI()
        
        # Example data fetch plan
        sample_data_fetch_plan = [
            {
                "answer_id": "1.1",
                "original_phase_number": 1,
                "original_step_title": "Sample Data Fetch",
                "prompt": "Show me all opportunities created in the last 7 days",
                "data_requirements": {
                    "columns_to_fetch": ["Opportunity Name", "Created Date", "ACV"],
                    "filters": [
                        {
                            "column": "Created Date",
                            "condition": "greater_than",
                            "value": "7 days ago"
                        }
                    ]
                }
            }
        ]
        
        # Execute data fetch
        print("🚀 Executing sample data fetch plan...")
        fetched_data = api.execute_data_fetch_plan(sample_data_fetch_plan, 'support')
        
        print(f"\n📊 Fetched data summary:")
        for answer_id, result in fetched_data.items():
            if 'error' not in result:
                print(f"  {answer_id}: {len(result.get('data', []))} rows")
            else:
                print(f"  {answer_id}: Error - {result['error']}")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")


if __name__ == "__main__":
    main()
