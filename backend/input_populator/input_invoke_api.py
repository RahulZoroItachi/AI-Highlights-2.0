#!/usr/bin/env python3
"""
Integrated TML export and visualization extraction for ThoughtSpot.
"""

import json
import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from input_extract_visualizations import extract_visualization_data

# Load environment variables from the correct location
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class ThoughtSpotAPI:
    """ThoughtSpot API client for TML export."""
    
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
    
    def export_tml(self, 
                   metadata_objects: List[Dict[str, Any]] = None,
                   export_associated: bool = False,
                   export_fqn: bool = False,
                   edoc_format: str = "JSON",
                   export_schema_version: str = "DEFAULT",
                   export_dependent: bool = False,
                   export_connection_as_dependent: bool = False,
                   all_orgs_override: bool = False) -> Dict[str, Any]:
        """
        Export TML (ThoughtSpot Modeling Language) for metadata objects.
        
        Args:
            metadata_objects: List of metadata objects to export. If None or empty, exports all.
            export_associated: Whether to export associated objects
            export_fqn: Whether to export fully qualified names
            edoc_format: Export format ("JSON" or "YAML")
            export_schema_version: Schema version to use ("DEFAULT" or specific version)
            export_dependent: Whether to export dependent objects
            export_connection_as_dependent: Whether to export connections as dependent
            all_orgs_override: Whether to override all organizations
            
        Returns:
            API response containing TML data
        """
        url = f"{self.base_url}/api/rest/2.0/metadata/tml/export"
        
        # Default to empty metadata if none provided
        if metadata_objects is None:
            metadata_objects = [{}]
        
        payload = {
            "metadata": metadata_objects,
            "export_associated": export_associated,
            "export_fqn": export_fqn,
            "edoc_format": edoc_format,
            "export_schema_version": export_schema_version,
            "export_dependent": export_dependent,
            "export_connection_as_dependent": export_connection_as_dependent,
            "all_orgs_override": all_orgs_override
        }
        
        try:
            print(f"📋 Exporting TML with format: {edoc_format}")
            print(f"🌐 API URL: {url}")
            print(f"📊 Metadata objects count: {len(metadata_objects)}")
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ TML export completed successfully")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error exporting TML: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            raise
    

def process_and_analyze_tml(tml_data: Dict[str, Any], liveboard_name: str = None) -> str:
    """
    Process TML data, extract visualizations, analyze for KPIs and attributes, and save final result.
        
        Args:
        tml_data: Raw TML data from API
        liveboard_name: Optional liveboard name for filename
            
        Returns:
        Path to the final analysis file
    """
    try:
        print(f"🔍 Processing TML data and extracting visualizations...")
        
        # Extract visualization data (in memory)
        result = extract_visualization_data(tml_data)
        
        if result['success']:
            print(f"✅ Extracted {result['count']} visualization(s)")
            print(f"📊 Liveboard: {result['liveboard_name']}")
            
            # Now extract KPIs and attributes from the structured visualization data
            try:
                from input_extractor import extract_kpi_from_json, extract_attributes_and_date_from_json, refine_kpis, extract_goal, extract_user_context
                
                print("🤖 Analyzing visualizations for KPIs and attributes...")
                
                # Extract KPIs from the visualization data (raw extraction)
                raw_kpis = extract_kpi_from_json(result, "analysis")
                #print(f"Raw KPIs: {raw_kpis}")
                
                # Refine KPIs (scoring and deduplication)
                #refined_kpis = refine_kpis(raw_kpis)
                refined_kpis = raw_kpis
                
                # Extract attributes and date columns
                attributes, date_column = extract_attributes_and_date_from_json(result, "analysis")
                
                # Extract goal and user context
                goal = extract_goal(result, "analysis")
                user_context = extract_user_context(result, "analysis")
                
                # Create final analysis result (without visualizations)
                final_result = {
                    'success': result['success'],
                    'liveboard_name': result['liveboard_name'],
                    'visualization_count': result['count'],
                    'kpis': refined_kpis,  # Use extracted KPIs directly
                    'attributes': attributes,
                    'date_column': date_column,
                    'goal': goal,
                    'user_context': user_context
                }
                
                print(f"📈 KPIs identified: {len(refined_kpis)} KPIs")
                for kpi_id, kpi_data in refined_kpis.items():
                    chart_type = kpi_data.get('chart_type', 'Unknown')
                    print(f"  - {kpi_data.get('name', kpi_id)} (Type: {chart_type}): {kpi_data.get('description', 'No description')}")
                print(f"📋 Key attributes: {attributes}")
                print(f"📅 Primary date field: {date_column}")
                print(f"🎯 Primary business goal: {goal}")
                print(f"👥 User context: {user_context}")
            except Exception as e:
                print(f"⚠️ Could not extract KPIs and attributes: {e}")
                final_result = {
                    'success': result['success'],
                    'liveboard_name': result['liveboard_name'],
                    'visualization_count': result['count'],
                    'kpis': {"KPI_1": {
                        "name": "Key Performance Indicator",
                        "measure": "primary_measure",
                        "formula": "aggregation_function",
                        "filters": [],
                        "description": "Key performance indicators from the data"
                    }},
                    'attributes': 'Key dimensions for analysis',
                    'date_column': 'Date column for temporal analysis',
                    'goal': 'Monitor key business performance metrics and KPIs to support data-driven decision making.',
                    'user_context': 'Business stakeholders and analysts use this dashboard to monitor performance metrics and make data-driven decisions.',
                    'error': str(e)
                }
        else:
            # If visualization extraction failed
            final_result = {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'liveboard_name': 'Unknown',
                'visualization_count': 0,
                'kpis': {},
                'attributes': '',
                'date_column': '',
                'goal': 'Monitor key business performance metrics and KPIs to support data-driven decision making.',
                'user_context': 'Business stakeholders and analysts use this dashboard to monitor performance metrics and make data-driven decisions.'
            }
        
        # Generate final output filename in TMLs folder
        if liveboard_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"analysis_{liveboard_name}_{timestamp}.json"
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"analysis_{timestamp}.json"
        
        output_file = os.path.join("TMLs", output_filename)
        
        # Create TMLs folder if it doesn't exist
        os.makedirs("TMLs", exist_ok=True)
        
        # Save final analysis result only (no visualizations)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        if final_result['success']:
            print(f"📁 Final analysis saved to: {output_file}")
        else:
            print(f"❌ Error in analysis: {final_result.get('error', 'Unknown error')}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error processing TML data: {e}")
        raise


def export_and_extract_liveboard(liveboard_id: str, liveboard_name: str = None, use_existing_file: bool = False) -> Dict[str, Any]:
    """
    Export TML for a specific liveboard and perform complete analysis pipeline.
    
    Args:
        liveboard_id: The liveboard identifier
        liveboard_name: Optional name for the liveboard (used in filenames)
        use_existing_file: If True, try to read from existing TML file instead of calling API
        
    Returns:
        Dictionary with file paths and results
    """
    try:
        print(f"🚀 Starting TML export and analysis for liveboard: {liveboard_id}")
        if liveboard_name:
            print(f"📋 Liveboard name: {liveboard_name}")
        print("=" * 60)
        
        # Step 1: Get TML data (either from file or API)
        if use_existing_file:
            tml_data = load_existing_tml_file(liveboard_name or "unknown")
            if tml_data is None:
                print("⚠️ Existing file not found, falling back to API call...")
                use_existing_file = False
        
        if not use_existing_file:
            # Initialize API client and call API
            try:
                print("🔧 Initializing ThoughtSpot API client...")
                api = ThoughtSpotAPI()
                print("✅ ThoughtSpot API client initialized successfully")
            except Exception as init_error:
                print(f"❌ Failed to initialize ThoughtSpot API: {init_error}")
                print("💡 Please check your THOUGHTSPOT_BASE_URL and THOUGHTSPOT_AUTH_TOKEN in the Settings tab")
                raise
            
            metadata_objects = [
                {
                    "type": "LIVEBOARD",
                    "identifier": liveboard_id
                }
            ]
            
            try:
                print(f"📞 Calling ThoughtSpot API to export liveboard: {liveboard_id}")
                tml_data = api.export_tml(metadata_objects=metadata_objects)
                print(f"📊 TML export completed successfully: {type(tml_data)}")
            except Exception as api_error:
                print(f"❌ ThoughtSpot API call failed: {api_error}")
                print("💡 Please verify the liveboard ID and your ThoughtSpot access permissions")
                raise
            
            # Optionally save the TML data for future use
            if liveboard_name:
                try:
                    save_tml_to_file(tml_data, liveboard_name)
                except Exception as e:
                    print(f"⚠️ Could not save TML file for future use: {e}")
        
        # Step 2 & 3: Process TML → Extract Visualizations → Analyze KPIs/Attributes → Save Final Result
        analysis_file = process_and_analyze_tml(tml_data, liveboard_name)
        
        print("\n" + "=" * 60)
        print("✅ Complete! Analysis file created:")
        print(f"  📊 Final Analysis: {analysis_file}")
        
        return {
            'liveboard_id': liveboard_id,
            'liveboard_name': liveboard_name,
            'analysis_file': analysis_file,
            'used_existing_file': use_existing_file,
            'api_result': tml_data
        }
        
    except Exception as e:
        print(f"❌ Error processing liveboard {liveboard_id}: {e}")
        return None


def load_existing_tml_file(scenario: str) -> Dict[str, Any]:
    """
    Load existing TML file from the TMLs folder.
    
    Args:
        scenario: The scenario name (e.g., "PG", "CMO", "Support", "SpotIQ")
        
    Returns:
        TML data dictionary or None if file doesn't exist
    """
    try:
        # Construct filename
        filename = f"tml_export_{scenario}.json"
        filepath = os.path.join("TMLs", filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"📁 File not found: {filepath}")
            return None
        
        # Read and parse the file
        print(f"📁 Loading existing TML file: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            tml_data = json.load(f)
        
        print(f"✅ Successfully loaded TML data from existing file")
        return tml_data
        
    except Exception as e:
        print(f"❌ Error loading existing TML file: {e}")
        return None


def save_tml_to_file(tml_data: Dict[str, Any], scenario: str) -> str:
    """
    Save TML data to a standard filename for future use.
    
    Args:
        tml_data: The TML data to save
        scenario: The scenario name for the filename
        
    Returns:
        Path to the saved file
    """
    try:
        # Create TMLs folder if it doesn't exist
        os.makedirs("TMLs", exist_ok=True)
        
        # Construct filename
        filename = f"tml_export_{scenario}.json"
        filepath = os.path.join("TMLs", filename)
        
        # Save the file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tml_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 TML data saved for future use: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error saving TML file: {e}")
        raise


def main():
    """Main function - can be controlled via environment variables or hardcoded configuration."""
    
    # Check for environment variables first (for API calls)
    scenario_name = os.getenv('SCENARIO_NAME')
    liveboard_id = os.getenv('LIVEBOARD_ID')
    
    if scenario_name and liveboard_id:
        # Called from API - use environment variables
        print(f"🎯 API Mode: Creating scenario '{scenario_name}' with liveboard: {liveboard_id}")
        result = export_and_extract_liveboard(liveboard_id, scenario_name)
        return result
    
    # ========================================
    # CONFIGURATION - CHANGE THESE VARIABLES (for direct execution)
    # ========================================
    LIVEBOARD_TYPE = "CMO"  # Options: "PG", "CMO", "Support", "SpotIQ"
    USE_EXISTING_FILE = True   # Set to True to read from existing TML file, False to call API
    #To reference a file, the file name format should be tml_export_{liveboard_name}.json
    # Liveboard configurations
    LIVEBOARDS = {
        "PG": {
            "id": "36183de4-035f-48df-b364-9233a8334aba",
            "name": "PG"
        },
        "CMO": {
            "id": "624a034c-4782-45a8-a553-aa37aed139c0",
            "name": "CMO"
        },
        "Support": {
            "id": "1d8000d8-6225-4202-b56c-786fd73f95ad",
            "name": "Support"
        },
        "SpotIQ": {
            "id": "2d4bd5f7-8c55-403c-804d-f28a8e2bbb81",
            "name": "SpotIQ"
        }
    }
    
    # Get the selected liveboard configuration
    if LIVEBOARD_TYPE not in LIVEBOARDS:
        print(f"❌ Error: Unknown liveboard type '{LIVEBOARD_TYPE}'")
        print(f"Available options: {list(LIVEBOARDS.keys())}")
        return None
    
    config = LIVEBOARDS[LIVEBOARD_TYPE]
    liveboard_id = config["id"]
    liveboard_name = config["name"]
    
    print(f"🎯 Direct Mode: Selected liveboard: {LIVEBOARD_TYPE}")
    print(f"🆔 Liveboard ID: {liveboard_id}")
    print(f"📁 Use existing file: {USE_EXISTING_FILE}")
    
    if USE_EXISTING_FILE:
        expected_file = f"TMLs/tml_export_{liveboard_name}.json"
        if os.path.exists(expected_file):
            print(f"✅ Found existing TML file: {expected_file}")
        else:
            print(f"⚠️ Existing TML file not found: {expected_file}")
            print("   Will fall back to API call if file is missing")
        
    result = export_and_extract_liveboard(liveboard_id, liveboard_name, USE_EXISTING_FILE)
    return result


if __name__ == "__main__":
    main()