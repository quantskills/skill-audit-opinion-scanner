# Audit Opinion Scanner — Multi-dimensional Financial Analysis System

Covering audit opinion scanning, 25 financial statement items, 15 derived ratios, industry classification benchmarking, 5-dimension rapid scoring, 8-section deep analysis, and composite risk detection. From risk screening to valuation to AI interpretation — a single pipeline.

## ⚠️ Disclaimer

- **Research & Educational Use Only**: This skill is a quantitative financial analysis research tool and does NOT constitute investment advice, financial advice, or trading recommendations of any kind.
- **Data Accuracy**: Financial data is sourced from panda_data and may contain errors, omissions, or delays. Always verify against official filings (annual reports, CSRC announcements) before making decisions.
- **No Guaranteed Outcomes**: Financial analysis scores and risk ratings are quantitative heuristics, not predictions. A high score does not guarantee future performance; a red flag does not guarantee losses.
- **Audit Opinion Lag**: Audit opinions reflect historical financial conditions and may not capture emerging risks. Non-standard opinions are trailing indicators, not leading ones.

## Directory Structure

```
├── SKILL.md                                ← Skill specification (v2.0)
├── README.md                               ← Chinese README
├── README.en.md                            ← This file
├── LICENSE                                 ← GPL-3.0
├── INSTALL.md                              ← Multi-platform install guide
├── requirements.txt                        ← pandas >= 2.0, pytest >= 7.0
├── data/                                   ← Local cache (parquet)
│   ├── fina_cache.parquet                  ← 300 stocks × 8 qtrs × (25 items + 15 ratios)
│   └── fina_industry.parquet               ← 5,514 stocks × 31 Shenwan L1 industries
├── scripts/
│   ├── scan.py                             ← Step 1: Audit opinion scanner
│   ├── build_cache.py                      ← Step 2: Local cache builder
│   ├── analyze_quick.py                    ← Step 3: 5-dim batch scoring (300 stocks)
│   ├── analyze_stock.py                    ← Step 4: Single-stock 8-section deep report
│   ├── data.py / universe.py / rules.py / report.py
├── output/                                 ← Generated CSV reports
├── references/
│   └── need_used_api.md                    ← 5 panda_data API contracts
└── tests/                                  ← 95 unit tests
```

## Quick Start

```bash
# 1. Build local cache (requires panda_data credentials, one-time, ~5 seconds)
python scripts/build_cache.py --universe 000300.SH --quarters 8

# 2. Audit opinion scan
python scripts/scan.py --quarter 2025q4

# 3. Batch financial health scoring (300 stocks, pure local, <1s)
python scripts/analyze_quick.py --all

# 4. Single-stock deep analysis
python scripts/analyze_stock.py 600519.SH

# 5. Run tests
pytest tests/ -v
```

## Core Design

1. **5-Step Pipeline**: Audit scan → Local cache → Batch scoring → Deep analysis → AI interpretation. Steps 3-5 are pure local reads with zero API calls.

2. **Two-Tier Caching**: 25 curated fields from 320+ general-ledger columns, selected for maximum analytical value with minimal redundancy. 15 derived ratios computed on load (ROE, DuPont decomposition, cash flow quality).

3. **Industry-Normalized Scoring**: Every metric is compared against same-industry peers using MAD-based z-scores. A 90th-percentile ROE in pharmaceuticals ≠ 90th-percentile in banking.

4. **8-Section Deep Report**: Core financials → Profitability decomposition → DuPont → Balance sheet health → Cash flow quality → Growth trajectory → Industry percentiles → Composite risk detection (12 automated checks).

5. **Agent-Ready Data Products**: CSV and Parquet outputs with stable schemas. Other agents consume data via `pd.read_csv()` or `pd.read_parquet()` without running scripts.

## Supported Runtimes

| Platform | Install Guide |
|---|---|
| Claude Code | `INSTALL.md` § Claude Code |
| Any Python 3.10+ runtime | `INSTALL.md` § Standalone |
| Agent consumption | `INSTALL.md` § Data Products |

## Data Coverage

| Dimension | Scope |
|---|---|
| Stocks | 300 (CSI300), expandable to CSI500/CSI1000 |
| Quarters | 8 trailing (e.g., 2024q3–2026q2) |
| Financial Fields | 25 curated (income stmt, balance sheet, cash flow) |
| Derived Ratios | 15 (ROE, ROA, margins, leverage, turnover, cash flow quality) |
| Industries | 31 Shenwan L1, 5,514 stocks classified |
| Audit Opinion Types | 10 (from unqualified to disclaimer of opinion) |

## Limitations

| Limitation | Detail |
|---|---|
| CSI300 only (default) | Expand via `--universe 000852.SH` for CSI1000 |
| Reports cache needs manual CSI1000 build | `--universe 000852.SH --reports-only` |
| No LLM API integration | AI interpretation via current conversation context |
| get_fina_performance end_quarter filtering unreliable | Switched to get_fina_reports for cache building |
| No PDF/annual report text analysis | v2 planned |
| Real-time data not supported | Point-in-time analysis only |
