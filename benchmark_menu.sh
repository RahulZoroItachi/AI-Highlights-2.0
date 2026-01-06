#!/bin/bash
# Benchmark Menu - Easy access to benchmark tools

show_menu() {
    clear
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           🎯 AI ANALYSIS BENCHMARK MENU                       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 QUICK ACTIONS:"
    echo "   1) Run Quick Test (2 configs, ~10-20 min)"
    echo "   2) Run Temperature Test (5 configs, ~25-150 min)"
    echo "   3) Run Model Comparison (6 configs, ~30-180 min)"
    echo "   4) Run Full Benchmark (9 configs, ~45-270 min)"
    echo ""
    echo "⚙️  CONFIGURATION:"
    echo "   5) Edit benchmark_config.json"
    echo "   6) View current configuration"
    echo "   7) Create custom configuration"
    echo ""
    echo "📈 RESULTS:"
    echo "   8) View latest benchmark results"
    echo "   9) Compare specific reports"
    echo "   10) List all benchmark runs"
    echo ""
    echo "📖 HELP:"
    echo "   11) View Quick Start Guide"
    echo "   12) View Full Documentation"
    echo "   13) Show Example Configurations"
    echo ""
    echo "   0) Exit"
    echo ""
    echo -n "Select option: "
}

run_quick_test() {
    echo "🚀 Running Quick Test..."
    cp benchmark_examples/quick_test.json benchmark_config.json
    python run_benchmark.py
    read -p "Press Enter to continue..."
}

run_temperature_test() {
    echo "🌡️  Running Temperature Test..."
    cp benchmark_examples/temperature_test.json benchmark_config.json
    python run_benchmark.py
    read -p "Press Enter to continue..."
}

run_model_comparison() {
    echo "🤖 Running Model Comparison..."
    cp benchmark_examples/model_comparison.json benchmark_config.json
    python run_benchmark.py
    read -p "Press Enter to continue..."
}

run_full_benchmark() {
    echo "🎯 Running Full Benchmark..."
    # Use existing benchmark_config.json
    python run_benchmark.py
    read -p "Press Enter to continue..."
}

edit_config() {
    ${EDITOR:-nano} benchmark_config.json
}

view_config() {
    clear
    echo "═══════════════════════════════════════════════════════════════"
    echo "📋 CURRENT CONFIGURATION"
    echo "═══════════════════════════════════════════════════════════════"
    cat benchmark_config.json
    echo ""
    read -p "Press Enter to continue..."
}

create_custom_config() {
    clear
    echo "═══════════════════════════════════════════════════════════════"
    echo "🎨 CREATE CUSTOM CONFIGURATION"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Available examples:"
    ls -1 benchmark_examples/
    echo ""
    read -p "Copy from example (or press Enter to create from scratch): " example
    
    if [ -n "$example" ] && [ -f "benchmark_examples/$example" ]; then
        cp "benchmark_examples/$example" benchmark_config.json
        echo "✓ Copied $example to benchmark_config.json"
        echo ""
        read -p "Edit now? (y/n): " edit
        if [ "$edit" = "y" ]; then
            ${EDITOR:-nano} benchmark_config.json
        fi
    else
        ${EDITOR:-nano} benchmark_config.json
    fi
}

view_latest_results() {
    clear
    echo "═══════════════════════════════════════════════════════════════"
    echo "📊 LATEST BENCHMARK RESULTS"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Find latest benchmark directory
    latest=$(find backend/*/benchmark_* -type d 2>/dev/null | sort -r | head -1)
    
    if [ -z "$latest" ]; then
        echo "❌ No benchmark results found"
    else
        echo "📁 Location: $latest"
        echo ""
        
        # Show comparison report if exists
        report=$(find "$latest" -name "benchmark_comparison_*.txt" | head -1)
        if [ -n "$report" ]; then
            cat "$report"
        else
            echo "⚠️  Comparison report not found"
        fi
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

compare_reports() {
    clear
    echo "═══════════════════════════════════════════════════════════════"
    echo "📈 COMPARE REPORTS"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Available scenarios:"
    ls -d backend/*/ 2>/dev/null | grep -v "__pycache__" | grep -v "input_populator" | grep -v "TMLs"
    echo ""
    read -p "Enter scenario name: " scenario
    
    if [ -z "$scenario" ]; then
        echo "❌ No scenario entered"
        read -p "Press Enter to continue..."
        return
    fi
    
    echo ""
    echo "Available versions for $scenario:"
    ls -d backend/${scenario}/${scenario}_v*/ 2>/dev/null
    echo ""
    echo "Enter version numbers to compare (space-separated, e.g., 001 002 003):"
    read -p "Versions: " versions
    
    if [ -z "$versions" ]; then
        echo "❌ No versions entered"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Build report paths
    reports=""
    for ver in $versions; do
        report=$(find "backend/${scenario}/${scenario}_v${ver}/" -name "${scenario}_report_*.txt" 2>/dev/null | head -1)
        if [ -n "$report" ]; then
            reports="$reports $report"
        fi
    done
    
    if [ -z "$reports" ]; then
        echo "❌ No reports found"
    else
        python compare_reports.py $reports
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

list_benchmarks() {
    clear
    echo "═══════════════════════════════════════════════════════════════"
    echo "📋 ALL BENCHMARK RUNS"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    find backend/*/benchmark_* -type d 2>/dev/null | while read dir; do
        echo "📁 $dir"
        config="$dir/benchmark_config.json"
        if [ -f "$config" ]; then
            scenario=$(grep -o '"scenario": *"[^"]*"' "$config" | cut -d'"' -f4)
            configs=$(grep -c '"name":' "$config")
            echo "   Scenario: $scenario"
            echo "   Configurations: $configs"
        fi
        echo ""
    done
    
    read -p "Press Enter to continue..."
}

show_quick_start() {
    clear
    cat BENCHMARK_QUICK_START.md | less
}

show_full_docs() {
    clear
    cat BENCHMARK_README.md | less
}

show_examples() {
    clear
    echo "═══════════════════════════════════════════════════════════════"
    echo "📚 EXAMPLE CONFIGURATIONS"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    for example in benchmark_examples/*.json; do
        echo "📄 $(basename $example)"
        echo "─────────────────────────────────────────────────────────"
        cat "$example"
        echo ""
        echo ""
    done
    
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1) run_quick_test ;;
        2) run_temperature_test ;;
        3) run_model_comparison ;;
        4) run_full_benchmark ;;
        5) edit_config ;;
        6) view_config ;;
        7) create_custom_config ;;
        8) view_latest_results ;;
        9) compare_reports ;;
        10) list_benchmarks ;;
        11) show_quick_start ;;
        12) show_full_docs ;;
        13) show_examples ;;
        0) echo "👋 Goodbye!"; exit 0 ;;
        *) echo "❌ Invalid option"; sleep 1 ;;
    esac
done

