
## SG01 0 shot Prompt Generation

Each cell: requested → kept after filter → selected (target 500 per cell).

**Jais-2-8B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 1,300 → 38 → 38 | 1,300 → 8 → 8 | 1,300 → 186 → 186 | 232 |
| egypt | 1,300 → 247 → 247 | 1,300 → 122 → 122 | 1,300 → 514 → 500 | 869 |
| gulf | 1,300 → 482 → 482 | 1,300 → 252 → 252 | 1,300 → 361 → 361 | 1,095 |
| levant | 1,300 → 469 → 469 | 1,300 → 237 → 237 | 1,300 → 516 → 500 | 1,206 |
| **Total** | 5,200 → 1,236 → 1,236 | 5,200 → 619 → 619 | 5,200 → 1,577 → 1,547 | 3,402 |

**Fanar-1-9B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 650 → 646 → 500 | 650 → 644 → 500 | 650 → 649 → 500 | 1,500 |
| egypt | 650 → 646 → 500 | 650 → 647 → 500 | 650 → 648 → 500 | 1,500 |
| gulf | 650 → 646 → 500 | 650 → 647 → 500 | 650 → 649 → 500 | 1,500 |
| levant | 650 → 645 → 500 | 650 → 647 → 500 | 650 → 646 → 500 | 1,500 |
| **Total** | 2,600 → 2,583 → 2,000 | 2,600 → 2,585 → 2,000 | 2,600 → 2,592 → 2,000 | 6,000 |

**Qwen3-8B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 650 → 648 → 500 | 650 → 645 → 500 | 650 → 648 → 500 | 1,500 |
| egypt | 650 → 643 → 500 | 650 → 650 → 500 | 650 → 635 → 500 | 1,500 |
| gulf | 650 → 648 → 500 | 650 → 650 → 500 | 650 → 646 → 500 | 1,500 |
| levant | 650 → 648 → 500 | 650 → 649 → 500 | 650 → 642 → 500 | 1,500 |
| **Total** | 2,600 → 2,587 → 2,000 | 2,600 → 2,594 → 2,000 | 2,600 → 2,571 → 2,000 | 6,000 |

**Aya-Expanse-8B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 650 → 559 → 500 | 650 → 613 → 500 | 650 → 572 → 500 | 1,500 |
| egypt | 650 → 640 → 500 | 650 → 644 → 500 | 650 → 641 → 500 | 1,500 |
| gulf | 650 → 647 → 500 | 650 → 628 → 500 | 650 → 624 → 500 | 1,500 |
| levant | 650 → 641 → 500 | 650 → 648 → 500 | 650 → 642 → 500 | 1,500 |
| **Total** | 2,600 → 2,487 → 2,000 | 2,600 → 2,533 → 2,000 | 2,600 → 2,479 → 2,000 | 6,000 |

SG01 Jais-2, Fanar, Qwen3, Aya.

| Generator | Requested | Distinct texts | Kept after filter | Exact dup. | Near dup. | Script | Length | Unparsed | Selected | Short cells | Test matches | Translations cut | Texts/s | Mean words (selected) | Imbalance (max : min) | MSA share | Dialectness | Lexical diversity | Topic spread (of 30) | Semantic diversity (Vendi) | Repeats | Fidelity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jais-2-8B | 15,600 | 4,398 (28.2%) | 3,432 (22.0%) | 11,168 | 950 | 14 | 1 | 35 | 3,402 | 10 of 12 | 0 | 264 | 4.07 | 12.4 | 62.5 : 1 | 9.6% | 0.69 | 339 | 9 | 2.8 | 77.7% | 98.0% |
| Fanar-1-9B | 7,800 | 7,794 (99.9%) | 7,760 (99.5%) | 6 | 1 | 26 | 7 | 0 | 6,000 | 0 of 12 | 0 | 116 | 1.28 | 13.8 | 1.0 : 1 | 25.0% | 0.48 | 1123 | 11 | 3.1 | 0.1% | 94.9% |
| Qwen3-8B | 7,800 | 7,772 (99.6%) | 7,752 (99.4%) | 28 | 5 | 6 | 9 | 0 | 6,000 | 0 of 12 | 0 | 2 | 1.93 | 13.9 | 1.0 : 1 | 22.1% | 0.56 | 323 | 8 | 3.2 | 0.4% | 88.7% |
| Aya-Expanse-8B | 7,800 | 7,714 (98.9%) | 7,499 (96.1%) | 86 | 213 | 1 | 1 | 0 | 6,000 | 0 of 12 | 0 | 4 | 2.20 | 17.4 | 1.0 : 1 | 20.4% | 0.57 | 499 | 7 | 2.8 | 3.8% | 91.2% |
| S1 real (reference) | — | — | — | — | — | — | — | — | — | — | — | — | — | — | 37.7 : 1 | 22.4% | 0.54 | 2518 | 29 | 4.0 | 1.0% | 80.3% |



**Column explanation:**
-  Script: Rejected because under 70% of the letters are Arabic script, e.g. mostly English, or Chinese characters mixed in
- Length: Rejected because the tweet has fewer than 2 or more than 60 words
- Unparsed: The output held no usable tweet: the parser found no Arabic line, only an explanation or English

**Takeaway:**
- Jais-2 repeats itself almost word for word.
- TODO: check what each model generations looked like, what they got wrong, any drifts and any mislabeling

**Future runs:**
- 

## Universal Topic Clustering

One frozen topic list for every dataset, real or generated, so the topic mix of any two sets can be compared (quality row 5). Both tracks use it (D-018, D-019).

- **Pool:** 555,820 unique texts from 19 datasets, both tracks (`data/topics/pool/universal_v1.jsonl`, `scripts/topics/build_topic_pool.py`). Only Arabic-script texts (at least 70% Arabic letters), only human-written (no machine translation, no LLM output), no song lyrics. MLADI dev, ArSarcasm-v2 test and all synthetic sets are left out.
- **Cleaning (D-015):** placeholders, links and mentions removed, hashtags turned into words, laughter shortened, texts under 5 words dropped: 489,815 texts.
- **Cap:** at most 20,000 texts per dataset, so no single dataset sets the topics: 181,905 texts.
- **Clustering:** E5 embeddings, k-means with 50 clusters, seed 0 (`configs/quality/topics_universal_clean_k50.json`, 18 min). Ammar reviewed every cluster and named 18 topics. Report with tweets per cluster: `data/topics/universal_clean_k50_seed0/report.md`. Backup: private Hub dataset `Ammar-06/thesis-topic-embeddings`.

| Topic | Clusters | Texts | Share |
|---|---|---|---|
| Books and novels | 20, 19, 29, 40, 11 | 22,957 | 12.6% |
| COVID-19 | 18, 12, 22, 7, 21 | 18,835 | 10.4% |
| Hotels and stays | 33, 42, 31, 24, 49, 8 | 18,138 | 10.0% |
| Religion and prayer | 15, 34 | 9,325 | 5.1% |
| Politics and government | 30, 10 | 9,286 | 5.1% |
| War and conflict | 39, 5 | 9,144 | 5.0% |
| Restaurants and food | 46, 6, 25 | 9,126 | 5.0% |
| Love and feelings | 26, 47 | 8,634 | 4.7% |
| News and official announcements | 28, 2 | 6,455 | 3.5% |
| Products and shopping | 37, 13 | 6,298 | 3.5% |
| Greetings | 23, 32 | 5,357 | 2.9% |
| Films, TV, music and celebrities | 9, 36 | 5,331 | 2.9% |
| Football | 0 | 4,494 | 2.5% |
| Friendship and affection | 4 | 4,284 | 2.4% |
| Places, malls and attractions | 1 | 2,718 | 1.5% |
| Apps, phones and technology | 48 | 2,591 | 1.4% |
| Women's empowerment | 27 | 1,587 | 0.9% |
| Digital transformation | 38 | 1,407 | 0.8% |
| Not named | 14, 45, 3, 43, 44, 35, 17, 41, 16 | 35,938 | 19.8% |

**Takeaways:**
- Unlike D1, one subject is split by sentiment and length (hotels 6 clusters, books 5, COVID-19 5); these splits were merged, since only the subject counts.
- Books, COVID-19 and hotels are a third of the pool, and each comes mainly from one or two datasets (LABR and 100k Reviews; ArSen-20; TripAdvisor and 100k Reviews).
- Unnamed clusters are grouped by form, not subject: mixed chatter, very short emoji replies, stretched letters, questions (C16) and short negative statements (C17, a tone).
- The list is for measurement only. Generation topics stay the 24 of D-016.

## SG02

**Topic spread across the universal topic list**
Few shot Generation

Frozen list `universal_clean_k50_seed0` (50 E5 clusters, 18 named topics, D-019). Texts cleaned as the pool (D-015), under 5 words not scored. Effective topics = exp(entropy), mean ± std over 10 samples of 800 texts. Distance to real = Jensen-Shannon divergence (base 2, 0 = same mix, 1 = no overlap) between the set's topic shares (18 named topics + unnamed) and S1 real train. Generated by `python -m src.quality.topic_spread` (`results/quality/sentiment/universal_topics.json`).

| Set | Effective clusters (of 50) | Effective named topics (of 18) | Unnamed | Distance to real | War | Politics | News | Religion | Greetings | Love |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 real train | 15.6 ± 0.7 | 6.5 ± 0.5 | 19% | 0.000 | 38% | 6% | 7% | 3% | 3% | 4% |
| SG01 Jais-2 | 17.6 ± 0.5 | 7.0 ± 0.3 | 36% | 0.336 | 0% | 3% | 8% | 23% | 12% | 7% |
| SG01 Fanar | 16.8 ± 0.7 | 8.7 ± 0.4 | 25% | 0.257 | 4% | 10% | 9% | 15% | 19% | 6% |
| SG02 Fanar | 17.9 ± 0.5 | 10.2 ± 0.2 | 10% | 0.179 | 9% | 15% | 15% | 14% | 9% | 5% |
| SG01 Qwen3 | 15.7 ± 0.4 | 7.7 ± 0.3 | 39% | 0.272 | 1% | 9% | 9% | 14% | 2% | 16% |
| SG02 Qwen3 | 20.4 ± 0.5 | 10.3 ± 0.3 | 35% | 0.143 | 6% | 10% | 10% | 9% | 2% | 8% |
| SG01 Aya | 16.7 ± 0.4 | 8.8 ± 0.3 | 31% | 0.318 | 1% | 8% | 5% | 14% | 17% | 7% |
| SG02 Aya | 18.8 ± 0.3 | 10.9 ± 0.2 | 16% | 0.190 | 9% | 14% | 7% | 10% | 15% | 3% |



**Fidelity against diversity**


| Set | Fidelity | Fidelity NEU | MTLD | Vendi | Topic spread (of 30) | Effective universal topics (of 18) | Distance to real |
|---|---|---|---|---|---|---|---|
| S1 real (reference) | 80.3% | 78.9% | 2518 | 4.01 | 29 | 6.5 | 0.000 |
| SG01 Jais-2 | 98.0% | 90.1% | 339 | 2.76 | 9 | 7.0 | 0.336 |
| SG01 Fanar | 94.9% | 85.2% | 1123 | 3.09 | 11 | 8.7 | 0.257 |
| SG02 Fanar | 95.4% | 87.0% | 1756 | 3.41 | 13 | 10.2 | 0.179 |
| SG01 Qwen3 | 88.7% | 74.5% | 323 | 3.22 | 8 | 7.7 | 0.272 |
| SG02 Qwen3 | 88.2% | 74.8% | 507 | 3.62 | 17 | 10.3 | 0.143 |
| SG01 Aya | 91.2% | 73.7% | 499 | 2.77 | 7 | 8.8 | 0.318 |
| SG02 Aya | 89.0% | 67.7% | 1053 | 3.15 | 10 | 10.9 | 0.190 |

**Takeaway:**
- ArSarcasm-v2 is very focused on war
- need to identify the unnamed topics to train the E5 on them to generate better
- why is topic spread of 30 lower than topic spread of 18?
- need to increase MTLD, Vendi and possibly Topic spread of 30 if found to be useful


## SG03
**Why**: Open Synthetic data doesnt help we need few shot.

**Thought Process**: 
- i wanted to give the shots to focus on the examples, phenomenons or scentence types that create more errors. 
- **issues**: 
  - as per the annotation guidelines, News should be NEU, but many annotators have chosen POS or NEG based on the news itself not on the writers emotion, which is wrong.
  
| Type | Tweets | NEG | NEU | POS |
  |---|---|---|---|---|
  | Bad-news headline | 468 | 36% | 60% | 4% |
  | Good-news headline | 158 | 4% | 67% | 29% |
- i then went through all the cases that all the models got wrong (63) `@data/inspect/hard_cases/sr02_dev_hard_cases.md` and classified them into groups (Complaint, Lyric/praise, Lyric/sadness, Fan/ad post)
- wrote the opposing pair by changing only the part that decides the sentiment. 

- so this is how i constructed the prompt
  | Pair type | Tweet A → Tweet B | Pairs | What the model had to learn |
  |---|---|---|---|
  | Bad-news headline | NEU → NEG | 250 | A report is neutral; the writer's own anger makes it NEG |
  | Good-news headline | NEU → POS | 250 | A report is neutral; the writer's own joy makes it POS |
  | **Short dialect complaint** | NEG → NEU | **500** | A short dialect tweet with a complaint word isn't always NEG; some are neutral remarks |
  | Quoted lyric, praise | NEU → POS | 250 | Quoting a song is neutral; the writer's own praise makes it POS |
  | Quoted lyric, sadness | NEU → NEG | 250 | Quoting a song is neutral; the writer's own sadness makes it NEG |
  | **Fan / ad post** | POS → NEU | **500** | Hearts and hashtags on a promo or fan post don't always mean POS |
  - we also followed the annotation guidelines of the majority not of on the guidelines. 

**Dataset quality metrics (SQ04)**

Topic spread on the frozen universal list `universal_clean_k50_seed0` (50 E5 clusters, 18 named topics, D-019), as for SG02. Effective topics = exp(entropy), mean ± std over 10 samples of 800 texts. Distance to real = Jensen-Shannon divergence (base 2) between the set's topic shares (18 named topics + unnamed) and S1 real train. Source `results/quality/sentiment/universal_topics_sg03.json`.

| Set | Effective clusters (of 50) | Effective named topics (of 18) | Unnamed | Distance to real | War | Politics | News | Religion | Greetings | Love | Films, TV, music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 real train | 15.6 ± 0.7 | 6.5 ± 0.5 | 19% | 0.000 | 38% | 6% | 7% | 3% | 3% | 4% | 7% |
| SG03 Fanar | 14.8 ± 0.5 | 8.0 ± 0.2 | 27% | 0.255 | 1% | 2% | 17% | 1% | 2% | 15% | 19% |
| SG03-random Fanar | 19.7 ± 0.6 | 11.4 ± 0.4 | 19% | 0.147 | 7% | 18% | 8% | 4% | 2% | 6% | 12% |
| SG03 Qwen3 | 11.2 ± 0.3 | 6.5 ± 0.2 | 35% | 0.300 | 1% | 1% | 18% | 0% | 0% | 20% | 12% |
| SG03-random Qwen3 | 19.5 ± 0.7 | 9.2 ± 0.3 | 31% | 0.130 | 10% | 8% | 7% | 2% | 1% | 18% | 6% |
| SG03 Aya | 16.2 ± 0.7 | 8.6 ± 0.3 | 19% | 0.233 | 3% | 5% | 15% | 0% | 2% | 14% | 21% |
| SG03-random Aya | 21.6 ± 0.5 | 12.4 ± 0.4 | 25% | 0.110 | 10% | 10% | 8% | 4% | 3% | 7% | 9% |

Fidelity = share of texts whose requested label the SR01 MARBERT ensemble agrees with (real: accuracy on S1 dev). Imbalance over the requested variety × sentiment cells only. Source `results/quality/sentiment/{sg03,sg03r}_quality.json`; all sets in `tables/dataset_quality.md`.

| Set | Fidelity | Fidelity NEG / NEU / POS | MTLD | Vendi | Topic spread (of 30) | Effective universal topics (of 18) | Distance to real | MSA share | Dialectness | Repeats | Imbalance |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 real (reference) | 80.3% | 85% / 79% / 75% | 2518 | 4.01 | 29 | 6.5 | 0.000 | 22.4% | 0.54 | 1.0% | 37.7 : 1 |
| SG03 Fanar | 73.9% | 91% / 59% / 87% | 1865 | 3.83 | 18 | 8.0 | 0.255 | 31.0% | 0.46 | 0.0% | 4.3 : 1 |
| SG03-random Fanar | 68.8% | 87% / 48% / 91% | 2817 | 3.76 | 19 | 11.4 | 0.147 | 28.9% | 0.46 | 0.0% | 4.1 : 1 |
| SG03 Qwen3 | 68.5% | 78% / 56% / 84% | 989 | 3.94 | 18 | 6.5 | 0.300 | 24.7% | 0.51 | 5.0% | 4.1 : 1 |
| SG03-random Qwen3 | 55.9% | 65% / 46% / 67% | 1496 | 3.98 | 22 | 9.2 | 0.130 | 9.8% | 0.66 | 8.1% | 3.9 : 1 |
| SG03 Aya | 77.7% | 98% / 58% / 97% | 1435 | 3.63 | 16 | 8.6 | 0.233 | 23.8% | 0.53 | 1.1% | 4.0 : 1 |
| SG03-random Aya | 65.1% | 92% / 39% / 91% | 2162 | 3.50 | 17 | 12.4 | 0.110 | 11.0% | 0.61 | 0.0% | 4.0 : 1 |

SG03 changes four things besides the targeting: quantity (from 11,208 to 15,208 texts), source (LLM-written instead of human), format (minimal pairs instead of single tweets) and label mix (50% NEU). I built SG03-random to keep all four the same and remove only the targeting, so the comparison is fair and tests only the targeting.


## SG04
Test Set
| Type | Tweets |
|---|---|
| 1. Sarcastic praise (NEG → POS) | 141 |
| 2. Dry sarcastic jab (NEG → NEU) | 162 |
| 3. Maxim / reflection (NEU → NEG) | 194 |
| 4. Prayer / verse / greeting (NEU → POS) | 13 |
| 5. Election / promo hashtag (NEU → POS) | 26 |
| 6. Crying / laughing emoji | 47 |

These are the errors from test where at least 32/63 runs classified them wrong classified into groups.
This generation will focus on the errors from test instead of dev because in ArSarcasm-V2 the errors in dev almost dont exist in test, because test and dev are not equally balanced. This could be considered cheating the model, but how else will we generate data for the models weakness.

Your labels are saved in [sg04_review_ammar.csv](data/inspect/hard_cases/sg04_review_ammar.csv). The test gold labels are not changed.




| Type | Change | Pairs |
|---|---|---|
| 1. Sarcastic praise, POS → NEG | Keep. The task text says sincere praise or encouragement stays POS. | 500 |
| 2. Dry sarcastic jab, NEU → NEG | Keep. Merge in the reproach / disapproval tweets from type 3 (3.5, 3.10, 3.24): disapproval without negative words is NEG. | 600 |
| 3. Maxim / reflection | Narrow to real general sayings (لهفة البدايات ليست حبّ…), which stay NEU. Pair: saying NEU ↔ the writer's own sad or happy use of it, NEG / POS. | 400 |
| 4. Prayer / verse, NEU → POS | Keep. Only 13 test tweets, so it stays small. | 200 |
| 5. Spam hashtag | Drop. | 0 |
| 6. 😭 / 😂💔 | Redefine as a context pair. The same emoji appears in both tweets, and only the context decides: POS (excitement) ↔ NEG (sadness). That turns your "depends on context" into what the pair teaches. | 300 |

| Type | Read | Gold label wrong | Share |
|---|---|---|---|
| 1. Sarcastic praise | 32 | 6 | 19% |
| 2. Dry sarcastic jab | 32 | 0 | 0% |
| 3. Maxim / reflection | 32 | 4 | 13% |
- So the example tweets in the prompts must use my label, not the gold one.

**Type 1: sarcastic praise (keep)**
- Tweet A: real praise, POS.
- Tweet B: the same praise, but sarcastic, NEG.
- What the model learns: nice words can be mockery.
- Change: the prompt says real praise or encouragement stays POS.
**Types 2 + 3: neutral remark vs a dig (merge into one type)**
- Tweet A: a plain remark or joke, NEU.
- Tweet B: the same remark, but with a real dig at someone, NEG.
- Why merge: both types make this same pair. Type 2 errors miss the dig, and type 3 errors see a dig that isn't there. One pair fixes both.

**Type 4: prayer or verse (keep, small)**
- Tweet A: a prayer or verse alone, NEU.
- Tweet B: the same prayer plus the writer's own joy or thanks, POS.
- What the model learns: religious words alone are not POS.

**Type 5: spam hashtags (drop)**
- These tweets can't be read, as you said.

**Type 6: 😭 and 😂💔 (redefine)**
- Both tweets use the same emoji.
- Tweet A: excitement (e.g. a fan seeing their idol), POS.
- Tweet B: real sadness, NEG.
- What the model learns: the emoji alone doesn't decide; the context does. That is your "depends on context".


## Size

| Type | Pairs |
|---|---|
| 1. Sarcastic praise | 500 |
| 2+3. Remark vs dig | 1,000 |
| 4. Prayer / verse | 200 |
| 6. Emoji in context | 300 |
| **Total** | **2,000** (4,000 tweets, same as SG03) |

- Sentiment split: NEG 1,800, NEU 1,200, POS 1,000.
- This leans NEG, like the test set.
- Keep a Fidelity at a minimum of 80% (generation repeats until each set reaches 80%.) using That is judge-based filtering with a set-level target. It ranks pairs by how many sides an external judge (the SR01 MARBERT ensemble) confirms. It then keeps generating until set reaches 80% agreement.


**Dataset quality** (source `tables/dataset_quality.md`; fidelity = SR01 MARBERT judge, which SG04 was also selected by, so its ≥ 80% holds by construction)

| Dataset | Texts | Imbalance | MSA share | Dialectness | MTLD | Topics (of 30) | Universal clusters (of 50) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 real (train) | 11,171 | 37.7 : 1 | 22.4% | 0.54 | 2518 | 29 | 15.6 | 4.0 | 1.0% | 80.3% (85% / 79% / 75%) |
| SG03 Fanar | 4,000 | 4.3 : 1 | 31.0% | 0.46 | 1865 | 18 | 14.8 | 3.8 | 0.0% | 73.9% (91% / 59% / 87%) |
| SG03 Qwen3 | 4,000 | 4.1 : 1 | 24.7% | 0.51 | 989 | 18 | 11.2 | 3.9 | 5.0% | 68.5% (78% / 56% / 84%) |
| SG03 Aya | 4,000 | 4.0 : 1 | 23.8% | 0.53 | 1435 | 16 | 16.2 | 3.6 | 1.1% | 77.7% (98% / 58% / 97%) |
| SG04 (test-contaminated) Fanar | 4,000 | 2.4 : 1 | 22.6% | 0.51 | 1749 | 12 | 20.9 | 3.5 | 0.0% | 81.3% (90% / 53% / 99%) |
| SG04 (test-contaminated) Qwen3 | 4,000 | 3.2 : 1 | 25.8% | 0.49 | 901 | 9 | 18.6 | 3.5 | 3.0% | 80.7% (80% / 72% / 91%) |
| SG04 (test-contaminated) Aya | 4,000 | 2.6 : 1 | 18.8% | 0.58 | 1159 | 10 | 17.8 | 3.1 | 0.4% | 82.4% (98% / 44% / 100%) |

- Fidelity per type after selection (`results/filtering/sg04_<gen>.selection.json`):

| Type | Fanar | Qwen3 | Aya |
|---|---|---|---|
| Sarcastic praise | 86.0% | 64.2% | 100% |
| Public jab | 91.2% | 93.9% | 83.3% |
| Personal remark | 68.0% | 81.8% | 66.4% |
| Prayer | 50.5% | 57.3% | 50.0% |
| Emoji in context | 100% | 100% | 100% |
| **Set** | **81.3%** (2.0× requests) | **80.7%** (3.0×) | **82.4%** (2.0×) |

- Prayer stays near 50% for every generator: the judge reads neutral prayers as POS (the error the type targets).
- Note: types 2 and 3 were finally kept as two types (public jab 500, personal remark 500), not merged.
