# Audit Notebook — The Audit

## Purpose

This notebook records the audit as a chronological engineering trail:
**hypothesis → experiment → result → interpretation → revision**.

The objective was to test the claims in `REPORT_v0.md` rather than accept its
numbers at face value. Material findings were isolated with controlled
experiments and measured on the same evaluation corpus.

---

# A0. Starting Point

The starter kit contained:

- `fertility.py` — tokenizer fertility benchmark
- `REPORT_v0.md` — previous tokenizer and serving conclusions
- `corpus_sample/` — small English/Hindi smoke-test corpus
- `bench/model_spec.md` and `bench/bench_log.csv` — serving configuration and load-test data

The initial report made strong cross-language and serving claims without the
level of evidence required by the assignment. I therefore froze the original
measurements first, then changed one factor at a time.

---

# A1. Evaluation Corpus

## A1.1 Corpus Selection

### Hypothesis
The supplied ~10-sentence sample is insufficient for a robust multilingual
comparison. A parallel corpus containing English, Hindi and two Dravidian
languages provides a stronger basis.

### Experiment
Selected the FLORES-200 `dev` split for:

| Language | Code | Sentences |
|---|---|---:|
| English | `eng_Latn` | 997 |
| Hindi | `hin_Deva` | 997 |
| Tamil | `tam_Taml` | 997 |
| Kannada | `kan_Knda` | 997 |
| **Total** | | **3,988** |

Preparation script: `Part-A/prepare_corpus.py`

### Execution / dead ends
1. `python partA/prepare_corpus.py` failed because the project directory was
   named `Part-A`.
2. `python Part-A/prepare_corpus.py` downloaded/extracted the corpus but hit
   `FileExistsError` because `Part-A/corpus` already existed.
3. Re-running after inspecting the existing output path completed successfully.

### Preprocessing
UTF-8 decoding, empty-line removal, leading/trailing whitespace removal and
Unicode NFC normalization. Internal whitespace and punctuation were retained;
no translation, tokenization or language-specific rewriting was performed.

### Caveat
FLORES-200 is a multilingual machine-translation benchmark rather than a
production traffic sample. It does not fully represent conversational text,
informal spelling, code-switching, very long prompts or domain-specific traffic.

## A1.2 Corpus Verification

### Hypothesis
Each generated file should contain exactly 997 non-empty readable sentences.

### Experiment
`Part-A/verify_corpus.py`

Command:
`python Part-A/verify_corpus.py`

### Result
English, Hindi, Tamil and Kannada each passed with **997 sentences and 0 empty
lines**, giving **3,988 verified sentences**.

### Decision
The corpus passed structural checks and was retained unchanged for the audit.

---

# A2. Audit of `fertility.py`

## A2.1 Establish Original Baseline

### Hypothesis
The original script should produce a reproducible baseline on the new corpus.

### Environment
`tiktoken` was initially missing.

Command:
`python -m pip install tiktoken`

Verified version: `0.14.0`.

### First execution
The original benchmark failed with:
`ModuleNotFoundError: No module named 'tiktoken'`.

This was an environment issue, not a benchmark flaw. No measurement was taken
from the failed run.

### Successful baseline
Command:
`python fertility.py --corpus eng=Part-A/corpus/eng.txt --corpus hin=Part-A/corpus/hin.txt --corpus tam=Part-A/corpus/tam.txt --corpus kan=Part-A/corpus/kan.txt --tokenizer gpt2`

| Language | Fertility | Tokens/char | vs English |
|---|---:|---:|---:|
| English | 1.28 | 0.215 | 1.00× |
| Hindi | 7.82 | 1.528 | 6.10× |
| Tamil | 24.73 | 2.717 | 19.28× |
| Kannada | 22.15 | 2.655 | 17.27× |

These values were frozen as the original baseline.

---

## A2.2 Finding 1 — `split(" ")` Is a Measurement Bug

### Hypothesis
`line.split(" ")` can count repeated spaces as empty words, changing the
fertility denominator.

### Experiment
Compared `split(" ")` with `split()` while holding the corpus, tokenizer,
normalization, lowercasing, character count and averaging method constant.

Script:
`Part-A/experiments/a2_split_spaces.py`

Command:
`python Part-A/experiments/a2_split_spaces.py`

### Result

| Language | Before | After | Delta | Relative delta |
|---|---:|---:|---:|---:|
| English | 1.282531 | 1.282579 | +0.000048 | +0.0037% |
| Hindi | 7.823186 | 7.825973 | +0.002787 | +0.0356% |
| Tamil | 24.733182 | 24.866899 | +0.133717 | +0.5406% |
| Kannada | 22.148288 | 22.945631 | +0.797342 | +3.6000% |

Tokens/character was unchanged.

### Interpretation
The bug is real and measurable, but it is too small to explain the original
large Indic-vs-English gap.

### Revision
Use whitespace-aware `split()` for word counting.

---

## A2.3 Finding 2 — Per-Sentence Averaging Is the Wrong Aggregate Cost Metric

### Hypothesis
The existing calculation gives every sentence equal weight. For corpus-level
cost estimation, `total_tokens / total_words` is more representative.

### Experiment
Compared the mean of sentence-level fertility ratios with aggregate
`total_tokens / total_words`, using `split()` in both calculations.

Script:
`Part-A/experiments/a2_aggregation.py`

Command:
`python Part-A/experiments/a2_aggregation.py`

### Result

| Language | Sentence mean | Aggregate | Delta |
|---|---:|---:|---:|
| English | 1.282579 | 1.274029 | -0.6666% |
| Hindi | 7.825973 | 7.796237 | -0.3800% |
| Tamil | 24.866899 | 24.618136 | -1.0004% |
| Kannada | 22.945631 | 22.670253 | -1.2001% |

### Interpretation
The original code computes exactly the arithmetic mean it claims to compute.
The conceptual problem is using that equal-weight sentence statistic as a
proxy for aggregate serving cost.

### Revision
Keep sentence-level averages as descriptive statistics, but use token counts
with an explicitly fixed unit (parallel sentence for this audit, actual
input tokens/request in production) for routing and cost decisions.

---

## A2.4 Finding 3 — Forced Lowercasing Changes the Measurement

### Hypothesis
`line.lower()` may alter GPT-2 tokenization and therefore distort comparison.

### Experiment
Compared lowercased versus original casing while keeping the corpus,
tokenizer and other preprocessing identical.

Script:
`Part-A/experiments/a2_lowercase.py`

Command:
`python Part-A/experiments/a2_lowercase.py`

### Result

| Language | Fertility change from lowercasing | Relative change |
|---|---:|---:|
| English | -0.045871 | -3.5765% |
| Hindi | -0.000642 | -0.0082% |
| Tamil | -0.001776 | -0.0071% |
| Kannada | -0.001751 | -0.0076% |

Tokens/character showed the same pattern: about -3.50% for English and less
than 0.01% for the Indic languages.

### Interpretation
Lowercasing is not a universal bug, but it is a preprocessing-induced
measurement change. It matters materially for English in this audit and can
therefore affect cross-language ratios.

### Revision
The corrected analysis preserves original corpus casing.

---

## A2.5 Suspicious-Looking but Actually Fine — `random.seed(1337)`

### Hypothesis
The fixed seed looks unnecessary because the benchmark performs no random
sampling.

### Experiment
Compared benchmark results with the fixed seed against a reset/random state.

Script:
`Part-A/experiments/a2_random_seed.py`

Command:
`python Part-A/experiments/a2_random_seed.py`

### Result
Fertility and tokens/character were identical for all four languages; every
measured delta was **0.000000**.

### Interpretation
The seed is redundant but harmless. It does not change the reported result.

### Revision
Do not classify it as a bug.

---

# A3. Corrected Cross-Language Analysis

## A3.1 Tokenizer Comparison

### Hypothesis
A multilingual tokenizer can behave very differently from GPT-2 on Indic
scripts, so the original language penalty may be tokenizer-specific.

### Experiment
Compared GPT-2 with `xlm-roberta-base` using original casing and whitespace-aware
word counting.

Script:
`Part-A/experiments/a3_tokenizer_comparison.py`

Command:
`python Part-A/experiments/a3_tokenizer_comparison.py`

### Result

| Language | GPT-2 tokens | GPT-2 tok/word | XLM-R tokens | XLM-R tok/word |
|---|---:|---:|---:|---:|
| English | 25,741 | 1.228 | 28,995 | 1.384 |
| Hindi | 191,828 | 7.796 | 36,634 | 1.489 |
| Tamil | 397,163 | 24.617 | 39,088 | 2.423 |
| Kannada | 349,772 | 22.668 | 39,602 | 2.567 |

GPT-2 language inflation relative to English:
- Hindi: **7.45×**
- Tamil: **15.43×**
- Kannada: **13.59×**

XLM-R language inflation:
- Hindi: **1.26×**
- Tamil: **1.35×**
- Kannada: **1.37×**

### Interpretation
The large original Indic penalty is not an inherent property of the languages.
It is strongly dependent on tokenizer/model vocabulary coverage. XLM-R reduces
the observed Indic inflation dramatically.

### Revision
Routing should not use language identity as a proxy for tokenization cost when
the tokenizer/model pair has not been specified.

---

## A3.2 Denominator Comparison

### Hypothesis
No single linguistic denominator is equally meaningful across all scripts.
Compare multiple normalized views.

### Experiment
Script:
`Part-A/experiments/a3_routing_metric.py`

Command:
`python Part-A/experiments/a3_routing_metric.py`

Measured:
1. tokens / whitespace word,
2. tokens / UTF-8 byte,
3. tokens / parallel sentence.

### Result

XLM-R:

| Language | tok/sentence | tok/word | tok/byte |
|---|---:|---:|---:|
| English | 29.082 | 1.384 | 0.231 |
| Hindi | 36.744 | 1.489 | 0.114 |
| Tamil | 39.206 | 2.423 | 0.098 |
| Kannada | 39.721 | 2.567 | 0.111 |

The 997 sentences are aligned across languages, so parallel sentence count holds
the evaluation unit constant without assuming equivalent word or byte
segmentation.

### Decision
For this cross-language audit, **tokens per parallel sentence** is the single
primary comparison number.

For actual production cost, the direct quantity is **input tokens per request**
for the deployed tokenizer/model pair; the audit metric is a controlled
cross-language proxy, not a billing formula.

---

## A3.3 Tail Behaviour

### Hypothesis
Mean tokens per sentence can hide large requests that matter for serving.

### Experiment
Script:
`Part-A/experiments/a4_variability.py`

Command:
`python Part-A/experiments/a4_variability.py`

### Result with XLM-R

| Language | Mean | Median | P95 | Max tokens/sentence |
|---|---:|---:|---:|---:|
| English | 29.1 | 28 | 47 | 76 |
| Hindi | 36.7 | 35 | 60 | 99 |
| Tamil | 39.2 | 37 | 65 | 94 |
| Kannada | 39.7 | 38 | 65 | 96 |

### Decision
A production dashboard should monitor **p95 input tokens/request by language
and tokenizer route**, rather than relying only on the mean.

---

# B. Capacity Reconciliation

The serving report was audited against `bench/model_spec.md` and
`bench/bench_log.csv`.

## B1. KV-cache capacity

### Hypothesis
The model specification should predict the order of the observed long-context
capacity limit.

### Calculation

KV bytes/token:

`2 × layers × KV heads × head_dim × bytes_per_fp16`

`= 2 × 28 × 8 × 128 × 2`

`= 114,688 bytes/token`

For a 4096-token sequence:

`114,688 × 4096 = 469,762,048 bytes`

≈ **448 MiB per sequence**.

Available memory under the stated assumptions:

`24 GB × 0.92 - 1.6 GB = 20.48 GB`

Approximate concurrent 4096-token sequences:

`20.48 GB / 469,762,048 bytes ≈ 43.6`

So the estimate is **about 43 full 4096-token sequences**.

### Log check
The long-context sweep reaches `kv_cache_util = 0.93` at batch 24, then
`0.97` at batches 32 and 48. Preemptions begin at batch 32 (7 sequences) and
increase to 23 at batch 48. This is consistent with the predicted KV-capacity
boundary.

---

## B2. Long-context throughput anomaly

### Hypothesis
If throughput scaled normally with batch size, increasing batch from 24 to 32
to 48 should continue increasing useful throughput.

### Evidence
For prompt length 3584 and generation length 512:

| Batch | Reported tok/s | Preempted | KV util |
|---:|---:|---:|---:|
| 24 | 1607.4 | 0 | 0.93 |
| 32 | 1384.0 | 7 | 0.97 |
| 48 | 1298.5 | 23 | 0.97 |

Increasing batch beyond 24 **reduces** the reported throughput while preemption
appears.

### Interpretation
The workload is crossing the KV-cache capacity boundary. Scheduler
preemption/recomputation overhead offsets the expected batching gain.

### Proposed deployment change
For 3584-token prompts, cap the batch at **24** (or dynamically lower it as
prompt length increases). Using the observed data as the prediction, batch 24
delivers 1607.4 reported tokens/s versus 1384.0 at batch 32 and 1298.5 at batch
48: approximately **16% higher than batch 32 and 24% higher than batch 48**.

This is an evidence-backed prediction from the existing sweep, not a claim that
a new configuration has already been benchmarked.

---

## B3. The report's column misreading

### Problem
`reported_tok_s` counts the full prompt-plus-generation token workload. It is
not generated/decode-only throughput.

For the batch-24 long-prompt row:

`reported_tok_s = 1607.4`

Prompt + generation = `3584 + 512 = 4096` tokens/request.

Generated-token goodput from wall-clock time:

`24 × 512 / 61.16 = 200.9 generated tok/s`

Independent derivation from the reported counter:

`1607.4 × (512 / 4096) = 200.9 generated tok/s`

Both methods agree.

### What the report should have said
Longer prompts do **not** demonstrate better generation throughput. The
higher `reported_tok_s` is caused by counting the much larger prompt workload.
The observed batch-24 long-context generation goodput is about **201 generated
tokens/s**.

The claim that batch 48 would deliver ~3200 tok/s is unsupported by the sweep;
the observed reported value is only **1298.5 tok/s**, and it occurs with 23
preempted sequences.

---

## B4. Production counter

### Hypothesis
The B2 mechanism should be visible in a scheduler/KV-cache metric.

### Decision
Pull **KV-cache utilization together with preemption count/rate** from the
serving stack. I would expect utilization to remain near saturation while
preemptions rise sharply once batch size exceeds the safe long-context region:
the provided log already shows 0 preemptions at batch 24/0.93 utilization,
7 at batch 32/0.97, and 23 at batch 48/0.97.

---

# C. Decision-Memo Reasoning

The product scenario asks for casual multilingual responses under one A100 for
two weeks, limited native-speaker review and a three-week launch window.

The selected path is **prompt engineering first**, with a small controlled
evaluation before committing training or a rewriter to production.

## Why

The schedule is too short to make a large synthetic-data/SFT effort the first
move when the problem may be substantially prompt-addressable. A rewriter adds
another inference stage and therefore another latency/capacity dependency.

Prompt engineering also produces a reversible baseline quickly and gives the
team evidence about whether training is actually necessary.

---

# Rejected Hypotheses / Dead Ends

| Hypothesis | Evidence | Decision |
|---|---|---|
| Indic token inflation is inherent to the scripts | XLM-R reduced GPT-2 inflation from 7.45–15.43× to 1.26–1.37× | Reject |
| `split(" ")` explains the huge language gap | Maximum measured effect was 3.60% | Reject as root cause; retain as bug |
| Sentence-level mean is the best aggregate cost metric | Aggregate ratio differed by up to 1.20% | Reject for aggregate cost use |
| Lowercasing is harmless | English fertility changed by 3.58% | Reject; preserve casing |
| `random.seed(1337)` is a bug | All measured deltas were zero | Reject bug classification |
| Longer prompts improve generation throughput | Corrected goodput at batch 16 was ~164 vs ~294 generated tok/s for short prompts | Reject |
| Batch 48 should scale to ~3200 tok/s | Observed reported throughput was 1298.5 with 23 preemptions | Reject |

---

# Final Engineering Decisions

1. Use a real parallel multilingual corpus rather than the supplied toy sample.
2. Treat `split(" ")` as a verified implementation bug.
3. Do not use sentence-level mean fertility as the production cost proxy.
4. Preserve original casing in the corrected audit.
5. Do not blame language/script alone for tokenizer inflation; evaluate the
   tokenizer/model pair.
6. Use tokens per parallel sentence for controlled cross-language comparison.
7. Use actual input tokens/request, especially p95, for production cost and
   capacity monitoring.
8. For long prompts, avoid assuming throughput scales with batch once KV-cache
   utilization approaches saturation.
9. Treat the original report's unsupported conclusions as hypotheses to test,
   not facts.
