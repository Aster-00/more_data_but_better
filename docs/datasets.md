## Choosing a second sentiment dataset: standards (2026-10-31)

**Why:** ArSarcasm-v2's official splits do not come from the same distribution (SA-E01): tweets with a link 38.5% in train vs 14.7% in test, labels NEG / NEU / POS 37 / 46 / 17% in train vs 56 / 25 / 19% in test. Hard cases found on dev (cut from train) therefore do not carry over to test. The SG03 experiment is repeated on a dataset that meets the standards below.

**Standards** (a dataset must meet all six):
- **S1 human labels:** sentence-level sentiment labelled by people, not derived from star ratings, emojis or lexicons (label trust rule in CLAUDE.md).
- **S2 three classes:** POS / NEG / NEU, as ArSarcasm-v2, so macro F1 and the NEU findings compare.
- **S3 Arabic script:** a text counts as Arabic script if at least 70% of its letters are Arabic (quality row 8). The dataset passes if at least 70% of its texts are Arabic script, **or** if after keeping only the Arabic-script texts it still meets S4 and S5 (it stays stratified and large enough). Reason: our generation rule (D-010) produces Arabic script only, so training and test data must be Arabic script too.
- **S4 uniform splits:** an official train and test split from the same distribution, measured after the S3 filter: every class share within 5 points between train and test; link, mention and hashtag shares within 5 points; mean length within a factor 1.25. Without an official split a stratified split could be made, but then there is no independent benchmark to compare with published results.
- **S5 size:** after the S3 filter, train at least 1,000 texts, test at least 500, smallest class at least 5% of train (macro F1 needs every class).
- **S6 text available:** the texts are in the download, not tweet IDs only.

**Result** (`python -m src.sentiment.dataset_survey`, table `tables/dataset_survey.md`; all downloaded sentiment datasets):

| Dataset | Arabic script | Train / test after filter | Train vs test labels (NEG / NEU / POS) | Max label gap | Passes |
|---|---|---|---|---|---|
| ArSarcasm-v2 (current) | 81% | 9,900 / 2,730 | 43 / 39 / 19 vs 59 / 23 / 18 | 16 points (links 25% vs 7%) | no (S4) |
| **Mawqif** | 100% | 3,492 / 619 | 27 / 31 / 42 vs 28 / 31 / 42 | 1 point | **yes** |
| **EESA** | 61% | 1,513 / 504 | 28 / 29 / 42 vs 29 / 30 / 41 | 1 point | **yes, after the S3 filter** |
| AfriSenti Algerian | 91% | 1,492 / 892 | 55 / 19 / 25 vs 50 / 15 / 35 | 10 points | no (S4) |
| AfriSenti Moroccan | 55% | 3,301 / 1,395 | 35 / 29 / 36 vs 23 / 36 / 41 | 12 points | no (S3, S4) |
| ArSen-20 | 81% | no split | 9 / 86 / 4 | – | no (S4, S5: POS 4%) |
| AT-ODTSA | 99% | no split | 28 / 35 / 37 | – | no (S4; targeted sentiment) |

Not measured because they fail S1 or S2: MASC, AJGT, ASTD / ArTwitter / QRCI (binary), Arabic 100k Reviews, LABR and the ATT/HTL/MOV/PROD/RES reviews (star ratings), E_MSA_BDs (ratings, translated), arabic-sentiment-analysis (emoji labels), ALR (aspect level).

**Choice:** Mawqif and EESA are the only downloaded datasets that meet all six standards.
- **Mawqif:** tweets, 100% Arabic script, train and test match within 1 point on every class and within 4 points on links, mentions and hashtags. Narrow in subject (COVID-19 vaccine, digital transformation, women's empowerment).
- **EESA:** Egyptian YouTube comments; 39% are mostly Latin script and are removed by S3, leaving 1,513 / 504 texts that are still stratified (1-point label gap). The remaining texts still contain English words (code-switched), which our generation does not produce (D-010).
- **ASAD** (added 2026-10-31, `data/datasets/sa/official_ASAD.csv`) fails S6: the official file holds only tweet IDs and labels (100,000 tweets, Neutral 69% / Positive 15% / Negative 15%), no text. Getting the text would mean hydrating the IDs through the paid X API (zero-cost rule), and deleted tweets would be lost.
- **SDTC** is not downloaded, so it is not checked yet (TODO: source to be identified).

**Before using them:** Mawqif (train and test) and EESA (all splits) are in the universal topic pool (D-018). If one becomes an evaluation set, its test split has to leave the pool and the topic list has to be refitted (D-011: evaluation data is never in a topic pool).



## MYC (Moroccan YouTube Corpus), Jbel et al.
### What it is
- Source: YouTube comments posted 2018–2022 on 50 well-known Moroccan channels, which native speakers hand-picked to cover different topics.
- Size and balance: 20,000 comments, 10,000 positive and 10,000 negative, with each class split evenly between Arabic script and Latin script. That leaves about 10,000 comments in Arabic script.
- Dialect: Moroccan only (Darija). Comments written entirely in French or English were removed.
- Split: the paper doesn’t describe a train/test split.
- Link: https://github.com/MouadJb/MYC. 

### Procedure

- The paper publishes no annotation guidelines. It describes only the procedure:
- Five native Moroccan annotators labelled each comment as positive or negative. Two of them were experts in social-media project management.
- A comment’s class needed 4 of 5 votes. The paper doesn’t say what happened to comments below that threshold; presumably they were dropped, which would mean only easy, clear-cut comments remain.
- No agreement metric is reported: no kappa and no agreement percentage.

### Verdict (possible usages):

- Steering goal 1 (boost under-represented dialects). Use MYC’s Arabic-script rows as the Moroccan reference set. They can be seed examples for generating Maghrebi text, and a check on whether the synthetic Moroccan actually sounds Moroccan (dialect fidelity). This fits better than mixing it into training.
- Separate cross-dialect test. Evaluate your ArSarcasm-trained model on MYC’s positive and negative rows only, and report it separately. It shows whether synthetic Maghrebi data improves Moroccan performance, without touching the ArSarcasm-v2 comparison.


## MAC (Moroccan Arabic Corpus)

### What it contains
	
- Size	18,000 tweets, chosen from 36,114 collected
- Language	9,640 MSA + 8,360 Moroccan dialect. Only 46% is Darija. The type column in the CSV is this MSA/DA label, and 8,360 is the figure the MYC paper quoted.
- Period	1 Jan – 27 Apr 2021
- Collection	Streaming API filtered to Morocco (8,975 tweets); timelines of 29 very active Moroccan accounts (5,371); about 950 trending Moroccan hashtags (3,654)
- Users	2,354 distinct users
- Retweets	4,076 (22.6%), so likely duplicates. Deduplicate before splitting.
- Labels	Positive / Negative / Neutral / Mixed. Mixed is 643 tweets (per Atlas-Chat); drop it to get 3 classes.
- Class counts	Only shown in a figure, never as numbers. Count them from the CSV.
- Split	None. They used 5-fold stratified cross-validation.
- Link	https://github.com/LeMGarouani/MAC

### Annotation: the weak point
- The two annotators were the authors themselves. They’re native speakers, but they also designed and promoted the dataset.
- Only 2,500 tweets (13.9%) were labelled by both. That was a practice round to get familiar with the task. The other ~15,500 tweets were each labelled by one person only.
- The agreement figure is inconsistent. The abstract says 0.9; Section 3.2 says 0.97. Neither says which measure it is (kappa or plain percent agreement), and it covers only the 2,500 practice tweets, not the labels you’d actually use.
- No guidelines published. Labelling was done in a web app they built; there’s no definition of positive, negative or neutral.

### For 08_DATASET_RATING:
| Field | Value |
|---|---| 
| Annotation error | Not reported |
| IAA | 0.97 (body) / 0.9 (abstract), metric unnamed, measured on 2,500 double-labelled tweets |
| Method of labelling |	2 authors; 86% single-annotated |
| Trustworthiness | about 2/5 |

### Verdict (possible usages):
- Better than MYC to add to ArSarcam-V2
- But very unstrustworthy for a dataset