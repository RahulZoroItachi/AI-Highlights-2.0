#!/usr/bin/env python3
"""
Input configuration for different business scenarios.
Reads scenario-specific parameters from inputs.json file.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def _read_tml_file(filename: str) -> str:
    """Read TML file content from the backend directory."""
    backend_dir = Path(__file__).parent
    tml_path = backend_dir / filename
    
    if not tml_path.exists():
        return f"TML file not found: {filename}"
    
    try:
        with open(tml_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading TML file {filename}: {str(e)}"


def _load_inputs_json() -> Dict[str, Any]:
    """Load inputs from inputs.json file."""
    try:
        json_path = Path(__file__).parent / 'inputs.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("inputs.json file not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in inputs.json: {e}")
    except Exception as e:
        raise Exception(f"Error reading inputs.json: {e}")


def _save_inputs_json(data: Dict[str, Any]) -> None:
    """Save updated inputs to inputs.json file."""
    json_path = Path(__file__).parent / 'inputs.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _extract_kpi_from_tml(tml_content: str, scenario: str) -> str:
    """
    Extract KPI information from TML content using a focused LLM call.
    
    Args:
        tml_content: The TML file content
        scenario: The scenario name for context
        
    Returns:
        Extracted KPI string
    """
    try:
        # Import here to avoid circular imports
        from analysis import call_llm_for_analysis
        
        # Create a focused prompt to extract KPIs only
        kpi_prompt = f"""
        

        ROLE:You are an expert TML (ThoughtSpot Modeling Language) analyst. Your primary purpose is to parse and interpret TML files to identify the most important business metrics and provide a comprehensive, consolidated view of all filters applied to them across the entire Liveboard.
OBJECTIVE:Analyze the provided TML file to score every base measure based on its usage. You will then rank these measures. For each of the top-ranked measures, you will detail the complete, consolidated set of all non-date filters that are ever applied to it, paying special attention to how different values for the same filter field are grouped together in different contexts.
Core Concepts & Definitions
Base Measure: The fundamental, reusable calculation defined in the TML (e.g., f_opportunity_m1_created_count). This is the entity you will be scoring.
Business Metric: A high-level business concept that directly corresponds to a Base Measure (e.g., the Business Metric "M1 Count" is represented by the Base Measure f_opportunity_m1_created_count). Your goal is to understand the full context of this metric.
Filter Value Grouping: A specific set of values used to filter a field in one or more visualizations. For example, [Opportunity Stage] IN ('s2 pot', 's3 go/no-go') represents one grouping, while [Opportunity Stage] = 's1 discovery' represents a different, distinct grouping for the same field.
Methodology & Step-by-Step Instructions
Part 1: Identify and Score the Top Base Measures (No Change)
Initialize a Scoreboard: Create a list or dictionary to track the total score for every unique base measure found in the TML.
Scan All Visualizations: Iterate through every visualization block. For each measure used:
Identify the base measure name (e.g., f_opportunity_m1_created_count).
Add points to that base measure's total score according to the following rules:
+10 points: Conditional Formatting Applied
+8 points: KPI Headliner
+5 points: Primary Chart Axis (y or y2)
+3 points: Featured in a Table
Rank the Measures: After scanning all visualizations, sort your scoreboard in descending order.
Part 2: Consolidate All Applied Filters for Each Top Metric (Heavily Refined)
Iterate Through Top Measures: For each of the high-scoring base measures from Part 1, you will now create its comprehensive filter profile.
Initialize a Filter Profile: For each top measure, create a data structure (e.g., a dictionary where keys are field names) to store the distinct filter value groupings.
Comprehensive Scan for Filters: Perform a scan of all visualizations in the TML.
Aggregate Filter Groupings: In each visualization where a top measure is present:
Parse its search_query and extract every non-date filter condition.
For each filtered field (e.g., [Opportunity Stage]), identify the complete set of values used in that single filter instance. For example, [Opportunity Stage].'s2 pot' [Opportunity Stage].'s3 go/no-go' corresponds to the value set {'s2 pot', 's3 go/no-go'}. [Opportunity Stage] = 's1 discovery' corresponds to the value set {'s1 discovery'}.
Add this complete set of values to a list associated with that field name in the measure's filter profile.
Present Consolidated View: After scanning all visualizations, de-duplicate the lists of value sets for each field. The result is a master list of all the unique ways a field is filtered for that metric. Present this master list hierarchically.
Required Output Format (Refined for Clarity)Present your final analysis in a clear, hierarchical report, ordered by the measure's total score.
codeMarkdown

## Top Metrics & Comprehensive Filter Report

This report identifies the most important business metrics, ranked by an importance score. For each metric, it lists the complete, consolidated set of all non-date filters applied to it anywhere on the Liveboard, showing the distinct groupings of values used.

---

        Required Output Format
        Your response must be a single, valid JSON object and nothing else. Do not add any explanatory text, markdown formatting, or code block syntax around the JSON.

        JSON

        {{
          "KPI 1": [
            "aggregation:[base_measure_name] ",
            "[filter_field_1] IN ('value_A', 'value_B', ...) ",
            "[filter_field_1] = 'value_C' ",
            "[filter_field_2] IN ('value_X', 'value_Y') "
          ],
          "KPI 2": [
            "aggregation:[base_measure_name] ",
            "[filter_field_1] IN ('value_A', 'value_B', ...) ",
            "[filter_field_1] = 'value_C' ",
            "[filter_field_2] IN ('value_X', 'value_Y') "
          ]
        }}

        TML Content:
        {tml_content}
        """
        
        system_prompt = """
        You are an expert TML (ThoughtSpot Modeling Language) analyst specializing in business intelligence and KPI identification.
        Analyze the TML content to identify the most critical business metrics and KPIs that would be valuable for analysis and reporting.
        Focus on metrics that directly impact business performance and decision-making.
        """
        
        # Call LLM to extract KPIs
        response = call_llm_for_analysis(system_prompt, kpi_prompt, "claude")
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                extracted_data = json.loads(json_match.group())
                
                # Extract all KPI names and combine them
                kpi_list = []
                for kpi_name, kpi_details in extracted_data.items():
                    if isinstance(kpi_details, list) and len(kpi_details) > 0:
                        # Extract the base measure name from the first item (aggregation:base_measure_name)
                        first_item = kpi_details[0] if kpi_details else ""
                        if "aggregation:" in first_item:
                            base_measure = first_item.split("aggregation:")[1].strip()
                            kpi_list.append(base_measure)
                        else:
                            kpi_list.append(kpi_name)
                    else:
                        kpi_list.append(kpi_name)
                
                # Join all KPIs with commas
                if kpi_list:
                    kpi = ", ".join(kpi_list)
                else:
                    kpi = "Key performance indicators from the data"
                    
            except json.JSONDecodeError:
                kpi = "Key performance indicators from the data"
        else:
            # Fallback if JSON parsing fails
            kpi = response.strip()
            if not kpi or len(kpi) < 10:
                kpi = "Key performance indicators from the data"
        print(f"Extracted KPIs: {kpi}")    
        return kpi
            
    except Exception as e:
        print(f"Warning: Failed to extract KPIs from TML: {e}")
        return "Key performance indicators from the data"




def _extract_attributes_and_date_from_tml(tml_content: str, scenario: str) -> tuple[str, str]:
    """
    Extract attributes and date column information from TML content using a combined LLM call.
    
    Args:
        tml_content: The TML file content
        scenario: The scenario name for context
        
    Returns:
        Tuple of (attributes, date_column)
    """
    try:
        # Import here to avoid circular imports
        from analysis import call_llm_for_analysis
        
        # Use the existing attributes prompt that returns combined JSON
        attributes_prompt = f"""
        Your task is to act as an expert data analyst specializing in BI dashboard metadata. I will provide you with a TML file (a YAML-based format) that contains the metadata for a business intelligence dashboard.

        Your goal is to analyze this TML file and identify the most important attributes for analysis. You must rank these attributes based on how they are used throughout the dashboard according to a specific scoring system.

        Definition and Scoring of an "Important Attribute"
        Please classify and score attributes based on the following hierarchy of importance. For each visualization an attribute appears in, award it points as follows:

        Color Slicing (10 points): The attribute is used in the color field within axis_configs. This is the most important usage as it directly slices a metric within a chart.

        X-Axis (7 points): The attribute is used in the x field within axis_configs. This is the primary dimension used for grouping and slicing data.

        Liveboard Filter (5 points): The attribute is listed in the top-level liveboard.filters section. This indicates it's used to filter the entire dashboard.

        Table/Chart Column (1 point): The attribute is present as a column in a table or chart (found in answer_columns, table_columns, or chart_columns). This is the least weighted, as it often provides contextual detail rather than being a primary analytical driver.

        Instructions
        Parse the entire TML file and iterate through each visualization.

        For every attribute, calculate its total score by summing the points from all its occurrences across the dashboard based on the scoring system above.

        Crucially, you must ignore measures/metrics. Focus only on the dimensional attributes used for slicing and dicing. Common measures to exclude are fields containing names like 'ACV', 'Count', 'Total', 'Sum', 'Average', etc.

        If you encounter date attributes with functions (e.g., Week(Opportunity M1 Date) or Month(Opportunity S1 Date)), consolidate the points under the base attribute (e.g., Opportunity M1 Date, Opportunity S1 Date).

        Required Output Format
        Your response must be a single, valid JSON object and nothing else. Do not add any explanatory text, markdown formatting, or code block syntax around the JSON.

        JSON

        {{
          "Attribute": [
            "Top Attribute 1",
            "Top Attribute 2",
            "Top Attribute 3",
            "Top Attribute 4",
            "Top Attribute 5"
          ],
          "Date": "Top Date Attribute"
        }}

        TML Content:
        {tml_content}
        """
        
        system_prompt = """
        You are a data modeling expert specializing in dimensional analysis. 
        Analyze the TML content and identify the most important dimensions and attributes that would be useful for data slicing, filtering, and grouping in business analysis.
        Focus on attributes that provide meaningful business insights when used for analysis.
        """
        
        # Call LLM to extract attributes and date
        response = call_llm_for_analysis(system_prompt, attributes_prompt, "claude")
        
        # Parse JSON response
        import re
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
                attributes = "Key dimensions for analysis"
                date_column = "Date column for temporal analysis"
        else:
            # Fallback if JSON parsing fails
            attributes = "Key dimensions for analysis"
            date_column = "Date column for temporal analysis"
            
        return attributes, date_column
            
    except Exception as e:
        print(f"Warning: Failed to extract attributes and date from TML: {e}")
        return "Key dimensions for analysis", "Date column for temporal analysis"




def _extract_metadata_from_tml(tml_content: str, scenario: str) -> Dict[str, str]:
    """
    Extract KPI, attributes, and date column information from TML content using separate LLM calls.
    
    Args:
        tml_content: The TML file content
        scenario: The scenario name for context
        
    Returns:
        Dictionary with extracted kpi, attributes, and date_column
    """
    print(f"🔍 Extracting metadata for {scenario} scenario using separate LLM calls...")
    
    # Extract KPI with separate call
    kpi = _extract_kpi_from_tml(tml_content, scenario)
    
    # Extract attributes and date column from combined JSON response
    attributes, date_column = _extract_attributes_and_date_from_tml(tml_content, scenario)
    
    return {
        'kpi': kpi,
        'attributes': attributes,
        'date_column': date_column
    }


def _ensure_metadata_complete(scenario: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure that KPI, attributes, and date_column are present in the config.
    If missing, extract them from TML and update the JSON file.
    
    Args:
        scenario: The scenario name
        config: The scenario configuration
        
    Returns:
        Updated configuration with complete metadata
    """
    # Check if any of the required fields are missing or empty
    missing_fields = []
    if not config.get('kpi') or config.get('kpi').strip() == '':
        missing_fields.append('kpi')
    if not config.get('attributes') or config.get('attributes').strip() == '':
        missing_fields.append('attributes')
    if not config.get('date_column') or config.get('date_column').strip() == '':
        missing_fields.append('date_column')
    
    if missing_fields:
        print(f"📊 Extracting missing metadata for {scenario} scenario: {', '.join(missing_fields)}")
        
        # Read TML file
        tml_content = _read_tml_file(config['tml_filename'])
        
        # Extract metadata from TML using separate focused calls
        extracted_metadata = _extract_metadata_from_tml(tml_content, scenario)
        
        # Update the config with extracted metadata
        for field in missing_fields:
            if field in extracted_metadata:
                config[field] = extracted_metadata[field]
                print(f"✅ Extracted {field}: {extracted_metadata[field][:100]}{'...' if len(extracted_metadata[field]) > 100 else ''}")
        
        # Update the JSON file with the new metadata
        try:
            inputs_data = _load_inputs_json()
            inputs_data[scenario].update(config)
            _save_inputs_json(inputs_data)
            print(f"💾 Updated inputs.json with extracted metadata for {scenario}")
        except Exception as e:
            print(f"⚠️ Warning: Could not update inputs.json: {e}")
    
    return config


def scenario_pg() -> Dict[str, Any]:
    """Product Growth scenario inputs."""
    inputs_data = _load_inputs_json()
    pg_config = inputs_data['pg'].copy()  # Make a copy to avoid modifying original
    
    # Ensure metadata is complete
    pg_config = _ensure_metadata_complete('pg', pg_config)
    
    Liveboard_TML = _read_tml_file(pg_config['tml_filename'])
    
    return {
        "Liveboard_TML": Liveboard_TML,
        "Worksheet_ID": pg_config['worksheet_id'],
        "KPI": pg_config['kpi'],
        "Attributes": pg_config['attributes'],
        "Aggregations": pg_config['aggregations'],
        "Date_Column": pg_config['date_column'],
        "Goal": pg_config['goal'],
        "User_Context": pg_config['user_context'],
        "Report_Format": pg_config['report_format'],
    }


def scenario_support() -> Dict[str, Any]:
    """Customer Support scenario inputs."""
    inputs_data = _load_inputs_json()
    support_config = inputs_data['support'].copy()  # Make a copy to avoid modifying original
    
    # Ensure metadata is complete
    support_config = _ensure_metadata_complete('support', support_config)
    
    Liveboard_TML = _read_tml_file(support_config['tml_filename'])
    
    return {
        "Liveboard_TML": Liveboard_TML,
        "Worksheet_ID": support_config['worksheet_id'],
        "KPI": support_config['kpi'],
        "Attributes": support_config['attributes'],
        "Aggregations": support_config['aggregations'],
        "Date_Column": support_config['date_column'],
        "Goal": support_config['goal'],
        "User_Context": support_config['user_context'],
        "Report_Format": support_config['report_format'],
    }


def scenario_ta() -> Dict[str, Any]:
    """Talent Acquisition scenario inputs."""
    inputs_data = _load_inputs_json()
    ta_config = inputs_data['ta'].copy()  # Make a copy to avoid modifying original
    
    # Ensure metadata is complete
    ta_config = _ensure_metadata_complete('ta', ta_config)
    
    Liveboard_TML = _read_tml_file(ta_config['tml_filename'])
    
    return {
        "Liveboard_TML": Liveboard_TML,
        "Worksheet_ID": ta_config['worksheet_id'],
        "KPI": ta_config['kpi'],
        "Attributes": ta_config['attributes'],
        "Aggregations": ta_config['aggregations'],
        "Date_Column": ta_config['date_column'],
        "Goal": ta_config['goal'],
        "User_Context": ta_config['user_context'],
        "Report_Format": ta_config['report_format'],
    }


def scenario_cmo() -> Dict[str, Any]:
    """Chief Marketing Officer scenario inputs."""
    inputs_data = _load_inputs_json()
    cmo_config = inputs_data['cmo'].copy()  # Make a copy to avoid modifying original
    
    # Ensure metadata is complete
    cmo_config = _ensure_metadata_complete('cmo', cmo_config)
    
    Liveboard_TML = _read_tml_file(cmo_config['tml_filename'])
    
    return {
        "Liveboard_TML": Liveboard_TML,
        "Worksheet_ID": cmo_config['worksheet_id'],
        "KPI": cmo_config['kpi'],
        "Attributes": cmo_config['attributes'],
        "Aggregations": cmo_config['aggregations'],
        "Date_Column": cmo_config['date_column'],
        "Goal": cmo_config['goal'],
        "User_Context": cmo_config['user_context'],
        "Report_Format": cmo_config['report_format'],
    }


def scenario_test() -> Dict[str, Any]:
    """Test scenario inputs with missing metadata for extraction testing."""
    inputs_data = _load_inputs_json()
    test_config = inputs_data['test'].copy()  # Make a copy to avoid modifying original
    
    # Ensure metadata is complete
    test_config = _ensure_metadata_complete('test', test_config)
    
    Liveboard_TML = _read_tml_file(test_config['tml_filename'])
    
    return {
        "Liveboard_TML": Liveboard_TML,
        "Worksheet_ID": test_config['worksheet_id'],
        "KPI": test_config['kpi'],
        "Attributes": test_config['attributes'],
        "Aggregations": test_config['aggregations'],
        "Date_Column": test_config['date_column'],
        "Goal": test_config['goal'],
        "User_Context": test_config['user_context'],
        "Report_Format": test_config['report_format'],
    }


def get_scenario_inputs(scenario: str) -> Dict[str, Any]:
    """
    Get scenario-specific inputs based on the scenario name.
    
    Args:
        scenario: One of 'pg', 'support', 'ta', 'cmo', 'test'
        
    Returns:
        Dictionary containing scenario-specific inputs
    """
    scenario_functions = {
        'pg': scenario_pg,
        'support': scenario_support,
        'ta': scenario_ta,
        'cmo': scenario_cmo,
        'test': scenario_test,
    }
    
    if scenario not in scenario_functions:
        raise ValueError(f"Unknown scenario: {scenario}. Must be one of: {list(scenario_functions.keys())}")
    
    return scenario_functions[scenario]()