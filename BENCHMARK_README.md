# 🎯 AI Analysis Benchmark Runner

Automated testing tool to compare different LLM models and configurations on the same scenario.

## 📋 What It Does

The benchmark runner allows you to:
- Run the same analysis scenario with multiple LLM configurations
- Compare different models (Claude, GPT, Gemini)
- Test different temperature settings
- Automatically generate comparison reports
- Track execution time for each configuration

## 🚀 Quick Start

### 1. **Configure Your Benchmark**

Edit `benchmark_config.json`:

```json
{
  "scenario": "your_scenario_name",
  "description": "Description of what you're testing",
  "load_previous_plan": null,
  "load_previous_data": null,
  "configurations": [
    {
      "name": "Claude Sonnet 4 - Standard",
      "llm_provider": "claude",
      "claude_model": "claude-sonnet-4-20250514",
      "temperature": 0.7
    },
    {
      "name": "GPT-4o - Creative",
      "llm_provider": "openai",
      "openai_model": "gpt-4o",
      "temperature": 0.9
    }
  ]
}
```

### 2. **Run the Benchmark**

```bash
# From the project root
python run_benchmark.py

# Or if executable
./run_benchmark.py
```

### 3. **Review Results**

Results are saved in:
```
backend/{scenario}/benchmark_{timestamp}/
├── benchmark_config.json      # Configuration used
├── results.json                # Detailed results
└── benchmark_comparison_*.txt  # Human-readable report
```

## ⚙️ Configuration Options

### Main Configuration

| Field | Description | Required |
|-------|-------------|----------|
| `scenario` | Scenario name to test | ✅ Yes |
| `description` | What you're testing | ❌ No |
| `load_previous_plan` | Version number or null | ❌ No |
| `load_previous_data` | Version number or null | ❌ No |
| `configurations` | Array of test configs | ✅ Yes |

### Per-Configuration Options

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Descriptive name | "Claude - Creative" |
| `llm_provider` | Provider: claude/openai/gemini | "claude" |
| `claude_model` | Claude model name | "claude-sonnet-4-20250514" |
| `openai_model` | OpenAI model name | "gpt-4o" |
| `gemini_model` | Gemini model name | "gemini-2.0-flash-exp" |
| `temperature` | Temperature (0-1 or null for o1/o3) | 0.7 |

## 📊 Available Models

### Claude Models
- `claude-opus-4-20250514` - Claude Opus 4.1
- `claude-sonnet-4-20250514` - Claude Sonnet 4
- `claude-sonnet-4-5-20250929` - Claude Sonnet 4.5
- `claude-3-7-sonnet-20250219` - Claude 3.7 Sonnet
- `claude-haiku-4-20250514` - Claude Haiku 4.5

### OpenAI Models
- `gpt-4o` - GPT-4o
- `gpt-4o-mini` - GPT-4o Mini
- `o1-mini` - o1 Mini (reasoning model, no temperature)
- `o3-mini` - o3 Mini (reasoning model, no temperature)

### Gemini Models
- `gemini-2.0-flash-exp` - Gemini 2.0 Flash
- `gemini-pro` - Gemini Pro

## 🎨 Example Use Cases

### 1. Compare All Available Models

Test the same scenario across all LLM providers to see which performs best:

```json
{
  "scenario": "marketing_funnel_a",
  "description": "Compare all models at standard temperature",
  "configurations": [
    {"name": "Claude Sonnet 4", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.7},
    {"name": "GPT-4o", "llm_provider": "openai", "openai_model": "gpt-4o", "temperature": 0.7},
    {"name": "Gemini 2.0", "llm_provider": "gemini", "gemini_model": "gemini-2.0-flash-exp", "temperature": 0.7}
  ]
}
```

### 2. Temperature Sensitivity Test

Test how temperature affects a specific model:

```json
{
  "scenario": "customer_support",
  "description": "Temperature sensitivity for Claude Sonnet 4",
  "configurations": [
    {"name": "Very Precise (0.1)", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.1},
    {"name": "Precise (0.3)", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.3},
    {"name": "Balanced (0.5)", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.5},
    {"name": "Standard (0.7)", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.7},
    {"name": "Creative (0.9)", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.9}
  ]
}
```

### 3. Model Version Comparison

Compare different versions of the same provider:

```json
{
  "scenario": "marketing_funnel_a",
  "description": "Compare Claude model versions",
  "configurations": [
    {"name": "Sonnet 4", "llm_provider": "claude", "claude_model": "claude-sonnet-4-20250514", "temperature": 0.7},
    {"name": "Sonnet 4.5", "llm_provider": "claude", "claude_model": "claude-sonnet-4-5-20250929", "temperature": 0.7},
    {"name": "Opus 4.1", "llm_provider": "claude", "claude_model": "claude-opus-4-20250514", "temperature": 0.7},
    {"name": "Haiku 4.5", "llm_provider": "claude", "claude_model": "claude-haiku-4-20250514", "temperature": 0.7}
  ]
}
```

### 4. Reasoning vs Standard Models

Compare reasoning models (o1/o3) with standard models:

```json
{
  "scenario": "complex_analysis",
  "description": "Reasoning models vs standard models",
  "configurations": [
    {"name": "GPT-4o Standard", "llm_provider": "openai", "openai_model": "gpt-4o", "temperature": 0.7},
    {"name": "o1-mini Reasoning", "llm_provider": "openai", "openai_model": "o1-mini", "temperature": null},
    {"name": "o3-mini Reasoning", "llm_provider": "openai", "openai_model": "o3-mini", "temperature": null}
  ]
}
```

## 📈 Understanding Results

The benchmark generates:

### 1. **Detailed JSON Results** (`results.json`)
- Full execution logs
- Configuration used
- Success/failure status
- Exact timing data
- Error messages if any

### 2. **Comparison Report** (`benchmark_comparison_*.txt`)
- Ranked list of all configurations
- Success rate
- Time statistics
- Fastest/slowest runs
- Easy-to-read summary

### 3. **Individual Run Outputs**
Each run creates its own version in the scenario folder:
- `{scenario}_plan_{timestamp}.json`
- `{scenario}_data_{timestamp}.json`
- `{scenario}_analysis_{timestamp}.json`
- `{scenario}_report_{timestamp}.txt`

## 💡 Tips & Best Practices

### Performance
- **Use `load_previous_plan` and `load_previous_data`** to skip data fetching and plan generation (only test analysis/reporting)
- Run benchmarks overnight for large configuration sets
- Each run can take 5-30 minutes depending on complexity

### Configuration
- Start with 2-3 configurations to test the setup
- Use descriptive names for easy comparison
- Set temperature to `null` for o1/o3 models (they don't support it)

### Analysis
- Look for consistency across models
- Compare execution times (faster isn't always better)
- Review individual reports for quality differences
- Temperature 0.7 is a good baseline for most scenarios

### Optimization
- Use mini/smaller models first to validate configuration
- Then run full benchmark with production models
- Save benchmark configs in version control for reproducibility

## 🔧 Troubleshooting

### "Benchmark configuration file not found"
- Ensure `benchmark_config.json` exists in the project root
- Check file name spelling

### "No configurations specified"
- Add at least one configuration to the `configurations` array

### "Timeout after 1 hour"
- Analysis is taking too long (complex scenario or slow model)
- Try with `load_previous_plan` and `load_previous_data`
- Reduce scenario complexity

### Individual run failures
- Check `.env` file has all required API keys
- Verify model names are correct
- Review error in comparison report

## 📝 Notes

- The script automatically updates your `.env` file for each configuration
- Your original `.env` settings will be from the last configuration tested
- Each benchmark run is isolated in its own directory
- Safe to run multiple benchmarks on different machines simultaneously

## 🚀 Advanced Usage

### Run from Python Code

```python
import subprocess
subprocess.run(['python', 'run_benchmark.py'])
```

### Automate Multiple Benchmarks

Create multiple config files and run them sequentially:

```bash
#!/bin/bash
for config in benchmark_*.json; do
    cp "$config" benchmark_config.json
    python run_benchmark.py
done
```

### CI/CD Integration

Add to your testing pipeline:

```yaml
- name: Run LLM Benchmarks
  run: |
    cp benchmark_configs/nightly.json benchmark_config.json
    python run_benchmark.py
```

## 📞 Support

For issues or questions:
1. Check the comparison report for detailed error messages
2. Review individual run logs in the benchmark directory
3. Ensure all API keys are properly configured
4. Verify model names match available options

Happy benchmarking! 🎯

