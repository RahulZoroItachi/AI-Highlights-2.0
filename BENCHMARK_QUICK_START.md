# 🚀 Benchmark Quick Start Guide

## 1️⃣ **Setup** (One-time)

```bash
# Make sure you're in the project root
cd /path/to/AIH_V1

# Verify scripts are executable
chmod +x run_benchmark.py compare_reports.py
```

## 2️⃣ **Choose or Create Config**

### Option A: Use Example Config
```bash
# Copy an example to the root
cp benchmark_examples/quick_test.json benchmark_config.json

# Edit if needed
nano benchmark_config.json
```

### Option B: Use Provided Config
The default `benchmark_config.json` is already configured with 9 different configurations.

### Option C: Create Your Own
See `BENCHMARK_README.md` for full configuration options.

## 3️⃣ **Run Benchmark**

```bash
python run_benchmark.py
```

**What happens:**
1. Shows configuration summary
2. Asks for confirmation
3. Runs each configuration sequentially
4. Saves all results
5. Generates comparison report

**Time estimate:** 5-30 minutes per configuration

## 4️⃣ **View Results**

### Comparison Report
```bash
# Find your benchmark directory
ls backend/{scenario}/benchmark_*

# View the comparison report
cat backend/{scenario}/benchmark_{timestamp}/benchmark_comparison_*.txt
```

### Individual Reports
```bash
# Each run creates a version folder
ls backend/{scenario}/{scenario}_v*

# View a specific report
cat backend/{scenario}/{scenario}_v001/{scenario}_report_*.txt
```

### JSON Results
```bash
# Detailed results with all metadata
cat backend/{scenario}/benchmark_{timestamp}/results.json
```

## 5️⃣ **Compare Reports** (Optional)

```bash
# Compare specific reports
python compare_reports.py \
  backend/scenario1/scenario1_v001/scenario1_report_*.txt \
  backend/scenario1/scenario1_v002/scenario1_report_*.txt
```

## 📋 **Quick Config Reference**

### Minimal Config
```json
{
  "scenario": "your_scenario",
  "configurations": [
    {
      "name": "Test 1",
      "llm_provider": "claude",
      "claude_model": "claude-sonnet-4-20250514",
      "temperature": 0.7
    }
  ]
}
```

### Speed Up Testing
```json
{
  "scenario": "your_scenario",
  "load_previous_plan": 1,    // Skip plan generation
  "load_previous_data": 1,    // Skip data fetching
  "configurations": [...]
}
```

### Temperature Range
```json
{
  "configurations": [
    {"name": "Precise", "temperature": 0.3},
    {"name": "Balanced", "temperature": 0.5},
    {"name": "Standard", "temperature": 0.7},
    {"name": "Creative", "temperature": 0.9}
  ]
}
```

## 🎯 **Common Use Cases**

### Test 1: Quick Validation (2 configs, ~10-20 min)
```bash
cp benchmark_examples/quick_test.json benchmark_config.json
python run_benchmark.py
```

### Test 2: Temperature Sweep (5 configs, ~25-150 min)
```bash
cp benchmark_examples/temperature_test.json benchmark_config.json
python run_benchmark.py
```

### Test 3: Model Comparison (6 configs, ~30-180 min)
```bash
cp benchmark_examples/model_comparison.json benchmark_config.json
python run_benchmark.py
```

### Test 4: Full Suite (9 configs, ~45-270 min)
```bash
# Use default benchmark_config.json
python run_benchmark.py
```

## 💡 **Pro Tips**

1. **Start Small**: Test with 2-3 configs first
2. **Use Previous Data**: Set `load_previous_plan: 1` and `load_previous_data: 1` to skip data fetching
3. **Run Overnight**: Large benchmarks can take hours
4. **Name Clearly**: Use descriptive names in configs for easy comparison
5. **Version Control**: Save your benchmark configs for reproducibility

## 🔍 **What to Look For in Results**

1. **Success Rate**: How many configs completed successfully?
2. **Timing**: Which model/config is fastest?
3. **Consistency**: Do similar configs produce similar results?
4. **Quality**: Review actual reports for insight quality
5. **Cost**: Faster/smaller models = lower API costs

## ⚠️ **Troubleshooting**

### "Benchmark configuration file not found"
```bash
# Check you're in project root
pwd

# Verify file exists
ls benchmark_config.json
```

### "Timeout after 1 hour"
- Use `load_previous_plan` and `load_previous_data`
- Simplify your scenario
- Try faster models first

### Configuration fails
- Check API keys in `.env`
- Verify model names are correct
- Review error in results.json

## 📞 **Need Help?**

See `BENCHMARK_README.md` for:
- Full configuration documentation
- All available models
- Advanced use cases
- Detailed examples

---

**Ready to start? Run:**
```bash
python run_benchmark.py
```

