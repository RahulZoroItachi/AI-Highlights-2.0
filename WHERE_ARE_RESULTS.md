# 📁 Where Are My Benchmark Results?

## 🎯 Quick Answer

**Benchmark Summary Report:**
```bash
backend/marketing_funnel_a/benchmark_YYYYMMDD_HHMMSS/benchmark_comparison_*.txt
```

**Individual Model Reports:**
```bash
backend/marketing_funnel_a/marketing_funnel_a_vXXX/marketing_funnel_a_report_*.txt
```

---

## 📊 Complete Results Structure

### 1. Main Benchmark Directory
```
backend/marketing_funnel_a/benchmark_20251018_203000/
├── benchmark_config.json           # Configuration you used
├── results.json                     # Detailed results (all timing, errors, etc.)
└── benchmark_comparison_*.txt       # ⭐ START HERE - Summary of all models
```

**This is your comparison report** showing:
- Which models succeeded/failed
- Timing for each model
- Rankings (fastest to slowest)
- Statistics

---

### 2. Individual Model Results

Each of the 8 models creates its own version folder:

```
backend/marketing_funnel_a/
├── marketing_funnel_a_v023/    ← Model 1: Claude Opus 4.1
│   ├── marketing_funnel_a_plan_*.json
│   ├── marketing_funnel_a_data_*.json
│   ├── marketing_funnel_a_analysis_*.json
│   └── marketing_funnel_a_report_*.txt    ⭐ The actual report
│
├── marketing_funnel_a_v024/    ← Model 2: Claude Sonnet 4
│   ├── marketing_funnel_a_plan_*.json
│   ├── marketing_funnel_a_data_*.json
│   ├── marketing_funnel_a_analysis_*.json
│   └── marketing_funnel_a_report_*.txt
│
├── marketing_funnel_a_v025/    ← Model 3: Claude Sonnet 4.5
├── marketing_funnel_a_v026/    ← Model 4: Claude Haiku 4.5
├── marketing_funnel_a_v027/    ← Model 5: GPT-4o
├── marketing_funnel_a_v028/    ← Model 6: GPT-4o-mini
├── marketing_funnel_a_v029/    ← Model 7: o1-mini
└── marketing_funnel_a_v030/    ← Model 8: Gemini 2.0 Flash
```

---

## 🔍 How to View Results

### View Comparison Report (All Models Summary)
```bash
cat backend/marketing_funnel_a/benchmark_*/benchmark_comparison_*.txt
```

### List All Benchmark Runs
```bash
ls -la backend/marketing_funnel_a/
```

### View Specific Model's Report
```bash
# Claude Opus (v023)
cat backend/marketing_funnel_a/marketing_funnel_a_v023/marketing_funnel_a_report_*.txt

# GPT-4o-mini (v028)
cat backend/marketing_funnel_a/marketing_funnel_a_v028/marketing_funnel_a_report_*.txt
```

### Compare Plans (How Each Model Planned)
```bash
# See Claude Opus's plan
cat backend/marketing_funnel_a/marketing_funnel_a_v023/marketing_funnel_a_plan_*.json

# See GPT-4o's plan
cat backend/marketing_funnel_a/marketing_funnel_a_v027/marketing_funnel_a_plan_*.json
```

### View Detailed JSON Results
```bash
cat backend/marketing_funnel_a/benchmark_*/results.json | python3 -m json.tool
```

---

## 📈 Monitoring Progress

### Check How Many Models Have Completed
```bash
ls backend/marketing_funnel_a/ | grep "_v" | tail -8
```

### Check if Benchmark is Still Running
```bash
ps aux | grep run_benchmark
```

### Watch for New Results (Live)
```bash
watch -n 10 'ls -la backend/marketing_funnel_a/ | tail -10'
```

---

## 🎯 What to Look At First

### 1. Comparison Report (5 min)
```bash
cat backend/marketing_funnel_a/benchmark_*/benchmark_comparison_*.txt
```
This shows you:
- Success rate (8/8 completed?)
- Timing (which was fastest?)
- Rankings

### 2. Individual Reports (Quality Check)
Pick 2-3 models and read their full reports:
```bash
# Read the fastest model's report
cat backend/marketing_funnel_a/marketing_funnel_a_v028/marketing_funnel_a_report_*.txt

# Read the premium model's report
cat backend/marketing_funnel_a/marketing_funnel_a_v023/marketing_funnel_a_report_*.txt
```

### 3. Compare Plans (How They Think)
```bash
# Compare how different models planned:
cat backend/marketing_funnel_a/marketing_funnel_a_v023/marketing_funnel_a_plan_*.json  # Opus
cat backend/marketing_funnel_a/marketing_funnel_a_v028/marketing_funnel_a_plan_*.json  # GPT-4o-mini
```

---

## 💡 Quick Tips

**Finding the Latest Benchmark:**
```bash
ls -lt backend/marketing_funnel_a/benchmark_* | head -1
```

**Counting Completed Runs:**
```bash
ls backend/marketing_funnel_a/ | grep "_v" | wc -l
```

**Opening in Your Editor:**
```bash
# Open comparison report
code backend/marketing_funnel_a/benchmark_*/benchmark_comparison_*.txt

# Or with nano
nano backend/marketing_funnel_a/benchmark_*/benchmark_comparison_*.txt
```

---

## 📞 Need Help?

**Can't find results?**
- Check if benchmark is still running: `ps aux | grep run_benchmark`
- Look for error messages: `cat nohup.out`
- Verify scenario name: `cat benchmark_config.json | grep scenario`

**Results look incomplete?**
- Benchmark might still be running (takes 80-200 minutes)
- Check progress: `ls backend/marketing_funnel_a/ | grep "_v" | tail -5`

---

**Current benchmark will create versions v023 through v030 (8 models)**

Check back in ~2 hours for complete results! 🚀


