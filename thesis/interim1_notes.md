# Notes for the first interim report (due 13 Oct 2026)

These are notes and evidence for writing the report, **not report text**. The report has to be written in your own words. Every reference below was checked to exist (title, authors, venue) on 2026-10-06; the link goes to the ACL Anthology, arXiv or the publisher. Numbers come from our own logs (`progress.md`, `results/`).

---

## Task 1: Why MLADI is the test set, not a held-out part of the LahjatBERT data

### The argument in one line
A held-out part of the LahjatBERT data would tell us how well a model copies GPT-4o's labelling. MLADI tells us how well it matches what native speakers say. Only the second is the question the thesis asks.

### Points, each with evidence

1. **Human labels vs automatic labels.**
   - MLADI's test set was annotated by native speakers from 11 Arab countries, who judged for each sentence whether it is valid in their dialect.
   - The LahjatBERT labels were produced automatically, by GPT-4o plus binary classifiers, aggregated using ALDi.
   - Our own rule (CLAUDE.md): human labels are the evaluation reference; automatic labels are for training only.
   - Refs: NADI 2024 [1], Keleg et al. 2025 [2], LahjatBERT [3].

2. **Our runs measure the gap directly.**
   - R03-marbert: the same model scores **~81 macro F1 on a held-out 10% of the LahjatBERT data**, but **71.34 ± 1.03 on the human-labelled MLADI dev set**.
   - So a held-out split would overstate quality by about 10 points, because it rewards agreeing with the automatic labeller, errors included.

3. **The automatic labels are visibly noisy** (our statistics, `results/data_stats/nadi_lahjatbert_stats.json`):
   - **Contradicts geolocation:** for 20% of tweets, the country the tweet was posted from is *not* among its "valid" dialects.
   - **Zero-label texts:** 2,271 texts are labelled valid in *no* dialect. Most are clearly dialectal: 69% have ALDi ≥ 0.5.
   - **Inconsistent duplicates:** 21 texts that occur twice received different labels.

   Evaluating on such labels would reward a model for copying these errors.

4. **Single-label geolocation data is the wrong reference for this task.**
   - NADI's original labels are one country per tweet, based on the user's location.
   - Keleg & Magdy (2023) [4] show that many sentences are valid in several dialects, so single-label evaluation counts correct predictions as errors.
   - In our data, 66 identical texts were tweeted from different countries.

5. **Independence and leakage.**
   - A random held-out split shares sources, time period, users and topics with the training data, so it overestimates generalization.
   - MLADI's test sentences were collected and annotated separately, and our check found **0 exact overlaps** between the dev set and the training texts.

6. **Specific to this thesis: circularity.**
   - The training labels come from an LLM (GPT-4o), and the augmentation also uses LLMs.
   - Testing on LLM-labelled data would favour LLM-like text and labels, which is exactly the bias the thesis wants to measure.
   - A human-labelled test set avoids grading LLM data with an LLM's answer key.

7. **Comparability.** MLADI has a public leaderboard where published systems are ranked with the same metric (macro F1) and settings: LahjatBERT, and NADI 2024 teams such as Elyadata, NLP_DI and dzNlp. Our results can be placed next to theirs.

### Limitations to state honestly
- **Private labels.** Only the 120-sentence dev set (8 dialects) is available locally. The test set (1,000 sentences, 11 dialects) can only be scored through public leaderboard submissions, so the number of test evaluations must stay small.
- **11 of 18 dialects.** Gulf dialects other than Saudi (Bahrain, Kuwait, Oman, Qatar, UAE), Lebanon and Libya are not scored.
- **The dev set is small.** 1–2 point differences on it are within seed noise (our spread is ±1.03).

---

## Task 2: Catalogue of data-augmentation techniques

Organized as in Feng et al.'s survey [5]. For each: what it does, and what it means for **dialect** identification, where the label depends on dialect-specific words and spelling.

| Family | Technique | What it does | Fit for dialect ID |
|---|---|---|---|
| Rule-based edits | EDA [6]: synonym replacement, random insertion, swap, deletion | Small random word edits | **Risky.** Replacing a dialect marker (e.g. Egyptian ده) with a synonym from another variety changes the true label. Random swaps and deletions are safer but add little dialect signal. |
| Model-based word substitution | Contextual augmentation [7] | A language model proposes replacement words that fit the context | Same risk: a masked LM trained on mostly MSA will tend to propose MSA words. |
| Paraphrase via translation | Back-translation [8] | Translate to another language and back | Back-translating through English or MSA tends to wash out the dialect. NLLB-200 has codes for several dialects (check the list in its model card), which allows dialect↔MSA or dialect↔dialect variants. |
| Translation + human post-editing | AraDiCE [9] | MT into dialects, then human correction | Strong for quality, but needs human effort; a reference point for faithful dialect data. |
| Semi-supervised / pseudo-labelling | Self-training on unlabelled tweets (NADI 2020 ArabicProcessors team [10]); LahjatBERT's pseudo-labelling [3] | Label unlabelled real text with a model, then add it to training | Real text, so natural dialect, but labels inherit the labeller's errors. |
| Fine-tuned LM generation | LAMBADA [11] | Fine-tune a generator on the labelled data, generate per class, filter with a classifier | The template for "generate, then filter". Needs fine-tuning, which is heavy for 7–9B models on 8 GB. |
| LLM rephrasing | AugGPT [12] | An LLM rewrites each training sentence into several variants | Keeps the topic; the dialect must be kept explicitly in the instruction. |
| Zero/few-shot dataset generation | ZeroGen [13] | Prompt a large model to write labelled examples from scratch | This is our **"open generation"** condition. |
| Diversity-controlled generation | Chung et al. [14]: logit suppression, temperature; human label replacement and filtering | Push generation away from repeated outputs | Shows the diversity–accuracy trade-off our thesis measures: more diverse output had more wrong labels. |
| Faithfulness-controlled generation | Veselovsky et al. [15]: grounding on real examples, filtering, taxonomy-based generation | Make synthetic data resemble the real distribution | Closest to our **"controlled generation"** condition. Grounding worked best in their sarcasm case study. |
| Overview of the LLM era | Long et al. survey [16] | Workflow: generation → curation (filtering) → evaluation | A useful frame for the report's structure. |

Related findings worth citing:
- **Li et al. 2023 [17]:** LLM-generated training data helps less as the task gets more subjective. Dialect validity is partly subjective (annotators disagree), so this predicts limited gains and motivates the quality controls.

---

## Task 3: Quality measures for augmented data

Grouped by the question each answers. "Ours" marks what we plan to compute (most models are already chosen: E5, CAMeLBERT DID, ALDi).

| Question | Measure | Reference | Ours |
|---|---|---|---|
| **Is it repeated?** | Exact duplicates; near-duplicates (shingle/MinHash Jaccard similarity) | Lee et al. 2022 [18] (dedup in LM training) | yes |
| | Overlap with the real training data and with the dev set (leakage) | — | yes |
| **Is the wording varied?** | Type–token ratio; distinct-n (share of unique n-grams) | Li et al. 2016 [19] | yes |
| | MTLD (length-robust lexical diversity) | McCarthy & Jarvis 2010 [20] | yes |
| | Self-BLEU (how similar each sentence is to the rest; lower = more diverse) | Zhu et al. 2018 (Texygen) [21] | yes |
| **Is the meaning varied?** | Mean pairwise cosine distance of sentence embeddings (E5) | — | yes |
| | Vendi score (effective number of distinct examples) | Friedman & Dieng 2023 [22] | yes |
| **Does it look like real data?** | MAUVE (distribution gap between generated and human text) | Pillutla et al. 2021 [23] | optional |
| **Is the label right? (dialect fidelity)** | Agreement with a dialect-ID classifier (CAMeLBERT DID [24]) | — | yes |
| | Dialectness score (ALDi): did the generator write dialect or slide into MSA? | Keleg et al. 2023 [25] | yes |
| | Agreement between two labellers (model–model or model–human): Cohen's kappa | Cohen 1960 [26] | yes |
| **Did it follow the controls?** | Per control factor: requested vs measured length, script (Arabic/Arabizi share), code-switching rate, topic | — | yes (controlled condition only) |
| **Does it help?** | Train on real + synthetic, test on real (MLADI); learning curves over real-data size | (our experimental design) | yes |
| | Data maps: training dynamics flag ambiguous and probably mislabelled examples | Swayamdipta et al. 2020 [27] | optional |

Point for the report: measures from the first five rows can be computed **before** training and compared with the final row (whether the data helps). That comparison is what answers the supervisor's "more data vs better data" question.

---

## Progress so far (for the "work done" section)

- **Data:** NADI 2020/2021/2023 tweets joined with LahjatBERT's multi-label annotations: 58,384 unique texts, 18 dialects.
  - Found and fixed three problems in the published data and code: IDs assigned by text lookup, double-escaped quotes, and link masking that never matches.
- **Evaluation:** the leaderboard's exact settings reproduced locally; the metric code matches the official scorer exactly.
- **Baseline (condition 1, real only):** MARBERT, 3 seeds, **71.34 ± 1.03** dev macro F1.
  - That is above LahjatBERT's published baseline (67.41) and level with their best published model (72.68).
  - It uses the same recipe with a dropout bug fixed and macro-F1 checkpoint selection. R04-marbert is testing which change explains the gain.
- **Models chosen:** 3 generators + NLLB, 3 scorers, 3 classifiers (`progress.md`).
- **Next:** generation (open and controlled), filtering and quality measures; baselines with MARBERTv2 and AraBERT-Twitter.

---

## References (all checked to exist)

1. Abdul-Mageed, Keleg, Elmadany, Zhang, Hamed, Magdy, Bouamor, Habash. *NADI 2024: The Fifth Nuanced Arabic Dialect Identification Shared Task.* ArabicNLP 2024. https://aclanthology.org/2024.arabicnlp-1.79
2. Keleg, Goldwater, Magdy. *Revisiting Common Assumptions about Arabic Dialects in NLP.* ACL 2025. https://arxiv.org/abs/2505.21816
3. Mekky, El Zeftawy, Hassan, Keleg, Nakov. *Curriculum Learning and Pseudo-Labeling Improve the Generalization of Multi-Label Arabic Dialect Identification Models.* arXiv 2602.12937 (2026). https://arxiv.org/abs/2602.12937
4. Keleg, Magdy. *Arabic Dialect Identification under Scrutiny: Limitations of Single-label Classification.* ArabicNLP 2023. https://aclanthology.org/2023.arabicnlp-1.31
5. Feng, Gangal, Wei, Chandar, Vosoughi, Mitamura, Hovy. *A Survey of Data Augmentation Approaches for NLP.* Findings of ACL 2021. https://aclanthology.org/2021.findings-acl.84
6. Wei, Zou. *EDA: Easy Data Augmentation Techniques for Boosting Performance on Text Classification Tasks.* EMNLP-IJCNLP 2019. https://aclanthology.org/D19-1670
7. Kobayashi. *Contextual Augmentation: Data Augmentation by Words with Paradigmatic Relations.* NAACL 2018. https://aclanthology.org/N18-2072
8. Sennrich, Haddow, Birch. *Improving Neural Machine Translation Models with Monolingual Data.* ACL 2016. https://aclanthology.org/P16-1009
9. *AraDiCE: Benchmarks for Dialectal and Cultural Capabilities in LLMs.* COLING 2025. https://aclanthology.org/2025.coling-main.283 (TODO: copy the author list from the Anthology page)
10. *Arabic dialect identification: An Arabic-BERT model with data augmentation and ensembling strategy.* WANLP 2020 (NADI 2020 system paper). https://aclanthology.org/2020.wanlp-1.28 (TODO: copy authors from the Anthology page)
11. Anaby-Tavor, Carmeli, Goldbraich, Kantor, Kour, Shlomov, Tepper, Zwerdling. *Do Not Have Enough Data? Deep Learning to the Rescue!* AAAI 2020. https://doi.org/10.1609/aaai.v34i05.6233
12. Dai et al. *AugGPT: Leveraging ChatGPT for Text Data Augmentation.* arXiv 2302.13007 (2023); published in IEEE Transactions on Big Data. https://arxiv.org/abs/2302.13007
13. Ye et al. *ZeroGen: Efficient Zero-shot Learning via Dataset Generation.* EMNLP 2022. https://aclanthology.org/2022.emnlp-main.801
14. Chung, Kamar, Amershi. *Increasing Diversity While Maintaining Accuracy: Text Data Generation with Large Language Models and Human Interventions.* ACL 2023. https://aclanthology.org/2023.acl-long.34
15. Veselovsky, Horta Ribeiro, Arora, Josifoski, Anderson, West. *Generating Faithful Synthetic Data with Large Language Models: A Case Study in Computational Social Science.* arXiv 2305.15041 (2023). https://arxiv.org/abs/2305.15041
16. Long, Wang, Xiao, Zhao, Ding, Chen, Wang. *On LLMs-Driven Synthetic Data Generation, Curation, and Evaluation: A Survey.* Findings of ACL 2024. https://arxiv.org/abs/2406.15126
17. Li, Zhu, Lu, Yin. *Synthetic Data Generation with Large Language Models for Text Classification: Potential and Limitations.* EMNLP 2023. https://aclanthology.org/2023.emnlp-main.647
18. Lee et al. *Deduplicating Training Data Makes Language Models Better.* ACL 2022. (TODO: confirm the Anthology link before citing)
19. Li, Galley, Brockett, Gao, Dolan. *A Diversity-Promoting Objective Function for Neural Conversation Models.* NAACL 2016. https://aclanthology.org/N16-1014
20. McCarthy, Jarvis. *MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment.* Behavior Research Methods 42(2):381–392, 2010. https://doi.org/10.3758/BRM.42.2.381
21. Zhu, Lu, Zheng, Guo, Zhang, Wang, Yu. *Texygen: A Benchmarking Platform for Text Generation Models.* SIGIR 2018, pp. 1097–1100. https://arxiv.org/abs/1802.01886
22. Friedman, Dieng. *The Vendi Score: A Diversity Evaluation Metric for Machine Learning.* TMLR 2023. https://arxiv.org/abs/2210.02410
23. Pillutla, Swayamdipta, Zellers, Thickstun, Welleck, Choi, Harchaoui. *MAUVE: Measuring the Gap Between Neural Text and Human Text using Divergence Frontiers.* NeurIPS 2021. https://arxiv.org/abs/2102.01454
24. Inoue, Alhafni, Baimukan, Bouamor, Habash. *The Interplay of Variant, Size, and Task Type in Arabic Pre-trained Language Models.* WANLP 2021 (CAMeLBERT). (TODO: confirm the Anthology link before citing)
25. Keleg, Goldwater, Magdy. *ALDi: Quantifying the Arabic Level of Dialectness of Text.* EMNLP 2023, pp. 10597–10611. https://aclanthology.org/2023.emnlp-main.655
26. Cohen. *A Coefficient of Agreement for Nominal Scales.* Educational and Psychological Measurement 20(1), 1960.
27. Swayamdipta, Schwartz, Lourie, Wang, Hajishirzi, Smith, Choi. *Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics.* EMNLP 2020. https://aclanthology.org/2020.emnlp-main.746
