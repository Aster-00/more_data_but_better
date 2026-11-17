# EESA Dataset metrics
## Exploring the dataset (EESA)
EESA-Corpus: Egyptian Arabic-English code-switched comments, labelled positive / negative / neutral. Most comments are YouTube comments on Egyptian songs, music videos, TV ads, films, series and TV shows. Source `data/datasets/sa/EESA-Corpus-main/` (official train / dev / test, no header row). Built by `python -m src.sentiment.build_eesa` (data versions E1 test, E2 train and dev; `docs/sentiment/data.md`).

The class-balance, script-mix, Self-BLEU and topic tables below come from `python -m src.sentiment.explore_eesa` (`results/quality/sentiment/eesa_explore.md`; no model, 6 s). They cover all 4,099 processed texts.

### Class balance

Share of texts per class (count in brackets):

| Split | Texts | NEG | NEU | POS |
|---|---|---|---|---|
| Train | 2,463 | 24.1% (594) | 31.6% (778) | 44.3% (1,091) |
| Dev | 818 | 24.1% (197) | 31.5% (258) | 44.4% (363) |
| Test | 818 | 24.1% (197) | 31.5% (258) | 44.4% (363) |
| All | 4,099 | 24.1% (988) | 31.6% (1,294) | 44.3% (1,817) |

- POS is the largest class (44%) and NEG the smallest (24%).
- The three splits have the same class shares, so the official split was stratified.

### Here are it's annotation guidelines
TODO: the README does not give the annotation guidelines; take them from the EESA paper (not checked yet, nothing here is invented).

What the labels look like in EESA train and dev (my keyword rules, 3,282 texts; observed, not the official guidelines):
- Insulting the people who pressed dislike is NEG (42 of 42 such comments).
- Channel promotion ("subscribe to my channel", links) is mostly NEU (82%).
- "Who loves X, press like" is mostly NEU (72%).
- Saying a song is copied ("مسروقة من ...") is mostly NEG (72%).
- Greetings from another country are almost always POS (97%).

### Script and code-switching (quality row 8 rules, all 4,100 texts)

- The English is mostly platform words (dislike, like, subscribe, views), short praise (love, nice, wow) and names (BTS, we, Tamer).

Script mix per text: Arabic and Latin share of its Arabic + Latin letters (links and mentions removed), in 10-point bins.

| share | Arabic Script perc | Latin Script Perc | Texts |
|----|----|----|----|
| 6.7% | 95-100% | 0-5% | 273 |
| 24.0% | 85-95% | 5-15% | 983 |
| 24.7% | 75-85% | 15-25% | 1,014 |
| 15.2% | 65-75% | 25-35% | 622 |
| 11.8% | 55-65% | 35-45% | 482 |
| 7.7% | 45-55% | 45-55% | 317 |
| 5.7% | 35-45% | 55-65% | 235 |
| 2.7% | 25-35% | 65-75% | 110 |
| 1.0% | 15-25% | 75-85% | 43 |
| 0.4% | 5-15% | 85-95% | 18 |
| 0.0% | 0-5% | 95-100% | 2 |

- Only 6.7% of texts are (almost) pure Arabic script; only 2 texts are (almost) pure Latin.
- Most texts (64%) are 65-95% Arabic letters: Arabic sentences with a few English words.
- 29.3% have 35% or more Latin letters.

### Self-BLEU (1,000 random texts, seeds 0-4)
How much texts copy each other's phrasing: 0 = no shared n-grams, 1 = identical. Same tokenisation as the other quality rows.

| Set | Self-BLEU |
|---|---|
| EESA train | 0.106 ± 0.005 |
| EESA all splits | 0.107 ± 0.002 |
| SG01-EASA Fanar | 0.150 ± 0.002 |
| SG01-EASA Qwen3 | 0.120 ± 0.002 |
| SG01-EASA Aya | 0.376 ± 0.005 |
| ArSarcasm-v2 train (S1) | 0.069 ± 0.003 |

- EESA repeats phrasing more than ArSarcasm-v2 (0.106 vs 0.069).
- The SG01-EASA sets repeat more than EESA; Aya repeats 3.5 times as much.

### Topics (universal E5 list, D-019; 2,505 of 4,099 texts in the pool)

| Topic | Texts | Share | NEG / NEU / POS |
|---|---|---|---|
| Unclustered | 1,329 | 53.1% | 41% / 31% / 28% |
| Films, TV, music and celebrities | 580 | 23.2% | 9% / 24% / 67% |
| Greetings | 122 | 4.9% | 1% / 18% / 81% |
| Love and feelings | 117 | 4.7% | 21% / 38% / 41% |
| Apps, phones and technology | 94 | 3.8% | 21% / 69% / 10% |
| Friendship and affection | 91 | 3.6% | 5% / 38% / 56% |
| Politics and government | 55 | 2.2% | 62% / 13% / 25% |
| Religion and prayer | 46 | 1.8% | 9% / 24% / 67% |
| War and conflict | 19 | 0.8% | 68% / 26% / 5% |
| Products and shopping | 19 | 0.8% | 11% / 21% / 68% |
| Books and novels | 8 | 0.3% | 12% / 12% / 75% |
| News and official announcements | 7 | 0.3% | 14% / 86% / 0% |
| Football | 5 | 0.2% | 20% / 60% / 20% |
| COVID-19 | 4 | 0.2% | 0% / 75% / 25% |
| Restaurants and food | 4 | 0.2% | 25% / 75% / 0% |
| Places, malls and attractions | 3 | 0.1% | 0% / 33% / 67% |
| Hotels and stays | 2 | 0.1% | 50% / 50% / 0% |

Not in the pool: 1,487 texts not Arabic script, 107 under 5 words.




## Generation (SG01-EASA)

| Dataset | Texts | MSA share | Dialectness | MTLD | Self-BLEU | Topics (of 30) | Universal clusters (topics of 19) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|---|
| EESA real (train) | 2,463 | 10.3% | 0.61 | 1,226 | 0.106 | 30 | 4.6 | 3.8 | 0.2% | 89.4% (93 / 80 / 94) |
| SG01-EASA Fanar | 1,320 | 1.6% | 0.77 | 589 | 0.150 | 15 | 3.0 | 3.0 | 0.0% | 84.2% (98 / 55 / 100) |
| SG01-EASA Qwen3 | 1,320 | 2.8% | 0.72 | 216 | 0.120 | 13 | 3.1 | 3.0 | 1.5% | 85.3% (84 / 73 / 99) |
| SG01-EASA Aya | 1,320 | 1.0% | 0.80 | 392 | 0.376 | 9 | 3.3 | 2.5 | 0.0% | 77.5% (100 / 32 / 100) |
| EESA dev (99-text samples) | 818 | 10.4% | 0.61 | 1,079 ± 224 | 0.062 ± 0.008 | 28.0 ± 1.6 | 4.2 ± 0.4 | 3.0 ± 0.1 | 0.0% | N/A |
| SG01-most-errors | 99 | 5.1% | 0.73 | 645 | 0.072 | 25 | 3.0 | 3.0 | 0.0% | N/A |

The real row's fidelity is the SR01-EASA judge's accuracy on EESA dev; the synthetic rows show how often that judge confirms the requested label. Self-BLEU: 1,000 random texts, mean of seeds 0–4, from `src.sentiment.explore_eesa`; higher = more repeated phrasing. Universal clusters (topics of 19): effective number of universal topics, the 18 named topics plus all unnamed clusters as one "Unclustered" topic (exp of entropy of the whole-set shares, `src.sentiment.explore_eesa`).

**Code-switching** (quality row 8 rules; not yet in the table):

| Dataset | Has a Latin word | Mixed script | Words per comment |
|---|---|---|---|
| EESA real | 99% | 34% | 12.7 |
| SG01-EASA Aya / Fanar / Qwen3 | 18% / 28% / 27% | 5% / 8% / 3% | 30.1 / 15.9 / 22.6 |

**What the quality rows say:**
- **Little variety:** MTLD is a fifth to a half of EESA's, and the sets cover 9–15 topics against 30.
- **Too little code-switching:** the generators ignore most of the "mix in English" instruction.
- **Too long:** comments run 1.3–2.4 times longer than real ones.
- **Weak NEU:** the judge confirms only 32% of Aya's NEU comments.

### Error analysis on 0 shot
**SG01-most-errors:** the 99 EESA dev texts that at least 43 of the 84 EESA runs get wrong (SR01-EASA 21 + SR02-EASA 63). Built by `python -m src.sentiment.most_errors_eesa` (texts in `data/inspect/hard_cases/sg01_most_errors_eesa_clusters.md`, numbers in `results/quality/sentiment/sg01_most_errors_eesa.md`).

- Class mix: NEU 48%, POS 33%, NEG 18% (dev: 32% / 44% / 24%). NEU is the hardest class.
- The last two rows of the quality table compare only with each other. The dev row is the mean ± std over 20 random 99-text samples of dev. MSA share, dialectness and repeats use all texts.
- The errors are more dialectal than dev (0.73 vs 0.61) and lexically poorer (MTLD 645 vs 1,079 ± 224).
- They spread over fewer universal topics (3.0 vs 4.2 ± 0.4) and repeat more phrasing (Self-BLEU 0.072 vs 0.062 ± 0.008).
- Vendi is the same as dev (3.0).

**E5 error clusters** (k-means, k = 8, on the 99 texts). Names by Ammar (2026-11-10), after reading the texts.

| Cluster | Texts | Main error (gold → prediction) | Universal topics | Name |
|---|---|---|---|---|
| E1 | 22 | POS→NEU 12, NEG→NEU 4, NEG→POS 2, NEU→POS 2, NEU→NEG 1, POS→NEG 1 | Unclustered 14, Films/TV/music 4 | Hype and fandom comments |
| E2 | 19 | NEU→NEG 19 | Unclustered 19 | "Why the dislikes?" questions |
| E3 | 16 | NEU→NEG 6, NEG→NEU 4, POS→NEU 3, NEU→POS 2, POS→NEG 1 | Unclustered 7, Films/TV/music 3, Greetings 3 | Long opinion with a question or advice |
| E6 | 14 | POS→NEU 5, NEU→POS 5, POS→NEG 3, NEG→POS 1 | Unclustered 9, Films/TV/music 3 | Indirect praise and wishes |
| E7 | 13 | NEG→POS 3, POS→NEU 3, NEU→POS 3, NEU→NEG 2, POS→NEG 2 | Unclustered 7, under 5 words 6 | Short stretched or emoji comments |
| E0 | 8 | NEG→NEU 2, POS→NEU 2, NEU→POS 1, POS→NEG 1, NEG→POS 1, NEU→NEG 1 | Love and feelings 3, Films/TV/music 2 | English names of films, shows and products |
| E5 | 4 | NEU→NEG 4 | Unclustered 3 | Neutral remarks on a negative subject |
| E4 | 3 | NEU→POS 2, NEG→NEU 1 | under 5 words 3 | One or two words |


## Dev Set analysis

### Errors of the 8-epoch runs on EESA dev (SR05-EASA, SR06-EASA, SR06-random-EASA)
The 210 BERT runs trained for 8 epochs (D-036): 7 BERTs × 3 seeds, real only and + SG01-EASA (84), + SG02-EASA (63), + SG02-random-EASA (63). EESA dev only; test is not used. Numbers from `python -m src.sentiment.dev_errors_eesa` (`results/quality/sentiment/eesa_dev_errors_8ep.json`). SR06-EASA is dev-contaminated: its few-shot examples were SG01-most-errors dev texts.

- 452 of the 818 dev texts (55%) are never wrong in any run.
- 71 texts are wrong in a majority of the runs (shared errors); 17 in at least 90%, 5 in all 210.
- 64 of the 71 shared errors are already in SG01-most-errors: 8 epochs do not fix a new kind of error.
- Without the contaminated SR06-EASA runs there are 75 shared errors (majority of the other 147 runs).

**Error per class** (error rate = share of the class's texts a run gets wrong, mean over the 210 runs)

| Gold class | Dev texts | Error rate | Of all errors | Predicted as NEG / NEU / POS | Shared errors |
|---|---|---|---|---|---|
| NEG | 197 | 13.4% | 25.4% | – / 65% / 35% | 18 |
| NEU | 258 | 16.8% | 41.9% | 51% / – / 49% | 28 |
| POS | 363 | 9.3% | 32.7% | 32% / 68% / – | 25 |

| Condition | Runs | Error rate | NEG | NEU | POS |
|---|---|---|---|---|---|
| SR05-EASA (real only, + SG01-EASA) | 84 | 12.9% | 12.4% | 18.2% | 9.3% |
| SR06-random-EASA | 63 | 12.8% | 13.0% | 17.1% | 9.7% |
| SR06-EASA (dev-contaminated) | 63 | 12.3% | 15.0% | 14.7% | 9.1% |

- NEU is the hardest class (16.8%) and makes 42% of all errors; its errors split evenly into NEG and POS.
- POS is the easiest (9.3%), but when it fails it is mostly read as NEU (68%).
- NEG is mostly read as NEU (65%).
- SR06-EASA has fewer NEU errors (14.7% vs 17–18%) but more NEG errors (15.0% vs 12–13%); this is on dev, where its examples came from, and its test score was not better (D-036).

**Error per script share** (Arabic share of the text's Arabic + Latin letters, links and mentions removed; same bins as the script-mix table above)

| Arabic share | Latin share | Dev texts | Error rate | Shared errors | Share of bin | NEG / NEU / POS (gold) |
|---|---|---|---|---|---|---|
| 95-100% | 0-5% | 57 | 10.4% | 4 | 7.0% | 16 / 12 / 29 |
| 85-95% | 5-15% | 197 | 11.4% | 13 | 6.6% | 54 / 64 / 79 |
| 75-85% | 15-25% | 208 | 12.9% | 21 | 10.1% | 60 / 69 / 79 |
| 65-75% | 25-35% | 109 | 13.3% | 8 | 7.3% | 27 / 30 / 52 |
| 55-65% | 35-45% | 100 | 11.2% | 10 | 10.0% | 18 / 33 / 49 |
| 45-55% | 45-55% | 69 | 14.9% | 5 | 7.2% | 9 / 27 / 33 |
| 35-45% | 55-65% | 46 | 16.1% | 6 | 13.0% | 6 / 14 / 26 |
| 25-35% | 65-75% | 20 | 18.5% | 3 | 15.0% | 5 / 5 / 10 |
| 15-25% | 75-85% | 11 | 10.9% | 1 | 9.1% | 2 / 4 / 5 |
| 5-15% | 85-95% | 1 | 7.6% | 0 | 0.0% | 0 / 0 / 1 |

- Error rises with the Latin share, from 10.4% (almost pure Arabic) to 15–18.5% when 45–75% of the letters are Latin.
- The rise is moderate: shared errors have a mean Arabic share of 70%, dev as a whole 73%.
- Texts with more than 75% Latin letters are too few (12) to read.

**Error types of the 71 shared errors** (SG01-most-errors types, named by Ammar 2026-11-10; script share in four bands)

| Error type | Shared errors | Gold NEG / NEU / POS | Main error (gold → predicted) | Arabic share 95-100 / 65-95 / 35-65 / under 35% | Mean Arabic share |
|---|---|---|---|---|---|
| Hype and fandom comments | 16 | 5 / 1 / 10 | POS→NEU 9, NEG→NEU 3 | 1 / 9 / 4 / 2 | 70% |
| Long opinion with a question or advice | 13 | 4 / 6 / 3 | NEU→NEG 5, NEG→NEU 4 | 2 / 9 / 2 / 0 | 82% |
| Short stretched or emoji comments | 10 | 2 / 4 / 4 | NEU→NEG 2, NEG→POS 2 | 0 / 2 / 8 / 0 | 57% |
| Indirect praise and wishes | 10 | 1 / 4 / 5 | NEU→POS 4, POS→NEU 3 | 0 / 8 / 2 / 0 | 74% |
| Not in SG01-most-errors | 7 | 3 / 4 / 0 | NEU→POS 3, NEG→NEU 3 | 0 / 4 / 2 / 1 | 64% |
| English names of films, shows and products | 6 | 2 / 1 / 3 | POS→NEU 2, NEU→POS 1 | 1 / 4 / 1 / 0 | 78% |
| "Why the dislikes?" questions | 5 | 0 / 5 / 0 | NEU→NEG 5 | 0 / 5 / 0 / 0 | 79% |
| One or two words | 3 | 1 / 2 / 0 | NEU→POS 2, NEG→NEU 1 | 0 / 0 / 2 / 1 | 42% |
| Neutral remarks on a negative subject | 1 | 0 / 1 / 0 | NEU→NEG 1 | 0 / 1 / 0 / 0 | 83% |

- The most Latin-heavy types are short comments: Short stretched or emoji comments (8 of 10 at 35–65% Arabic) and One or two words (42% Arabic). In these, an English word or a name carries the meaning.
- Hype and fandom comments are mostly POS read as NEU; 6 of 16 have 35% or more Latin letters (song, film and band names).
- Long opinion, "Why the dislikes?" and Neutral remarks are mostly Arabic (79–83%): their errors come from meaning, not from script.

**What the errors have in common** (Claude's reading of the 17 texts wrong in at least 90% of the runs; to be checked by Ammar)
1. Praise without a praise word, read as NEU: recommendations or habits that imply liking ("ممكن تراجع isle of dogs؟ مش هتندم", "يوميه اسمع الاغنيه الساعه اربعه", "انا جيت عشان كلمه BTS").
2. Sentiment carried by an English word, slang or irony: "هو الراجل ده vampire … بيصغر في السن" (praise, read as NEG), "هتدفن Mohamed Ramadan" (NEG, read as NEU), "200 مليون views على ما حرمه الله مبروك" (sarcastic NEG, read as POS).
3. Neutral explanations with negative words, read as NEG: comments that describe an illness ("عنده ADD وده مرض…", "مرض نفسي اسمه seeking attention…").
4. Dislike and channel comments whose labels disagree within EESA: "ايه كمية ال dislike ده 🤣" is NEU but "هى الناس الي عامله Dislike عندهم ودان…" is NEG; "قمر.ممكن دعم لقناتي" is POS while most channel promotion is NEU. The 7 new shared errors are of the same kinds (3 channel promotions NEU→POS, 3 dislike questions NEG→NEU, 1 neutral remark).

**Takeaway: the 8-epoch runs share one small hard core (71 dev texts, 9%), mostly the same texts as before. It is implicit sentiment (no sentiment word, irony, meaning in an English word) and EESA's own inconsistent labels for dislike and channel comments, centred on NEU. A higher Latin share adds some error (10% → 15–18%), but most hard texts are 65–95% Arabic, so script is a smaller factor than meaning.**

### Dev errors: 3 epochs against 8 epochs
Each 8-epoch run is paired with the 3-epoch run of the same BERT, generator and seed; only the epoch count differs: SR05-EASA ↔ SR03-EASA, SR06-EASA ↔ SR04-EASA, SR06-random-EASA ↔ SR04-random-EASA (210 pairs). EESA dev only. Numbers from `python -m src.sentiment.dev_errors_eesa --compare-3ep` (`results/quality/sentiment/eesa_dev_errors_3v8ep.json`).

| Gold class | Dev texts | Error rate 3 epochs | 8 epochs | Change |
|---|---|---|---|---|
| NEG | 197 | 16.0% | 13.4% | −2.7 |
| NEU | 258 | 21.1% | 16.8% | −4.2 |
| POS | 363 | 10.3% | 9.3% | −1.0 |
| **All** | 818 | 15.1% | 12.7% | −2.4 |

| Condition | Pairs | Error rate 3 epochs | 8 epochs | Change |
|---|---|---|---|---|
| SR05-EASA (real only, + SG01-EASA) | 84 | 15.4% | 12.9% | −2.6 |
| SR06-random-EASA | 63 | 15.1% | 12.8% | −2.3 |
| SR06-EASA (dev-contaminated) | 63 | 14.7% | 12.3% | −2.4 |

- 209 of the 210 runs make fewer dev errors at 8 epochs; none makes more.
- NEU gains most (−4.2 points), POS least (−1.0).
- Never-wrong texts rise from 398 to 452; shared errors (wrong in a majority of runs) fall from 95 to 71.
- Per text, 696 of 818 move by 20 runs or fewer (of 210); 93 are wrong in at least 21 fewer runs, 29 in at least 21 more.

**Shared errors per error type**

| Error type | Shared at 3 epochs | Shared at 8 epochs | In both | Mean wrong runs 3 → 8 (of 210) |
|---|---|---|---|---|
| Hype and fandom comments | 21 | 16 | 16 | 161 → 145 |
| "Why the dislikes?" questions | 16 | 5 | 5 | 158 → 91 |
| Long opinion with a question or advice | 16 | 13 | 13 | 161 → 157 |
| Short stretched or emoji comments | 13 | 10 | 10 | 157 → 138 |
| Indirect praise and wishes | 13 | 10 | 10 | 156 → 144 |
| English names of films, shows and products | 8 | 6 | 6 | 165 → 143 |
| One or two words | 3 | 3 | 3 | 174 → 164 |
| Not in SG01-most-errors | 3 | 7 | 1 | 88 → 110 |
| Neutral remarks on a negative subject | 2 | 1 | 1 | 158 → 142 |

- 65 of the 71 shared errors at 8 epochs were already shared at 3 epochs; 30 were fixed and 6 are new.
- "Why the dislikes?" questions changed most: 11 of 16 are fixed (wrong runs 158 → 91). With more training the BERTs learn that a plain "why the dislikes?" question is NEU.
- They over-apply it: 3 of the 6 new shared errors are dislike questions with an insult or mockery that are gold NEG and are now read as NEU ("هى الناس الي عامله Dislike عندهم ودان…", "معلش سوال اللي عامل dislike هما اي ف المجتمع", "10K dislike ليه !! … فاكرينها علامة Download"). The other 3 new ones: 2 channel or video promotions (NEU read as POS) and 1 neutral remark read as NEG.
- Long opinion with a question or advice barely moves (161 → 157): more epochs do not help with meaning spread over a long comment.
- Several fixed texts carry their sentiment in English ("Number 1", "number one", "over", "Dont mix"), so 8 epochs also learn some English sentiment words.

**Takeaway: 8 epochs lower the dev error in almost every run (15.1% → 12.7%), most for NEU, and fix most "Why the dislikes?" errors. The hard core stays: 65 of the 71 shared errors were already there at 3 epochs. The dislike fix moves the problem rather than solving it: plain dislike questions are now right, and the insulting ones (gold NEG) are now read as NEU, because EESA labels them by a rule the models cannot see.**

## Next
1. **Hard cases:** I build the list of EESA dev comments that most of the 63 SR02-EASA runs get wrong (`hard_cases --corpus eesa`). It takes seconds and needs no GPU.
2. **Your type choice:** you read the list and pick the types for SG03-EASA.


## Generation (SG02-EASA) (*most frequently errored clusters*) Few shot
**Setup (D-034):** few-shot generation for the 4 most frequent SG01-most-errors types: "Why the dislikes?" questions, Hype and fandom comments, Long opinion with a question or advice, Indirect praise and wishes.
- 330 texts per type, 1,320 per generator (= SG01-EASA). Class mix within each type = its gold mix; in total NEG 196 / NEU 658 / POS 466.
- Examples: 5 error texts of the request's type and class (EESA dev, so **dev-contaminated**). Prompt `prompts/sentiment/fewshot_eesa_v1.json`: SG02's structure, SG01-EASA's wording, no "write about something else".
- Control **SG02-random-EASA**: same prompt, size and class mix, but 5 random EESA train comments per request.
- Training: SR04-EASA (+ SG02-EASA) and SR04-random-EASA (+ SG02-random-EASA), with the epoch chosen by training loss (D-035); baseline SR03-EASA.

**Quality rows**

| Dataset | Texts | MSA share | Dialectness | MTLD | Self-BLEU | Topics (of 30) | Universal clusters (topics of 19) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|---|
| EESA real (train) | 2,463 | 10.3% | 0.61 | 1,226 | 0.106 | 30 | 4.6 | 3.8 | 0.2% | 89.4% (93 / 80 / 94) |
| SG02-EASA Fanar | 1,320 | 5.1% | 0.71 | 627 | 0.120 | 15 | 3.1 | 3.1 | 0.0% | 77.8% (95 / 57 / 100) |
| SG02-EASA Qwen3 | 1,320 | 2.4% | 0.81 | 221 | 0.141 | 18 | 2.4 | 3.1 | 1.9% | 70.1% (69 / 55 / 91) |
| SG02-EASA Aya | 1,320 | 3.6% | 0.76 | 389 | 0.354 | 11 | 3.4 | 2.6 | 0.0% | 81.1% (99 / 62 / 100) |
| SG02-random-EASA Fanar | 1,320 | 7.6% | 0.64 | 654 | 0.137 | 13 | 3.0 | 3.3 | 0.0% | 87.7% (96 / 77 / 100) |
| SG02-random-EASA Qwen3 | 1,320 | 3.3% | 0.74 | 227 | 0.109 | 17 | 3.1 | 3.4 | 2.0% | 90.7% (76 / 90 / 99) |
| SG02-random-EASA Aya | 1,320 | 4.5% | 0.69 | 468 | 0.314 | 12 | 3.7 | 2.8 | 0.0% | 87.5% (99 / 75 / 100) |

- The judge confirms fewer targeted texts (70–81% vs 88–91%), because these types are exactly what the judge gets wrong.
- Both few-shot sets are closer to real EESA than zero-shot SG01-EASA (more MSA, lower dialectness), but still far less varied (MTLD 221–654 vs 1,226).

Run results (SR04-EASA, SR04-random-EASA, BERTs and LLMs) are in `docs/sentiment/chron-EESA.md`.

## Generation (SG03-EASA) (*most frequently errored clusters*) Minimal Pairs


## Generation (SG03-EASA) matrix-language pilot
**Setup (D-037):** zero-shot generation as SG01-EASA, with one instruction that states (or does not state) the matrix language, the language that supplies the grammar of the code-switched comment. Arms: **NM** = mix Egyptian Arabic and English, no matrix stated; **DM3** = Egyptian Arabic sentence with English words inserted (prompt v3); **DM** = the same with prompt v2 (Qwen3 only, replaced by v3 because it inserted almost no English); **EM** = English sentence with Egyptian Arabic words inserted. Every arm asks for about 1 English word in 5 (EESA train: 23% Latin-script words).
- 1,320 texts per set (= SG01-EASA), NEG 440 / NEU 440 / POS 440 requested; Qwen3, Aya and Fanar; 10 sets.
- Prompts: `prompts/sentiment/matrix_eesa_{nm,dm,em}_v2.json`, `matrix_eesa_dm_v3.json`; the arms differ only in the writing instruction.
- Filter `configs/filtering/sentiment_eesa.json` (duplicates against EESA train and dev, at least 10% Arabic letters).
- Training: SR07-EASA (3 epochs) and SR08-EASA (8 epochs); results in `docs/sentiment/chron-EESA.md`.

**Quality rows**

| Dataset | Texts | MSA share | Dialectness | MTLD | Self-BLEU | Topics (of 30) | Universal clusters (topics of 19) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|---|
| EESA real (train) | 2,463 | 10.3% | 0.61 | 1,226 | 0.106 | 30 | 4.6 | 3.8 | 0.2% | 89.4% (93 / 80 / 94) |
| SG03-EASA-NM Aya | 1,320 | 3.9% | 0.70 | 402 | 0.392 | 9 | 3.3 | 2.4 | 0.0% | 75.0% (100 / 25 / 100) |
| SG03-EASA-NM Fanar | 1,320 | 1.6% | 0.74 | 1,045 | 0.110 | 14 | 3.1 | 2.9 | 0.0% | 78.9% (96 / 41 / 99) |
| SG03-EASA-NM Qwen3 | 1,320 | 1.3% | 0.79 | 73 | 0.106 | 12 | 2.9 | 3.2 | 1.4% | 79.2% (65 / 76 / 96) |
| SG03-EASA-DM3 Aya | 1,320 | 2.2% | 0.74 | 320 | 0.448 | 8 | 3.2 | 2.2 | 0.1% | 71.1% (99 / 15 / 100) |
| SG03-EASA-DM3 Fanar | 1,320 | 0.4% | 0.79 | 850 | 0.119 | 11 | 3.3 | 2.9 | 0.0% | 74.5% (97 / 26 / 100) |
| SG03-EASA-DM3 Qwen3 | 1,320 | 1.0% | 0.81 | 90 | 0.103 | 13 | 2.4 | 2.9 | 1.0% | 70.2% (78 / 44 / 88) |
| SG03-EASA-DM Qwen3 (prompt v2) | 1,320 | 0.9% | 0.85 | 42 | 0.088 | 10 | 2.4 | 3.3 | 1.7% | 74.2% (63 / 71 / 89) |
| SG03-EASA-EM Aya | 1,320 | 10.1% | 0.60 | 513 | 0.380 | 9 | 3.9 | 2.5 | 0.0% | 75.8% (100 / 28 / 100) |
| SG03-EASA-EM Fanar | 1,320 | 4.7% | 0.48 | 514 | 0.208 | 12 | 4.0 | 3.4 | 0.0% | 65.2% (75 / 22 / 99) |
| SG03-EASA-EM Qwen3 | 1,320 | 2.0% | 0.57 | 73 | 0.650 | 9 | 2.7 | 2.8 | 0.5% | 71.5% (100 / 15 / 100) |

Same measures as the SG01-EASA table. Quality rows from `src.sentiment.measure_quality` (`docs/sentiment/datasets/EESA/dataset_quality.csv`); Self-BLEU and universal clusters from `src.sentiment.explore_eesa`.

**Code-switching** (script per word, `src/sentiment/cmi.py`; CMI = code-mixing index, 0 = one language only; `results/quality/sentiment/cmi_sg03_eesa_*.json`)

| Set | Requests | Not parsed | Rejected by script filter | Latin-script words | CMI | Texts with no switch | Switch-point fraction | Words per text |
|---|---|---|---|---|---|---|---|---|
| EESA train (real) | – | – | – | 22.8% | 22.6 | 1% | 0.23 | 12.6 |
| SG03-EASA-NM Aya | 1,716 | 0 | 0 | 7.7% | 7.2 | 80% | 0.01 | 23.7 |
| SG03-EASA-NM Fanar | 2,400 | 299 | 48 | 21.0% | 18.2 | 28% | 0.09 | 16.0 |
| SG03-EASA-NM Qwen3 | 1,716 | 7 | 6 | 4.8% | 5.2 | 64% | 0.04 | 21.0 |
| SG03-EASA-DM3 Aya | 1,716 | 0 | 0 | 6.8% | 6.6 | 81% | 0.01 | 23.5 |
| SG03-EASA-DM3 Fanar | 1,716 | 75 | 20 | 25.1% | 23.7 | 9% | 0.10 | 20.1 |
| SG03-EASA-DM3 Qwen3 | 1,716 | 32 | 3 | 4.8% | 5.6 | 56% | 0.07 | 20.2 |
| SG03-EASA-DM Qwen3 (prompt v2) | 1,716 | 98 | 3 | 2.5% | 2.9 | 75% | 0.02 | 27.1 |
| SG03-EASA-EM Aya | 1,716 | 0 | 0 | 12.0% | 11.2 | 72% | 0.03 | 28.4 |
| SG03-EASA-EM Fanar | 3,300 | 825 | 615 | 63.6% | 23.4 | 2% | 0.19 | 16.7 |
| SG03-EASA-EM Qwen3 | 3,300 | 845 | 475 | 66.2% | 25.3 | 0% | 0.10 | 22.4 |

**What the quality rows say:**
- **Only Fanar code-switches like EESA:** 21–25% Latin-script words and CMI 18–24 in NM and DM3 (EESA 22.8%, 22.6). Aya stays at 7–12% in every arm, Qwen3 at 2.5–4.8% outside EM.
- **The English-matrix arm is the mirror of EESA:** Fanar and Qwen3 write mostly English (64–66% Latin-script words; 83% and 87% of texts mostly English). It cost 3,300 requests each, with 825–845 not parsed and 475–615 under the 10% Arabic-letter rule.
- **The dialect-matrix prompt v2 removed English with Qwen3:** 2.5% Latin-script words and 75% of texts with no switch, against 4.8% and 64% with no instruction. The reworded v3 only brings Qwen3 back to the NM level.
- **Little lexical variety except Fanar:** MTLD 42–90 for Qwen3, 320–513 for Aya, 514–1,045 for Fanar (EESA 1,226). Fanar NM is the closest generated set to EESA so far.
- **Aya and Qwen3 EM repeat phrasing:** Self-BLEU 0.38–0.45 for every Aya set (as SG01-EASA Aya, 0.376) and 0.650 for Qwen3 EM. Qwen3 NM and DM have low MTLD but EESA-level Self-BLEU (0.09–0.11): a small vocabulary in varied word order.
- **Few topics:** 8–14 of 30 (EESA 30). The universal clusters of the English-matrix Aya and Fanar sets (3.9–4.0) are close to EESA's 4.6, but the topic list was built on Arabic-script texts, so mostly-English texts are placed less reliably.
- **Dialectness and MSA share are not comparable for EM:** Sentence-ALDi scores Arabic, and the EM texts are largely English (dialectness 0.48–0.60 against 0.70–0.85 for the other arms).
- **Weak NEU:** the judge confirms 15–44% of the NEU comments in 8 of the 9 three-generator sets (76% for Qwen3 NM; real dev 80%). NEG and POS are confirmed at 63–100%.
- **Too long:** 16–28 words per text against 12.6.
