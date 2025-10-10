"""
LLM input handling and output parsing for TML analysis.
"""

import json
import re
from typing import Tuple, Dict, Any
from input_prompts import get_kpi_extraction_prompt, get_attributes_extraction_prompt, call_llm_for_analysis, kpi_refinement_prompt, get_goal_extraction_prompt, get_user_context_extraction_prompt


def refine_kpis(kpis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refine KPIs by scoring them and removing duplicates.
    
    Args:
        kpis_data: The raw KPIs data to refine
        
    Returns:
        Refined KPIs dictionary with scores and duplicates removed
    """
    try:
        print("🔍 Refining KPIs - scoring and removing duplicates...")
        
        # Get prompts from the prompts module
        system_prompt, user_prompt = kpi_refinement_prompt(kpis_data)
        
        # Call LLM to refine KPIs
        response = call_llm_for_analysis(system_prompt, user_prompt, "claude")
        
        # Parse the LLM response
        refined_kpis = _parse_kpi_response(response)
        
        print(f"📊 KPI refinement completed: {len(kpis_data)} → {len(refined_kpis)} KPIs after deduplication")
        
        # Log the refinement results
        for kpi_id, kpi_data in refined_kpis.items():
            score = kpi_data.get('score', 0)
            chart_type = kpi_data.get('chart_type', 'Unknown')
            print(f"  ✅ {kpi_data.get('name', kpi_id)} (Score: {score}, Type: {chart_type})")
        
        return refined_kpis
            
    except Exception as e:
        print(f"Warning: Failed to refine KPIs: {e}")
        print("Returning original KPIs without refinement")
        return kpis_data


def extract_kpi_from_json(extracted_json: dict, scenario: str) -> Dict[str, Any]:
    """
    Extract KPI information from extracted visualization JSON using a focused LLM call.
    
    Args:
        extracted_json: The extracted visualization JSON data
        scenario: The scenario name for context
        
    Returns:
        Extracted KPI dictionary with detailed information
    """
    try:
        # Get prompts from the prompts module
        system_prompt, user_prompt = get_kpi_extraction_prompt(extracted_json)
        
        # Call LLM to extract KPIs
        response = call_llm_for_analysis(system_prompt, user_prompt, "claude")
        
        # Parse the LLM response
        kpi = _parse_kpi_response(response)
        
        print(f"Extracted KPIs: {list(kpi.keys())}")    
        return kpi
            
    except Exception as e:
        print(f"Warning: Failed to extract KPIs from JSON: {e}")
        return {"KPI_1": {
            "name": "Key Performance Indicator",
            "measure": "primary_measure",
            "formula": "aggregation_function",
            "filters": [],
            "description": "Key performance indicators from the data"
        }}


def extract_attributes_and_date_from_json(extracted_json: dict, scenario: str) -> Tuple[str, str]:
    """
    Extract attributes and date column information from extracted visualization JSON using a combined LLM call.
    
    Args:
        extracted_json: The extracted visualization JSON data
        scenario: The scenario name for context
        
    Returns:
        Tuple of (attributes, date_column)
    """
    try:
        # Get prompts from the prompts module
        system_prompt, user_prompt = get_attributes_extraction_prompt(extracted_json)
        
        # Call LLM to extract attributes and date
        response = call_llm_for_analysis(system_prompt, user_prompt, "claude")
        
        # Parse the LLM response
        attributes, date_column = _parse_attributes_response(response)
        
        return attributes, date_column
            
    except Exception as e:
        print(f"Warning: Failed to extract attributes and date from JSON: {e}")
        return "Key dimensions for analysis", "Date column for temporal analysis"


# Legacy functions for backward compatibility - now work with TML content
def extract_kpi_from_tml(tml_content: str, scenario: str) -> str:
    """
    Extract KPI information from TML content using a focused LLM call.
    DEPRECATED: Use extract_kpi_from_json with extracted visualization data instead.
    
    Args:
        tml_content: The TML file content
        scenario: The scenario name for context
        
    Returns:
        Extracted KPI string
    """
    try:
        # Get prompts from the prompts module - need to create legacy TML prompts
        # For now, return a default message
        print("Warning: extract_kpi_from_tml is deprecated. Use extract_kpi_from_json instead.")
        return "Key performance indicators from the data"
            
    except Exception as e:
        print(f"Warning: Failed to extract KPIs from TML: {e}")
        return "Key performance indicators from the data"


def extract_attributes_and_date_from_tml(tml_content: str, scenario: str) -> Tuple[str, str]:
    """
    Extract attributes and date column information from TML content using a combined LLM call.
    DEPRECATED: Use extract_attributes_and_date_from_json with extracted visualization data instead.
    
    Args:
        tml_content: The TML file content
        scenario: The scenario name for context
        
    Returns:
        Tuple of (attributes, date_column)
    """
    try:
        # For now, return default values
        print("Warning: extract_attributes_and_date_from_tml is deprecated. Use extract_attributes_and_date_from_json instead.")
        return "Key dimensions for analysis", "Date column for temporal analysis"
            
    except Exception as e:
        print(f"Warning: Failed to extract attributes and date from TML: {e}")
        return "Key dimensions for analysis", "Date column for temporal analysis"


def _parse_kpi_response(response: str) -> Dict[str, Any]:
    """
    Parse the KPI extraction response from the LLM.
    
    Args:
        response: Raw LLM response
        
    Returns:
        Parsed KPI dictionary with detailed information
    """
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                extracted_data = json.loads(json_match.group())
                
                # Check if this is a refined KPIs response with 'top_10_kpis' array
                if 'top_10_kpis' in extracted_data and isinstance(extracted_data['top_10_kpis'], list):
                    print(f"🔄 Converting refined KPIs array format to dictionary format...")
                    
                    # Convert array format to dictionary format
                    converted_kpis = {}
                    for i, kpi in enumerate(extracted_data['top_10_kpis'], 1):
                        # Ensure kpi is a dictionary
                        if not isinstance(kpi, dict):
                            print(f"⚠️ Skipping non-dictionary KPI at index {i}: {type(kpi)}")
                            continue
                            
                        kpi_key = f"KPI_{i}"
                        converted_kpis[kpi_key] = {
                            "name": kpi.get('kpi_name', f'KPI {i}'),
                            "measure": kpi.get('measure', ''),
                            "formula": kpi.get('formula', ''),
                            "filters": kpi.get('filters', []),
                            "description": kpi.get('description', ''),
                            "chart_type": kpi.get('chart_type_source', ''),
                            "table_name": kpi.get('table_name', ''),
                            "table_id": kpi.get('table_id', ''),
                            "score": kpi.get('score', 0)  # Include score if available
                        }
                    
                    print(f"✅ Converted {len(converted_kpis)} KPIs from array to dictionary format")
                    return converted_kpis
                
                # Check if the extracted_data itself is a list (unexpected format)
                elif isinstance(extracted_data, list):
                    print(f"⚠️ Unexpected list format in LLM response, attempting to convert...")
                    converted_kpis = {}
                    for i, item in enumerate(extracted_data, 1):
                        if isinstance(item, dict):
                            kpi_key = f"KPI_{i}"
                            converted_kpis[kpi_key] = {
                                "name": item.get('kpi_name', item.get('name', f'KPI {i}')),
                                "measure": item.get('measure', ''),
                                "formula": item.get('formula', ''),
                                "filters": item.get('filters', []),
                                "description": item.get('description', ''),
                                "chart_type": item.get('chart_type_source', item.get('chart_type', '')),
                                "table_name": item.get('table_name', ''),
                                "table_id": item.get('table_id', ''),
                                "score": item.get('score', 0)
                            }
                    
                    if converted_kpis:
                        print(f"✅ Converted {len(converted_kpis)} KPIs from unexpected list format")
                        return converted_kpis
                    else:
                        print("❌ Could not convert list format - no valid KPI dictionaries found")
                
                # Standard dictionary format:
                # {
                #   "KPI 1": {
                #     "name": "...",
                #     "measure": "...",
                #     "formula": "...",
                #     "filters": [...],
                #     "description": "..."
                #   },
                #   ...
                # }
                elif extracted_data:
                    return extracted_data
                else:
                    return {"KPI_1": {
                        "name": "Key Performance Indicator",
                        "measure": "primary_measure",
                        "formula": "aggregation_function",
                        "filters": [],
                        "description": "Key performance indicators from the data",
                        "chart_type": "",
                        "table_name": "",
                        "table_id": "",
                        "score": 0
                    }}
                    
            except json.JSONDecodeError:
                return {"KPI_1": {
                    "name": "Key Performance Indicator",
                    "measure": "primary_measure",
                    "formula": "aggregation_function",
                    "filters": [],
                    "description": "Key performance indicators from the data",
                    "chart_type": "",
                    "table_name": "",
                    "table_id": "",
                    "score": 0
                }}
        else:
            # Fallback if JSON parsing fails
            return {"KPI_1": {
                "name": "Key Performance Indicator",
                "measure": "primary_measure",
                "formula": "aggregation_function",
                "filters": [],
                "description": "Key performance indicators from the data"
            }}
            
    except Exception as e:
        print(f"Error parsing KPI response: {e}")
        return {"KPI_1": {
            "name": "Key Performance Indicator",
            "measure": "primary_measure",
            "formula": "aggregation_function",
            "filters": [],
            "description": "Key performance indicators from the data"
        }}


def _parse_attributes_response(response: str) -> Tuple[str, str]:
    """
    Parse the attributes extraction response from the LLM.
    
    Args:
        response: Raw LLM response
        
    Returns:
        Tuple of (attributes, date_column)
    """
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                extracted_data = json.loads(json_match.group())
                
                # Extract attributes list and join them
                attributes_list = extracted_data.get('Attribute', [])
                if isinstance(attributes_list, list) and len(attributes_list) > 0:
                    attributes = ", ".join(attributes_list)
                else:
                    attributes = "Key dimensions for analysis"
                
                # Extract date column
                date_column = extracted_data.get('Date', '')
                if not date_column or len(date_column) < 5:
                    date_column = "Date column for temporal analysis"
                    
                return attributes, date_column
                
            except json.JSONDecodeError:
                return "Key dimensions for analysis", "Date column for temporal analysis"
        else:
            # Fallback if JSON parsing fails
            return "Key dimensions for analysis", "Date column for temporal analysis"
            
    except Exception as e:
        print(f"Error parsing attributes response: {e}")
        return "Key dimensions for analysis", "Date column for temporal analysis"


def validate_json_response(response: str) -> bool:
    """
    Validate if the response contains valid JSON.
    
    Args:
        response: Raw LLM response
        
    Returns:
        True if response contains valid JSON, False otherwise
    """
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json.loads(json_match.group())
            return True
        return False
    except (json.JSONDecodeError, AttributeError):
        return False


def extract_json_from_response(response: str) -> dict:
    """
    Extract and parse JSON from LLM response.
    
    Args:
        response: Raw LLM response
        
    Returns:
        Parsed JSON dict or empty dict if parsing fails
    """
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except (json.JSONDecodeError, AttributeError):
        return {}


# Legacy function names for backward compatibility
def _extract_kpi_from_tml(tml_content: str, scenario: str) -> str:
    """Legacy function name - use extract_kpi_from_tml instead."""
    return extract_kpi_from_tml(tml_content, scenario)


def _extract_attributes_and_date_from_tml(tml_content: str, scenario: str) -> Tuple[str, str]:
    """Legacy function name - use extract_attributes_and_date_from_tml instead."""
    return extract_attributes_and_date_from_tml(tml_content, scenario)


def extract_goal(analysis_result: Dict[str, Any], scenario: str = "analysis") -> str:
    """
    Extract the primary business goal from the complete analysis result.
    
    Args:
        analysis_result: Complete analysis result containing KPIs, attributes, liveboard name, etc.
        scenario: Scenario identifier for logging purposes
        
    Returns:
        String containing the primary business goal sentence
    """
    try:
        print("🎯 Analyzing dashboard for primary business goal...")
        
        # Get prompts from the prompts module
        system_prompt, user_prompt = get_goal_extraction_prompt(analysis_result)
        
        # Call LLM to analyze goals
        response = call_llm_for_analysis(system_prompt, user_prompt, "claude")
        
        # Parse the LLM response (expect a simple sentence)
        goal_sentence = _parse_goal_response(response)
        
        print(f"📊 Goal extraction completed for scenario: {scenario}")
        print(f"  🎯 Primary Goal: {goal_sentence}")
        
        return goal_sentence
            
    except Exception as e:
        print(f"Warning: Failed to extract goal from analysis result: {e}")
        print("Returning default goal")
        return "Monitor key business performance metrics and KPIs to support data-driven decision making."


def _parse_goal_response(response: str) -> str:
    """
    Parse the goal extraction response from the LLM.
    
    Args:
        response: Raw LLM response containing the goal sentence
        
    Returns:
        Cleaned goal sentence string
    """
    try:
        # Clean up the response by removing extra whitespace and common formatting
        cleaned_response = response.strip()
        
        # Remove common prefixes that might be added by the LLM
        prefixes_to_remove = [
            "The primary business goal is:",
            "Primary goal:",
            "Goal:",
            "The goal is:",
            "Business goal:",
            "Main objective:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned_response.lower().startswith(prefix.lower()):
                cleaned_response = cleaned_response[len(prefix):].strip()
                break
        
        # Remove quotes if the sentence is wrapped in them
        if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
            cleaned_response = cleaned_response[1:-1].strip()
        elif cleaned_response.startswith("'") and cleaned_response.endswith("'"):
            cleaned_response = cleaned_response[1:-1].strip()
        
        # Ensure it ends with a period if it doesn't already
        if cleaned_response and not cleaned_response.endswith('.'):
            cleaned_response += '.'
        
        # Return the cleaned sentence or default if empty
        return cleaned_response if cleaned_response else "Monitor key business performance metrics and support data-driven decision making."
            
    except Exception as e:
        print(f"Error parsing goal response: {e}")
        return "Monitor key business performance metrics and support data-driven decision making."


def extract_user_context(analysis_result: Dict[str, Any], scenario: str = "analysis") -> str:
    """
    Extract the primary user context from the complete analysis result.
    
    Args:
        analysis_result: Complete analysis result containing KPIs, attributes, liveboard name, etc.
        scenario: Scenario identifier for logging purposes
        
    Returns:
        String containing the primary user context sentence
    """
    try:
        print("👥 Analyzing dashboard for primary user context...")
        
        # Get prompts from the prompts module
        system_prompt, user_prompt = get_user_context_extraction_prompt(analysis_result)
        
        # Call LLM to analyze user context
        response = call_llm_for_analysis(system_prompt, user_prompt, "claude")
        
        # Parse the LLM response (expect a simple sentence)
        user_context_sentence = _parse_user_context_response(response)
        
        print(f"📊 User context extraction completed for scenario: {scenario}")
        print(f"  👥 Primary User Context: {user_context_sentence}")
        
        return user_context_sentence
            
    except Exception as e:
        print(f"Warning: Failed to extract user context from analysis result: {e}")
        print("Returning default user context")
        return "Business stakeholders and analysts use this dashboard to monitor performance metrics and make data-driven decisions."


def _parse_user_context_response(response: str) -> str:
    """
    Parse the user context extraction response from the LLM.
    
    Args:
        response: Raw LLM response containing the user context sentence
        
    Returns:
        Cleaned user context sentence string
    """
    try:
        # Clean up the response by removing extra whitespace and common formatting
        cleaned_response = response.strip()
        
        # Remove common prefixes that might be added by the LLM
        prefixes_to_remove = [
            "The primary user context is:",
            "Primary user context:",
            "User context:",
            "The user context is:",
            "Target audience:",
            "Primary users:",
            "Dashboard users:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned_response.lower().startswith(prefix.lower()):
                cleaned_response = cleaned_response[len(prefix):].strip()
                break
        
        # Remove quotes if the sentence is wrapped in them
        if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
            cleaned_response = cleaned_response[1:-1].strip()
        elif cleaned_response.startswith("'") and cleaned_response.endswith("'"):
            cleaned_response = cleaned_response[1:-1].strip()
        
        # Ensure it ends with a period if it doesn't already
        if cleaned_response and not cleaned_response.endswith('.'):
            cleaned_response += '.'
        
        # Return the cleaned sentence or default if empty
        return cleaned_response if cleaned_response else "Business stakeholders and analysts use this dashboard to monitor performance metrics and make data-driven decisions."
            
    except Exception as e:
        print(f"Error parsing user context response: {e}")
        return "Business stakeholders and analysts use this dashboard to monitor performance metrics and make data-driven decisions."
