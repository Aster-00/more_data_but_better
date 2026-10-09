# More Data But Better: controllable synthetic data for Arabic dialect identification

Bachelor thesis code (GIU, Winter 2026). Project brief, rules and model roster: [CLAUDE.md](CLAUDE.md).

## Where things are documented

| File | What |
|---|---|
| [docs/progress.md](docs/progress.md) | Run notes: what each run did, what changed, what it showed |
| [docs/decisions.md](docs/decisions.md) | Decisions log (D-NNN) |
| [docs/data.md](docs/data.md) | Data sources and versions (D1–D4) |
| [docs/tables/split_summary.md](docs/tables/split_summary.md) | Classifier scores per run: validation, dev, test, per dialect; leaderboard submissions |
| [docs/tables/quality_summary.md](docs/tables/quality_summary.md) | Quality measurements of data sets (Q) |
| [docs/tables/scorer_summary.md](docs/tables/scorer_summary.md) | Scorer validation against human gold (S) |
| [docs/tables/generator_summary.md](docs/tables/generator_summary.md) | Generator feasibility checks (G) |
| [thesis/](thesis/) | Report notes |

Tables in `docs/tables/` are generated from `results/` and never edited by hand:

```
python -m src.evaluation.summarize_runs      # split_summary
python -m src.quality.summarize_quality      # quality, scorer and generator summaries
```

Run IDs and result folders are registered in [configs/runs.json](configs/runs.json).
