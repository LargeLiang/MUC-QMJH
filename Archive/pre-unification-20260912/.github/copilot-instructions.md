# Copilot Instructions

## Project Overview

This is a Python data analysis research project studying **human preference biases in LLM outputs** (length and format preferences), using the LMArena `arena-human-preference-140k` dataset (~136k annotated records, 53 models). The project is affiliated with Minzu University of China (中央民族大学, MUC), funded under the "Qingmiao" undergraduate innovation program.

**Research goal**: Quantify and model length/format biases in RLHF preference data, control for confounders, and investigate causal mechanisms via SEM.

---

## Architecture

Scripts are numbered C01–C22 and follow a **four-layer pipeline**. Each script is standalone and run directly with `python Codes/CXX_name.py` from the project root.

```
Layer 1 — Ingestion     C01–C02   Validate raw shards, merge 7 parquet shards → integrated_data.parquet
Layer 2 — Exploration   C03–C11   Per-field analysis (touch_* scripts), each writes a Reports/RXX_*.txt
Layer 3 — Cleaning      C12       Filter + flatten + reduce → optimized_data.parquet (108k × 32 cols)
Layer 4 — Analysis      C13–C22   Subset division, visualization, statistical tests, robustness, SEM
```

**Data flow**:
```
Data/lmarena-aiarena-human-preference-140k/Data/train-0000X-of-00007.parquet  (7 shards)
  → C02 → Data/integrated_data/integrated_data.parquet          (135,634 × 14)
  → C12 → Data/optimized_data/optimized_data.parquet            (108k × 32)
  → C13 → Data/optimized_data/*_data.parquet                    (20 subsets)
  → C14–C22 → Tables/TXX_*.csv, Pictures/PXX_*.png, Reports/RXX_*.txt
```

**Key filtering rule (C12)**: Only rows where `evaluation_order == 1` are kept. Rows with `order > 1` have `sum_user_tokens` reflecting the full session history, not the current order — this contaminates length features.

**Four category boolean columns** in optimized data: `creative_writing_bool`, `if_bool`, `math_bool`, `code_bool` — used to partition the 20 subsets in C13.

---

## Code Conventions

### Path management
Every script exposes path factory functions with an optional `root` parameter for portability:

```python
def get_optimized_parquet_path(root: Path | str | None = None) -> Path:
    if root is None:
        root = Path.cwd()
    return Path(root) / "Data" / "optimized_data" / "optimized_data.parquet"
```

Always use `pathlib.Path`; never use `os.path` string concatenation. All output directories are created with `dir.mkdir(parents=True, exist_ok=True)` before writing.

### Function signatures
All main analysis functions accept optional `file_path`, `data_dir`, and `report_dir` parameters (all `Path | str | None = None`), normalized at the top of the function body. This makes scripts testable with custom paths.

### Type hints
Use full type annotations throughout. Use `Path | str | None` (Python 3.10+ union syntax), `Dict`, `Tuple`, `Counter` from `typing`, and inline variable annotations where clarifying.

### Output / logging
Use `"=" * 80` separators between major phases and `"-" * 80` between sub-steps. Include progress counters (`n/total`). End every script with `"任务完成！"` wrapped in `"=" * 80`.

### Stats collection pattern
Accumulate statistics in a dict with a `Counter` for categorical breakdowns, then pass the dict to a dedicated `generate_*_report()` function at the end:

```python
stats = {"total_rows": len(df), "filtered_rows": 0, "filter_reasons": Counter(), ...}
# ... accumulate in loop ...
generate_optimization_report(..., stats=stats, ...)
```

### Docstrings
Docstrings are written in **Chinese**. Format:
```
一句话描述。

详细说明（可选）。

参数说明：
- param_name：说明（默认值说明）

返回值：...
异常处理：...
```

### Comments
Inline comments explain *why*, not *what*. Prefer block comments over end-of-line comments for multi-line reasoning.

---

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Scripts | `CXX_snake_case.py` | `C12_optimize_data.py` |
| Reports | `RXX_snake_case_report.txt` | `R09_optimization_report.txt` |
| Tables | `TXX_snake_case_stats.csv` | `T01_length_ratio_analysis_stats.csv` |
| Pictures | `PXX_snake_case_chart.png` | `P04_length_ratio_line_chart.png` |
| Path functions | `get_*_path()` | `get_optimized_parquet_path()` |
| Analysis functions | `touch_*()`, `optimize_*()`, `divide_*()` | `touch_model()` |
| Subset creators | `create_*_subsets()` | `create_pure_subsets()` |
| Report generators | `generate_*_report()` | `generate_optimization_report()` |

---

## Key Data Schema

**optimized_data.parquet** (108k × 32 columns):
- Identifiers: `id`, `model_a`, `model_b`, `winner`
- Length: `a_tokens`, `b_tokens`
- Format: `a_header_counts`, `a_list_counts`, `a_bold_counts` (and `b_*` counterparts)
- Conversation (flattened): `turn_X_a_text`, `turn_X_b_text`
- Category booleans: `creative_writing_bool`, `if_bool`, `math_bool`, `code_bool`
- Quality dimensions: 7 standard evaluation criteria extracted from `category_tag`

**Session hierarchy**: Session → Order → Turn. One row = one Order. `evaluation_order == 1` means first evaluation within a session.

---

## matplotlib / Chinese font
All visualization scripts set:
```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-darkgrid')
```
Include this block at the top of any new visualization script.
