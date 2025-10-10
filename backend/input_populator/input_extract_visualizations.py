#!/usr/bin/env python3
"""
Python visualization extractor for TML JSON files.
Extracts visualization data from unformatted TML JSON and outputs to terminal.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional, Union


def parse_nested_json_strings(obj: Any) -> Any:
    """
    Recursively parse JSON strings within an object.
    
    Args:
        obj: The object to parse
        
    Returns:
        Parsed object with JSON strings converted to objects
    """
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except (json.JSONDecodeError, TypeError):
            return obj
    elif isinstance(obj, dict):
        return {key: parse_nested_json_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [parse_nested_json_strings(item) for item in obj]
    else:
        return obj


def extract_visible_columns(answer: Dict[str, Any]) -> List[str]:
    """
    Extract visible columns from table answer data.
    
    Args:
        answer: Answer object containing table and chart data
        
    Returns:
        List of visible column names
    """
    try:
        visible_columns = []
        
        # Get all answer columns first
        answer_columns = answer.get('answer_columns', [])
        all_column_names = [col.get('name') for col in answer_columns if col.get('name')]
        
        # Check if we have column properties in table data
        column_properties = []
        if answer.get('table', {}).get('client_state_v2'):
            try:
                table_config = answer['table']['client_state_v2']
                column_properties = table_config.get('columnProperties', [])
            except Exception as e:
                print(f"Warning: Could not parse table.client_state_v2: {e}")
        
        # Create a map of column properties for quick lookup
        column_props_map = {}
        for prop in column_properties:
            if prop.get('columnId'):
                column_props_map[prop['columnId']] = prop.get('columnProperty', {})
        
        # Determine visible columns
        for column_name in all_column_names:
            column_property = column_props_map.get(column_name, {})
            
            # If column is not in properties or isHidden is not true, include it
            if not column_property or column_property.get('isHidden') is not True:
                visible_columns.append(column_name)
        
        return visible_columns
    except Exception as e:
        print(f"Warning: Could not extract visible columns: {e}")
        return []


def extract_pivot_table_columns(answer: Dict[str, Any]) -> List[str]:
    """
    Extract visible columns from ADVANCED_PIVOT_TABLE chart configuration.
    
    Args:
        answer: Answer object containing chart data
        
    Returns:
        List of visible column names
    """
    try:
        visible_columns = []
        
        # Check if we have custom_chart_config with dimensions
        chart = answer.get('chart', {})
        custom_chart_config = chart.get('custom_chart_config', [])
        
        if isinstance(custom_chart_config, list):
            for config in custom_chart_config:
                dimensions = config.get('dimensions', [])
                if isinstance(dimensions, list):
                    for dimension in dimensions:
                        # Extract from all relevant dimensions: rows, values, columns, split-by-color
                        columns = dimension.get('columns', [])
                        if isinstance(columns, list):
                            for column in columns:
                                # Filter out "Measure names" and "Measure values" from final column names
                                if column not in ['Measure names', 'Measure values']:
                                    visible_columns.append(column)
        
        return visible_columns
    except Exception as e:
        print(f"Warning: Could not extract pivot table columns: {e}")
        return []


def extract_pivot_table_columns_from_axis(answer: Dict[str, Any]) -> List[str]:
    """
    Extract visible columns from PIVOT_TABLE chart configuration using axisProperties.
    
    Args:
        answer: Answer object containing chart data
        
    Returns:
        List of visible column names
    """
    try:
        visible_columns = []
        
        # Check if we have axisProperties with linkedColumns in chart.client_state_v2
        chart = answer.get('chart', {})
        client_state_v2 = chart.get('client_state_v2', {})
        
        # If client_state_v2 is a string, try to parse it as JSON
        if isinstance(client_state_v2, str):
            try:
                client_state_v2 = json.loads(client_state_v2)
            except (json.JSONDecodeError, TypeError):
                print(f"Warning: Could not parse client_state_v2 as JSON: {client_state_v2}")
                return []
        
        axis_properties = client_state_v2.get('axisProperties', [])
        
        if isinstance(axis_properties, list):
            for axis in axis_properties:
                # linkedColumns are nested under properties
                properties = axis.get('properties', {})
                linked_columns = properties.get('linkedColumns', [])
                
                if isinstance(linked_columns, list):
                    for column in linked_columns:
                        # Filter out "Measure names" and "Measure values" from final column names
                        if column not in ['Measure names', 'Measure values']:
                            visible_columns.append(column)
        
        # Remove duplicates while preserving order
        unique_columns = []
        seen = set()
        for column in visible_columns:
            if column not in seen:
                unique_columns.append(column)
                seen.add(column)
        
        return unique_columns
    except Exception as e:
        print(f"Warning: Could not extract pivot table columns from axis: {e}")
        return []


def extract_visualization_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract visualization data from a single JSON object.
    
    Args:
        input_data: The parsed JSON data
        
    Returns:
        Dictionary containing extracted visualization data
    """
    try:
        # Parse nested JSON strings
        formatted_data = parse_nested_json_strings(input_data)
        
        visualizations = []
        
        # Process each liveboard
        if isinstance(formatted_data, list):
            for liveboard_data in formatted_data:
                if isinstance(liveboard_data, dict):
                    liveboard = liveboard_data.get('edoc', {}).get('liveboard', {})
                    
                    if liveboard:
                        # Create tab mapping from layout.tabs
                        tab_map = {}
                        has_tabs = False
                        layout = liveboard.get('layout', {})
                        tabs = layout.get('tabs', [])
                        
                        if tabs:
                            has_tabs = True
                            for tab in tabs:
                                tab_name = tab.get('name', '')
                                
                                # Get visualizations from direct tiles
                                tiles = tab.get('tiles', [])
                                for tile in tiles:
                                    viz_id = tile.get('visualization_id')
                                    if viz_id:
                                        tab_map[viz_id] = tab_name
                                
                                # Get visualizations from group_layouts
                                group_layouts = tab.get('group_layouts', [])
                                for group in group_layouts:
                                    group_tiles = group.get('tiles', [])
                                    for tile in group_tiles:
                                        viz_id = tile.get('visualization_id')
                                        if viz_id:
                                            tab_map[viz_id] = tab_name
                        
                        # Process each visualization
                        liveboard_visualizations = liveboard.get('visualizations', [])
                        for viz in liveboard_visualizations:
                            # Determine chart type based on display mode
                            chart_type = 'Unknown'
                            axis_configs = None
                            visible_columns = None
                            
                            answer = viz.get('answer', {})
                            display_mode = answer.get('display_mode')
                            
                            if display_mode == 'CHART_MODE':
                                chart = answer.get('chart', {})
                                chart_type = chart.get('type', 'Unknown')
                                
                                # Add axis configs for non-pivot chart types
                                if chart_type not in ['ADVANCED_PIVOT_TABLE', 'PIVOT_TABLE']:
                                    axis_configs = chart.get('axis_configs')
                                    
                            elif display_mode == 'TABLE_MODE':
                                chart_type = 'TABLE'
                                
                                # Extract visible columns for table mode
                                try:
                                    visible_columns = extract_visible_columns(answer)
                                except Exception as e:
                                    print(f"Warning: Could not extract visible columns for TABLE visualization {viz.get('id', 'Unknown')}: {e}")
                                    visible_columns = []
                            
                            # Handle ADVANCED_PIVOT_TABLE chart type
                            if chart_type == 'ADVANCED_PIVOT_TABLE':
                                try:
                                    visible_columns = extract_pivot_table_columns(answer)
                                except Exception as e:
                                    print(f"Warning: Could not extract visible columns for ADVANCED_PIVOT_TABLE visualization {viz.get('id', 'Unknown')}: {e}")
                                    visible_columns = []
                            
                            # Handle PIVOT_TABLE chart type
                            if chart_type == 'PIVOT_TABLE':
                                try:
                                    visible_columns = extract_pivot_table_columns_from_axis(answer)
                                except Exception as e:
                                    print(f"Warning: Could not extract visible columns for PIVOT_TABLE visualization {viz.get('id', 'Unknown')}: {e}")
                                    visible_columns = []
                            
                            # Create visualization data
                            viz_data = {
                                'viz_id': viz.get('id', 'Unknown ID'),
                                'answer_name': answer.get('name', 'Unknown Name'),
                                'answer_tables': answer.get('tables', []),
                                'answer_formulas': answer.get('formulas', []),
                                'chart_type': chart_type,
                                'answer_parameters': answer.get('parameters', []),
                                'answer_search_query': answer.get('search_query', 'No Query')
                            }
                            
                            # Add tab_name only if the liveboard has tabs
                            if has_tabs:
                                viz_id = viz.get('id')
                                if viz_id in tab_map:
                                    viz_data['tab_name'] = tab_map[viz_id]
                            
                            # Add axis configs if present
                            if axis_configs:
                                viz_data['axis_configs'] = axis_configs
                            
                            # Add visible columns if present
                            if visible_columns:
                                viz_data['visible_columns'] = visible_columns
                            
                            visualizations.append(viz_data)
        
        return {
            'success': True,
            'liveboard_name': formatted_data[0].get('edoc', {}).get('liveboard', {}).get('name', 'Unknown Liveboard') if formatted_data else 'Unknown Liveboard',
            'visualizations': visualizations,
            'count': len(visualizations)
        }
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return {
            'success': False,
            'error': str(e),
            'visualizations': [],
            'count': 0
        }


def main():
    """
    Main function to process TML JSON input and output results to JSON file.
    """
    if len(sys.argv) != 2:
        print("Usage: python extract_visualizations.py <input_file.json>")
        print("Example: python extract_visualizations.py download.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    try:
        print(f"📁 Processing {input_file}...")
        print("=" * 50)
        
        # Read and parse JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print("Reading JSON file...")
        print("Parsing nested JSON strings...")
        
        # Extract visualization data
        result = extract_visualization_data(raw_data)
        
        if result['success']:
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}-extracted-visualizations.json"
            
            # Write results to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Extracted {result['count']} visualization(s) from {input_file}")
            print(f"📊 Liveboard: {result['liveboard_name']}")
            print(f"📁 Output written to: {output_file}")
            print(f"📊 Output size: {os.path.getsize(output_file)} characters")
            
        else:
            print(f"❌ Error processing {input_file}: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()