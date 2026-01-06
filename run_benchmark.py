#!/usr/bin/env python3
"""
Benchmark Runner for AI Analysis Platform
Runs the same scenario with different LLM configurations and compares results.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, set_key

# Load environment variables
env_file_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(env_file_path)


def update_env_file(config: dict):
    """Update .env file with the configuration."""
    env_vars_to_update = {}
    
    if config.get('llm_provider'):
        env_vars_to_update['LLM_PROVIDER'] = config['llm_provider']
    
    if config.get('claude_model'):
        env_vars_to_update['CLAUDE_MODEL'] = config['claude_model']
    
    if config.get('openai_model'):
        env_vars_to_update['OPENAI_MODEL'] = config['openai_model']
    
    if config.get('gemini_model'):
        env_vars_to_update['GEMINI_MODEL'] = config['gemini_model']
    
    # Update .env file
    for key, value in env_vars_to_update.items():
        set_key(env_file_path, key, value)
        print(f"  ✓ Set {key}={value}")
    
    # Reload environment
    load_dotenv(env_file_path, override=True)


def run_analysis(scenario: str, config_name: str, load_previous_plan=None, load_previous_data=None):
    """Run analysis with current environment configuration."""
    print(f"\n{'='*80}")
    print(f"🚀 Running: {config_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    # Set environment variables for the subprocess
    env = os.environ.copy()
    env['ANALYSIS_SCENARIO'] = scenario
    
    if load_previous_plan:
        env['LOAD_PREVIOUS_PLAN'] = str(load_previous_plan)
    if load_previous_data:
        env['LOAD_PREVIOUS_DATA'] = str(load_previous_data)
    
    # Run main.py
    try:
        result = subprocess.run(
            [sys.executable, 'main.py'],
            cwd=Path(__file__).parent / 'backend',
            env=env,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Completed successfully in {elapsed_time:.1f}s")
            return {
                'success': True,
                'elapsed_time': elapsed_time,
                'config_name': config_name,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            print(f"❌ Failed with return code {result.returncode}")
            print(f"Error output: {result.stderr[-500:]}")  # Last 500 chars
            return {
                'success': False,
                'elapsed_time': elapsed_time,
                'config_name': config_name,
                'error': result.stderr,
                'returncode': result.returncode
            }
    
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print(f"⏱️ Timeout after {elapsed_time:.1f}s")
        return {
            'success': False,
            'elapsed_time': elapsed_time,
            'config_name': config_name,
            'error': 'Timeout after 1 hour'
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Exception: {e}")
        return {
            'success': False,
            'elapsed_time': elapsed_time,
            'config_name': config_name,
            'error': str(e)
        }


def generate_comparison_report(benchmark_results: list, scenario: str, output_dir: Path):
    """Generate a comparison report of all benchmark results."""
    report_content = f"""BENCHMARK COMPARISON REPORT
{'='*80}
Scenario: {scenario}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Configurations Tested: {len(benchmark_results)}

{'='*80}
SUMMARY OF RESULTS
{'='*80}

"""
    
    # Sort by success and then by elapsed time
    sorted_results = sorted(benchmark_results, key=lambda x: (not x['success'], x['elapsed_time']))
    
    for i, result in enumerate(sorted_results, 1):
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        elapsed_min = result['elapsed_time'] / 60
        
        report_content += f"{i}. {result['config_name']}\n"
        report_content += f"   Status: {status}\n"
        report_content += f"   Time: {elapsed_min:.2f} minutes ({result['elapsed_time']:.1f} seconds)\n"
        
        if not result['success']:
            report_content += f"   Error: {result.get('error', 'Unknown error')[:200]}\n"
        
        report_content += "\n"
    
    # Statistics
    successful = [r for r in benchmark_results if r['success']]
    failed = [r for r in benchmark_results if not r['success']]
    
    report_content += f"\n{'='*80}\n"
    report_content += f"STATISTICS\n"
    report_content += f"{'='*80}\n\n"
    report_content += f"Successful Runs: {len(successful)}/{len(benchmark_results)}\n"
    report_content += f"Failed Runs: {len(failed)}/{len(benchmark_results)}\n"
    
    if successful:
        avg_time = sum(r['elapsed_time'] for r in successful) / len(successful)
        min_time = min(r['elapsed_time'] for r in successful)
        max_time = max(r['elapsed_time'] for r in successful)
        fastest = min(successful, key=lambda x: x['elapsed_time'])
        
        report_content += f"\nSuccessful Runs Time Statistics:\n"
        report_content += f"  Average: {avg_time/60:.2f} minutes\n"
        report_content += f"  Fastest: {min_time/60:.2f} minutes ({fastest['config_name']})\n"
        report_content += f"  Slowest: {max_time/60:.2f} minutes\n"
    
    # Save report
    report_file = output_dir / f"benchmark_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(f"\n📊 Comparison report saved to: {report_file}")
    
    # Also print to console
    print(f"\n{report_content}")
    
    return report_file


def main():
    """Main benchmark runner."""
    print("="*80)
    print("🎯 AI ANALYSIS BENCHMARK RUNNER")
    print("="*80)
    
    # Load benchmark configuration
    config_file = Path(__file__).parent / 'benchmark_config.json'
    
    if not config_file.exists():
        print(f"❌ Benchmark configuration file not found: {config_file}")
        print("Please create benchmark_config.json with your test configurations.")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        benchmark_config = json.load(f)
    
    scenario = benchmark_config.get('scenario')
    configurations = benchmark_config.get('configurations', [])
    load_previous_plan = benchmark_config.get('load_previous_plan')
    load_previous_data = benchmark_config.get('load_previous_data')
    
    if not scenario:
        print("❌ No scenario specified in benchmark_config.json")
        sys.exit(1)
    
    if not configurations:
        print("❌ No configurations specified in benchmark_config.json")
        sys.exit(1)
    
    print(f"\n📋 Benchmark Configuration:")
    print(f"   Scenario: {scenario}")
    print(f"   Configurations to test: {len(configurations)}")
    print(f"   Load previous plan: {load_previous_plan or 'Generate new'}")
    print(f"   Load previous data: {load_previous_data or 'Fetch fresh'}")
    print(f"   Description: {benchmark_config.get('description', 'N/A')}")
    
    # Confirm with user
    print(f"\n⚠️  This will run {len(configurations)} analysis runs.")
    print("   This may take several hours depending on your configurations.")
    response = input("\n   Continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Benchmark cancelled.")
        sys.exit(0)
    
    # Create output directory for this benchmark run
    benchmark_dir = Path(__file__).parent / 'backend' / scenario / f'benchmark_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Results will be saved to: {benchmark_dir}")
    
    # Save benchmark configuration
    with open(benchmark_dir / 'benchmark_config.json', 'w') as f:
        json.dump(benchmark_config, f, indent=2)
    
    # Run each configuration
    benchmark_results = []
    total_start_time = time.time()
    
    for i, config in enumerate(configurations, 1):
        config_name = config.get('name', f'Configuration {i}')
        
        print(f"\n{'='*80}")
        print(f"Configuration {i}/{len(configurations)}: {config_name}")
        print(f"{'='*80}")
        
        # Update .env file with this configuration
        print("\n🔧 Updating environment configuration...")
        update_env_file(config)
        
        # Wait a moment for environment to be ready
        time.sleep(2)
        
        # Run analysis
        result = run_analysis(
            scenario=scenario,
            config_name=config_name,
            load_previous_plan=load_previous_plan,
            load_previous_data=load_previous_data
        )
        
        # Add configuration details to result
        result['configuration'] = config
        benchmark_results.append(result)
        
        # Save intermediate results
        with open(benchmark_dir / 'results.json', 'w') as f:
            json.dump(benchmark_results, f, indent=2, default=str)
        
        print(f"\n✓ Configuration {i}/{len(configurations)} completed")
        print(f"  Success rate so far: {sum(1 for r in benchmark_results if r['success'])}/{len(benchmark_results)}")
    
    total_elapsed = time.time() - total_start_time
    
    print(f"\n{'='*80}")
    print(f"🎉 BENCHMARK COMPLETED!")
    print(f"{'='*80}")
    print(f"Total time: {total_elapsed/60:.2f} minutes")
    print(f"Successful runs: {sum(1 for r in benchmark_results if r['success'])}/{len(benchmark_results)}")
    
    # Generate comparison report
    generate_comparison_report(benchmark_results, scenario, benchmark_dir)
    
    print(f"\n📁 All results saved to: {benchmark_dir}")
    print(f"\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()

