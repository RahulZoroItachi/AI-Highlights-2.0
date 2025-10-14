"""
Run logging module for storing plans and data with versioning.
Creates scenario-specific folders and manages versioned file storage.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class RunLogger:
    """Manages run logging with versioned storage for plans and data."""
    
    def __init__(self, scenario: str, backend_dir: str = None):
        """
        Initialize the run logger for a specific scenario.
        
        Args:
            scenario: Scenario name (e.g., 'support', 'pg', 'cmo', 'ta')
            backend_dir: Backend directory path (defaults to current directory)
        """
        self.scenario = scenario.lower()
        self.backend_dir = Path(backend_dir) if backend_dir else Path(__file__).parent
        self.scenario_dir = self.backend_dir / self.scenario
        
        # Create scenario directory if it doesn't exist
        self._ensure_scenario_directory()
        
        # Get current date for file naming
        self.date_str = datetime.now().strftime("%Y%m%d")
        
        # Initialize version for this run (will be set when first file is saved)
        self.current_version = None
        self.version_dir = None
        
        # Append mode - when adding files to existing version
        self.append_mode = False
        self.append_version = None
    
    def _ensure_scenario_directory(self):
        """Create scenario directory if it doesn't exist."""
        if not self.scenario_dir.exists():
            self.scenario_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created scenario directory: {self.scenario_dir}")
        else:
            print(f"📁 Using existing scenario directory: {self.scenario_dir}")
    
    def enable_append_mode(self, version: int) -> None:
        """
        Enable append mode to add files to an existing version folder.
        
        Args:
            version: Version number to append to
        """
        self.append_mode = True
        self.append_version = version
        self.version_dir = self._get_version_directory(version)
        print(f"📁 Enabled append mode for version: {version}")
    
    def _initialize_run_version(self) -> int:
        """
        Initialize the version for this run. This should be called once at the start of a run.
        
        Returns:
            Version number for this run
        """
        if self.append_mode:
            # In append mode, use the specified version
            if self.current_version is None:
                self.current_version = self.append_version
                print(f"📁 Using append mode for version: {self.current_version}")
            return self.current_version
        
        if self.current_version is None:
            self.current_version = self._get_next_version()
            self.version_dir = self._get_version_directory(self.current_version)
            print(f"📁 Initialized new run version: {self.current_version}")
        return self.current_version
    
    def _get_version_directory(self, version: int) -> Path:
        """
        Get the version subdirectory path for a specific version.
        
        Args:
            version: Version number
            
        Returns:
            Path to the version subdirectory
        """
        version_dir = self.scenario_dir / f"{self.scenario}_v{version:03d}"
        version_dir.mkdir(parents=True, exist_ok=True)
        return version_dir
    
    def _get_next_version(self) -> int:
        """
        Get the next version number for a new run in the scenario directory.
        
        Returns:
            Next version number
        """
        # Look for existing version subdirectories with the pattern: scenario_v{version}
        version_dirs = list(self.scenario_dir.glob(f"{self.scenario}_v*"))
        
        if not version_dirs:
            return 1
        
        # Extract version numbers from directory names
        versions = []
        for dir_path in version_dirs:
            try:
                # Extract version from directory name: scenario_v{version}
                dir_name = dir_path.name
                if dir_name.startswith(f"{self.scenario}_v"):
                    version = int(dir_name.split('_v')[1])
                    versions.append(version)
            except (ValueError, IndexError):
                continue
        
        # Return next version number
        return max(versions) + 1 if versions else 1
    
    def save_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Save the generated plan to a versioned JSON file.
        
        Args:
            plan_data: The plan data (llm_response_3) to save
            
        Returns:
            Path to the saved file
        """
        # Initialize version if not already done
        self._initialize_run_version()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.scenario}_plan_{timestamp}.json"
        file_path = self.version_dir / filename
        
        try:
            print(f"🔧 Debug: About to serialize plan data with {len(plan_data)} keys")
            print(f"🔧 Debug: Plan data keys: {list(plan_data.keys())}")
            
            # Check for potential issues with the data structure
            if 'phases' in plan_data:
                print(f"🔧 Debug: Plan has {len(plan_data['phases'])} phases")
            
            # Try to serialize with a timeout approach
            print(f"🔧 Debug: Starting JSON serialization...")
            
            # First, try a quick JSON serialization check to see if there are any obvious issues
            try:
                json_str = json.dumps(plan_data, ensure_ascii=False)
                print(f"🔧 Debug: JSON serialization test successful, length: {len(json_str)}")
                
                # If that works, write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(plan_data, f, indent=2, ensure_ascii=False)
                print(f"🔧 Debug: JSON serialization completed successfully")
                
            except (TypeError, ValueError, RecursionError) as json_error:
                print(f"🔧 Debug: JSON serialization failed with {type(json_error).__name__}: {json_error}")
                
                # Try a safer serialization approach by removing potentially problematic fields
                safe_plan_data = {}
                for key, value in plan_data.items():
                    try:
                        # Test if this field can be serialized
                        json.dumps(value)
                        safe_plan_data[key] = value
                        print(f"🔧 Debug: Field '{key}' is safe to serialize")
                    except Exception as field_error:
                        print(f"🔧 Debug: Field '{key}' failed serialization: {field_error}")
                        safe_plan_data[key] = f"<SERIALIZATION_ERROR: {str(field_error)}>"
                
                # Try to save the safe version
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(safe_plan_data, f, indent=2, ensure_ascii=False)
                print(f"🔧 Debug: Safe JSON serialization completed")
            
            print(f"💾 Plan saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Error saving plan: {e}")
            print(f"🔧 Debug: Error type: {type(e).__name__}")
            print(f"🔧 Debug: Error details: {str(e)}")
            
            # Try to save basic info at least
            try:
                basic_info = {
                    "error": f"Failed to save full plan: {str(e)}",
                    "keys": list(plan_data.keys()) if isinstance(plan_data, dict) else "Not a dict",
                    "type": str(type(plan_data)),
                    "timestamp": datetime.now().isoformat()
                }
                error_file = file_path.with_suffix('.error.json')
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(basic_info, f, indent=2, ensure_ascii=False)
                print(f"🔧 Debug: Error info saved to: {error_file}")
            except Exception as fallback_error:
                print(f"🔧 Debug: Even fallback save failed: {fallback_error}")
            
            raise
    
    def save_data_to_json(self, fetched_data: Dict[str, Any]) -> str:
        """
        Save fetched data to a JSON file with raw data.
        
        Args:
            fetched_data: Data fetched from APIs
            
        Returns:
            Path to the saved JSON file
        """
        # Initialize version if not already done
        self._initialize_run_version()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.scenario}_data_{timestamp}.json"
        file_path = self.version_dir / filename
        
        try:
            # Simple structure: data { id { whole_data }}
            data_structure = {}
            
            for answer_id, data_info in fetched_data.items():
                # Store the entire data_info as-is
                data_structure[answer_id] = data_info
            
            # Write to JSON file without formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_structure, f, ensure_ascii=False)
            
            print(f"💾 Raw data saved to JSON: {file_path}")
            print(f"📊 Total steps: {len(fetched_data)}")
            for answer_id, data_info in fetched_data.items():
                if 'error' in data_info:
                    print(f"  {answer_id}: Error - {data_info['error']}")
                else:
                    row_count = len(data_info.get('data', []))
                    print(f"  {answer_id}: {row_count} rows")
            
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Error saving data to JSON: {e}")
            raise

    def save_data_to_text(self, fetched_data: Dict[str, Any]) -> str:
        """
        Save fetched data to a text file (summary view).
        
        Args:
            fetched_data: Data fetched from APIs
            
        Returns:
            Path to the saved text file
        """
        # Initialize version if not already done
        self._initialize_run_version()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.scenario}_data_summary_{timestamp}.txt"
        file_path = self.version_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Data Analysis Results - {self.scenario}\n")
                f.write(f"Generated on: {self.date_str}\n")
                f.write("=" * 50 + "\n\n")
                
                for answer_id, data_info in fetched_data.items():
                    f.write(f"--- {answer_id}: {data_info.get('original_step_title', 'Unknown')} ---\n")
                    
                    if 'error' in data_info:
                        f.write(f"Error: {data_info['error']}\n\n")
                        continue
                    
                    if 'data' in data_info and data_info['data']:
                        f.write(f"Row count: {len(data_info['data'])}\n")
                        f.write("Data:\n")
                        
                        # Write data in a readable format
                        for i, row in enumerate(data_info['data'][:10]):  # Show first 10 rows
                            f.write(f"Row {i+1}: {row}\n")
                        
                        if len(data_info['data']) > 10:
                            f.write(f"... and {len(data_info['data']) - 10} more rows\n")
                    else:
                        f.write("No data available\n")
                    
                    f.write("\n" + "-" * 30 + "\n\n")
            
            print(f"💾 Data summary saved to text file: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Error saving data to text file: {e}")
            raise

    def save_analysis_results(self, analysis_results: Dict[str, Any]) -> str:
        """
        Save analysis results to a JSON file.
        
        Args:
            analysis_results: Analysis results from LLM calls
            
        Returns:
            Path to the saved JSON file
        """
        # Initialize version if not already done
        self._initialize_run_version()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.scenario}_analysis_{timestamp}.json"
        file_path = self.version_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Analysis results saved to JSON: {file_path}")
            print(f"📊 Total analysis steps: {len(analysis_results)}")
            for step_id, result in analysis_results.items():
                if 'error' in result:
                    print(f"  {step_id}: Error - {result['error']}")
                elif result.get('status') == 'completed':
                    print(f"  {step_id}: Completed - {result.get('title', 'Unknown')}")
                else:
                    print(f"  {step_id}: {result.get('status', 'Unknown')} - {result.get('title', 'Unknown')}")
            
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Error saving analysis results: {e}")
            raise
    
    def list_previous_runs(self) -> Dict[str, list]:
        """
        List all previous runs for this scenario.
        
        Returns:
            Dictionary with 'plans', 'data', and 'analysis' lists of file paths
        """
        plans = []
        data_files = []
        analysis_files = []
        
        # Find all version subdirectories
        version_dirs = list(self.scenario_dir.glob(f"{self.scenario}_v*"))
        
        for version_dir in version_dirs:
            # Find plan files in this version directory
            for file_path in version_dir.glob(f"{self.scenario}_plan_*.json"):
                plans.append(str(file_path))
            
            # Find data files in this version directory
            for file_path in version_dir.glob(f"{self.scenario}_data_*.json"):
                data_files.append(str(file_path))
            
            # Find analysis files in this version directory
            for file_path in version_dir.glob(f"{self.scenario}_analysis_*.json"):
                analysis_files.append(str(file_path))
        
        return {
            'plans': sorted(plans),
            'data': sorted(data_files),
            'analysis': sorted(analysis_files)
        }
    
    def load_plan(self, version: int = None) -> Optional[Dict[str, Any]]:
        """
        Load a specific plan version or the latest plan.
        
        Args:
            version: Specific version to load (None for latest)
            
        Returns:
            Plan data or None if not found
        """
        if version is None:
            # Load latest plan (highest version number)
            version_dirs = list(self.scenario_dir.glob(f"{self.scenario}_v*"))
            if not version_dirs:
                print(f"⚠️ No previous plans found for scenario: {self.scenario}")
                return None
            
            # Find the highest version number
            latest_version = 0
            latest_version_dir = None
            for version_dir in version_dirs:
                try:
                    dir_name = version_dir.name
                    if dir_name.startswith(f"{self.scenario}_v"):
                        plan_version = int(dir_name.split('_v')[1])
                        if plan_version > latest_version:
                            latest_version = plan_version
                            latest_version_dir = version_dir
                except (ValueError, IndexError):
                    continue
            
            if latest_version_dir is None:
                print(f"⚠️ No valid version directories found for scenario: {self.scenario}")
                return None
            
            # Find plan file in the latest version directory
            plan_files = list(latest_version_dir.glob(f"{self.scenario}_plan_*.json"))
            if not plan_files:
                print(f"⚠️ No plan files found in latest version directory: {latest_version_dir}")
                return None
            
            plan_file = sorted(plan_files)[-1]  # Pick the latest timestamp
        else:
            # Find specific version directory
            version_dir = self.scenario_dir / f"{self.scenario}_v{version:03d}"
            if not version_dir.exists():
                print(f"⚠️ Plan version {version} not found for scenario: {self.scenario}")
                return None
            
            # Find plan file in this version directory
            plan_files = list(version_dir.glob(f"{self.scenario}_plan_*.json"))
            if not plan_files:
                print(f"⚠️ No plan files found in version {version} directory: {version_dir}")
                return None
            
            plan_file = sorted(plan_files)[-1]  # Pick the latest timestamp
        
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            print(f"📖 Loaded plan: {plan_file}")
            return plan_data
        except Exception as e:
            print(f"❌ Error loading plan: {e}")
            return None
    
    def load_data(self, version: int) -> Optional[Dict[str, Any]]:
        """
        Load data from a specific JSON version.
        
        Args:
            version: Specific version to load
            
        Returns:
            Parsed data or None if not found
        """
        # Find specific version directory
        version_dir = self.scenario_dir / f"{self.scenario}_v{version:03d}"
        if not version_dir.exists():
            print(f"⚠️ Data version {version} not found for scenario: {self.scenario}")
            return None
        
        # Find data file in this version directory
        data_files = list(version_dir.glob(f"{self.scenario}_data_*.json"))
        if not data_files:
            print(f"⚠️ No data files found in version {version} directory: {version_dir}")
            return None
        
        # If multiple files with same version, pick the latest timestamp
        data_file = sorted(data_files)[-1]
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 Loaded data from: {data_file}")
            print(f"📋 Data keys: {list(data.keys())}")
            return data
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def save_report(self, report_content: str, version: int = None) -> str:
        """
        Save report content to a text file in the version directory.
        
        Args:
            report_content: The report content to save
            version: Specific version to save to (None for current run)
            
        Returns:
            Path to the saved report file
        """
        if version is None:
            # Initialize version if not already done
            self._initialize_run_version()
            version_dir = self.version_dir
        else:
            version_dir = self._get_version_directory(version)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.scenario}_report_{timestamp}.txt"
        file_path = version_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"📄 Report saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            raise


def get_scenario_logger(scenario: str) -> RunLogger:
    """
    Get a run logger instance for a specific scenario.
    
    Args:
        scenario: Scenario name
        
    Returns:
        RunLogger instance
    """
    return RunLogger(scenario)


def get_scenario_logger_with_append(scenario: str, version: int) -> RunLogger:
    """
    Get a run logger instance for a specific scenario with append mode enabled.
    
    Args:
        scenario: Scenario name
        version: Version number to append to
        
    Returns:
        RunLogger instance with append mode enabled
    """
    logger = RunLogger(scenario)
    logger.enable_append_mode(version)
    return logger

