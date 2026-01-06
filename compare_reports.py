#!/usr/bin/env python3
"""
Report Comparison Tool
Compare multiple analysis reports side-by-side.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_report(report_path: Path) -> dict:
    """Load a report file and extract metadata."""
    if not report_path.exists():
        return None
    
    content = report_path.read_text()
    
    # Extract key information
    lines = content.split('\n')
    metadata = {
        'path': str(report_path),
        'size': len(content),
        'lines': len(lines)
    }
    
    # Try to extract header info
    for line in lines[:10]:
        if 'Generated on:' in line:
            metadata['generated_on'] = line.split('Generated on:')[1].strip()
        if 'Analysis Duration:' in line:
            metadata['duration'] = line.split('Analysis Duration:')[1].strip()
        if 'LLM Provider:' in line:
            metadata['llm_provider'] = line.split('LLM Provider:')[1].strip()
    
    metadata['content'] = content
    return metadata


def compare_reports(report_paths: list):
    """Compare multiple reports."""
    print("="*80)
    print("📊 REPORT COMPARISON TOOL")
    print("="*80)
    
    reports = []
    for path in report_paths:
        report = load_report(Path(path))
        if report:
            reports.append(report)
        else:
            print(f"⚠️  Could not load: {path}")
    
    if len(reports) < 2:
        print("❌ Need at least 2 reports to compare")
        return
    
    print(f"\n✅ Loaded {len(reports)} reports for comparison\n")
    
    # Summary table
    print("REPORT SUMMARY")
    print("-" * 80)
    print(f"{'#':<3} {'Path':<40} {'Size':<10} {'LLM':<15} {'Duration':<15}")
    print("-" * 80)
    
    for i, report in enumerate(reports, 1):
        path_short = Path(report['path']).name
        size = f"{report['size']/1024:.1f}KB"
        llm = report.get('llm_provider', 'Unknown')
        duration = report.get('duration', 'N/A')
        
        print(f"{i:<3} {path_short:<40} {size:<10} {llm:<15} {duration:<15}")
    
    # Detailed comparison
    print(f"\n{'='*80}")
    print("DETAILED COMPARISON")
    print("="*80)
    
    # Size comparison
    sizes = [r['size'] for r in reports]
    print(f"\n📏 Report Size:")
    print(f"   Smallest: {min(sizes)/1024:.1f}KB")
    print(f"   Largest:  {max(sizes)/1024:.1f}KB")
    print(f"   Average:  {sum(sizes)/len(sizes)/1024:.1f}KB")
    
    # Duration comparison (if available)
    durations = []
    for r in reports:
        dur_str = r.get('duration', '')
        if 'minutes' in dur_str:
            try:
                minutes = float(dur_str.split('minutes')[0].strip())
                durations.append(minutes)
            except:
                pass
    
    if durations:
        print(f"\n⏱️  Analysis Duration:")
        print(f"   Fastest: {min(durations):.2f} minutes")
        print(f"   Slowest: {max(durations):.2f} minutes")
        print(f"   Average: {sum(durations)/len(durations):.2f} minutes")
    
    # LLM distribution
    llms = [r.get('llm_provider', 'Unknown') for r in reports]
    llm_counts = {}
    for llm in llms:
        llm_counts[llm] = llm_counts.get(llm, 0) + 1
    
    print(f"\n🤖 LLM Distribution:")
    for llm, count in llm_counts.items():
        print(f"   {llm}: {count} report(s)")
    
    # Content analysis
    print(f"\n📝 Content Analysis:")
    for i, report in enumerate(reports, 1):
        content = report['content']
        
        # Count key sections
        insights_count = content.count('Insight:')
        recommendations_count = content.count('Recommendation:')
        
        print(f"\n   Report {i} ({Path(report['path']).name}):")
        print(f"      Lines: {report['lines']}")
        print(f"      Insights mentioned: {insights_count}")
        print(f"      Recommendations mentioned: {recommendations_count}")
    
    # Save comparison
    output_file = Path('report_comparison_') / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    output_file.parent.mkdir(exist_ok=True)
    
    print(f"\n✅ Comparison complete!")
    print(f"   View individual reports for detailed content differences")


def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_reports.py <report1> <report2> [report3] ...")
        print("\nExample:")
        print("  python compare_reports.py \\")
        print("    backend/scenario1/scenario1_v001/scenario1_report_*.txt \\")
        print("    backend/scenario1/scenario1_v002/scenario1_report_*.txt")
        sys.exit(1)
    
    report_paths = sys.argv[1:]
    compare_reports(report_paths)


if __name__ == "__main__":
    main()

