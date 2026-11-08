## Methods and general plan
### Two points from the literature to carry over:

1. Elozeiri found neuron steering only strengthens a property that is already there; it failed when starting from the wrong dialect. So keep the class in the prompt for neuron runs, and judge them against a prompt-only baseline as well as SR01.
2. As in the vector plan, compare each set against a same-size unsteered generation (e.g. SG02), not just SR01. Otherwise any gain could come from adding more data, not from steering.


### how the best layers were chosen
1. Method 1
    - Search every layer below 0.8 of depth; don’t fix one in advance. In the refusal paper the best layer ranged from 0.26 to 0.78 of depth.
    - Read activations at the last token or at clause-ending punctuation, in middle layers. Both Geometry of Truth and the refusal paper read them there.
    - Selection rule (refusal paper):
        - Keep a candidate only if adding it produces the property on its own.
        - Keep it only if KL divergence on neutral prompts stays below 0.1.
            - KL (decided 2026-11-08): how much steering changes the model's next-word probabilities (0 = no change). Neutral prompts = ordinary requests with no sentiment in them (`prompts/sentiment/kl_neutral_v1.json`). The direction is added at the response start, as in generation; KL is averaged over the prompts and the three class vectors. Overhead: about 15 min for all three generators (forward passes only, no generation), next to about 3 h for the layer screen.
        - Choose using a separate validation set.
    - Alpha for the layer search (decided 2026-11-08): first a short calibration on one middle layer per generator (about half depth: Fanar 21, Qwen3 18, Aya 16), alpha 0.1, 0.2, 0.4 and 0.8 × the layer's typical size, 156 texts each plus the unsteered baseline (about 30 min for all three generators). Use the smallest alpha that clearly moves the class (gain over the baseline with its lower 95% bound above 0) for every layer in the search.
2. Method 2
    - Read the tweets: each generator reads all 11,171 S1 train tweets once, with no generation.
    - Average over tokens: at every layer, I average each tweet's internal state over all its tokens. Only every second layer was saved (0, 2, 4…).
    - Keep non-sarcastic tweets: 9,255 tweets, the groups the vectors are built from.
    - Split into 5 folds: 4/5 to build, 1/5 to test, repeated so each tweet is tested once.
    - Build: on the 4 building folds, make the POS, NEG and NEU directions at each saved layer (class minus the other two, inside each dialect, then averaged).
    - Test: project the held-out tweets onto each direction, then measure separation.
    - Drop layers: layer 0 (word embeddings) and the last layer (normalised output) are left out.
    - Score: for each class, Cohen's d on held-out tweets: how far apart the class and the rest sit along its own direction.
    - Pick: the layer with the highest d, separately for each class.
    - Combine: each generator's list is the set of its classes' best layers.


### Sentiment Neuron Steering Generation 

##### Neuron Stering technuiques
- LAPE neuron steering: you choose class-specific neurons by activation entropy and change only those (Tang 2024; recipe from Elozeiri 2026: top 5% activation probability for at least one class AND bottom 1% LAPE).
- AP neuron steering: you choose neurons by average precision (Kojima 2024: top-1000 and bottom-1000 neurons by AP of each neuron's per-text mean activation) and compare the result against LAPE.
- Selection data: non-sarcastic S1 train tweets only. Test set never used.
- Every run: count-matched (500 per variety × sentiment cell), class named in the prompt, compared against SR01 (real only) AND a same-size unsteered prompt-only set (SG02).
- Comparisons for every SNG and SVG run (decided 2026-11-08): SR01 (real only), the SG01 runs of the same generator (SR02, zero-shot prompt only, same size) and the best SG02 run (SR04 Qwen3, few-shot, the best unsteered set on dev).
##### Vector steering prompting
- Prompt only (no steering): baseline (SG01/SG02).
- Without the sentence (DiffMean): same prompt minus the sentiment line; the vector alone makes the tweet negative. → control: proves the vector carries sentiment.
- With the sentence (Prompt + DiffMean): the prompt asks for negative and the vector pushes towards negative. → main condition, lower α; expected to help most on weak classes and phenomena (NEU, sarcasm).

##### Neuron steering prompting
- Prompt only (no steering): baseline (SG01/SG02).
- Without the sentence (Neurons): same prompt minus the sentiment line; class neurons alone. → small control, expected to fail (Elozeiri: neurons reinforce, cannot induce).
- With the sentence (Prompt + Neurons): the prompt asks for negative and the NEG neurons are amplified. → main condition, low α (Fanar 2–4).

#### Sentiment Neuron Steering Generation
- SNG01. Three generators will generate all three classes, each request steered by its own class's neurons selected by **LAPE** (paper recipe): POS requests use POS neurons, NEU requests NEU neurons, NEG requests NEG neurons. Amplify ×α, with α tuned per class in a small generation test (Fanar starts at α = 4 from Elozeiri; Qwen3 and Aya swept; SR01 judge + diversity + fluency). One balanced set of 6,000 per generator.
- SNG02. same as SNG01 but neurons selected by **AP** (top/bottom 1,000).
- SNG03. **matched count**: LAPE and AP keep the same number of neurons per class.
- SNG04. **random control**: same count and layer spread, random neurons.
- SNG05. best selection method, strength scaled.
- SNG06. same as SNG05 but suppress the other classes' neurons.
- SNG07. same as SNG05 but neuron count scaled (1% / 3% / 5%).
- SNG08. controlling topic, lexical diversity, sentiment diversity and fidelity from the best combo so far.

Combined (exploratory, no published precedent)
- SNVG13. best vector setting (SVG) + best neuron setting (SNG) together. compare against each alone.

### Sentiment Vector Steering Generation 

- DiffMean.sur you add a direction, the difference of mean activations between two groups of texts, to the residual stream.
- Steering-vector variants (ActAdd, CAA, RepE, Style Vectors): other published ways to build and apply steering directions, which we read as background.


- SVG01. Three generrunsators will generate by steering at the best layer for POS. Layers are chosen by **Method 1**. compare against SR01, real only. 
- SVG02. same as SVG01 but for NEU.  
- SVG03. same as SVG01 but for NEG. 
- SVG04
- SVG04 use the Best preforming out the of (SVG01-03) for each generator strength scaled. compare with the best out the 3 generations.
- SVG05 same as SVG04 but balanced strength
- SVG06 controlling the topic, lexical diversity, sentiment diveristy and fidelity from the best combo from the last 5 generations to see which one it better


## SV01
The Generators passed over the ArSarcasm-V2 dataset as if it has generated it to find the neurons activated and the vector directions for it


