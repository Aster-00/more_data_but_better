## Quality rows (for you to review; not written to the Sheet)

| Dataset | Texts | MSA share | Dialectness | MTLD | Topics (of 30) | Universal clusters (of 50) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|
| EESA real (train) | 2,463 | 10.3% | 0.61 | 1,226 | 30 | 14.6 | 3.8 | 0.2% | 89.4% (93 / 80 / 94) |
| SG01-EASA Fanar | 1,320 | 1.6% | 0.77 | 589 | 15 | 6.1 | 3.0 | 0.0% | 84.2% (98 / 55 / 100) |
| SG01-EASA Qwen3 | 1,320 | 2.8% | 0.72 | 216 | 13 | 6.2 | 3.0 | 1.5% | 85.3% (84 / 73 / 99) |
| SG01-EASA Aya | 1,320 | 1.0% | 0.80 | 392 | 9 | 4.6 | 2.5 | 0.0% | 77.5% (100 / 32 / 100) |

The real row's fidelity is the SR01-EASA judge's accuracy on EESA dev; the synthetic rows show how often that judge confirms the requested label.

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

The SG01 sets on ArSarcasm showed the same pattern. SG01 is the open condition, so the prompt stays as it is and these numbers are the result. They tell us what SG03-EASA should control.

## Next
1. **Hard cases:** I build the list of EESA dev comments that most of the 63 SR02-EASA runs get wrong (`hard_cases --corpus eesa`). It takes seconds and needs no GPU.
2. **Your type choice:** you read the list and pick the types for SG03-EASA.
