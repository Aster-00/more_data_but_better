# scripts/

Entry points that are not part of the `src/` pipeline modules. Run everything from the repo root.

| Folder | Script | What it does |
|---|---|---|
| `topics/` | `build_topic_pool.py` | Builds the universal topic pool (`data/topics/pool/universal_v1.jsonl`, D-018) |
| | `fit_topics.py` | Fits a frozen E5 k-means topic list from a `configs/quality/topics_*.json` config |
| | `analyze_topic_clusters.py` | Cluster-level analysis of a topic list (`results/quality/topics/<name>/analysis.json`, `layout.json`) |
| | `plot_topic_clusters.py` | Interactive HTML view of that analysis (`clusters.html`); the same figures are in `notebooks/topic_clusters.ipynb` |
| | `sample_reassignments.py` | Sample texts of unnamed clusters moved to their nearest named topic |
| `quality/` | `measure_dataset_quality.py` | Descriptive quality statistics of the real datasets (`python -m scripts.quality.measure_dataset_quality`) |
| `generation/` | `check_generators.py` | G01 generator feasibility check (4-bit load, VRAM, sample sentences) |
| | `g01_to_records.py` | Converts the G01 outputs to synthetic records |
| `hub/` | `download_models.py` | Downloads roster models to the model cache |
| | `upload_to_hub.py` | Uploads a trained BERT classifier for the MLADI leaderboard (`python -m scripts.hub.upload_to_hub`) |
| | `upload_adapter_to_hub.py` | Uploads a QLoRA adapter (`python -m scripts.hub.upload_adapter_to_hub`) |
| `queues/dialect/` | `queue_*.sh` | Restartable overnight queues of the dialect track |
| `queues/sentiment/` | `queue_*.sh` | Restartable queues of the sentiment track (SR01–SR04, SG01–SG02) |
| `system/` | `pc_crashdump_to_F.ps1` | Moves Windows crash dumps to `F:\CrashDumps` (D-009) |

Scripts that import from `src/` add the repo root to `sys.path` (`Path(__file__).resolve().parents[2]`), so a script moved to another depth needs that index changed.
