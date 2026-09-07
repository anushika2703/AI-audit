# Tokenizer Fertility Audit — Recommendation

## Executive Finding

The original benchmark substantially overstated Indic tokenization cost by
using GPT-2 as its only tokenizer. On 997 parallel FLORES-200 sentences per
language, GPT-2 required **7.45×** as many tokens for Hindi, **15.43×** for
Tamil and **13.59×** for Kannada relative to English.

With multilingual XLM-R, the same ratios fell to **1.26×, 1.35× and 1.37×**.
The large original gap is therefore primarily a tokenizer/model-vocabulary
mismatch, not an inherent property of the languages.

## Corrected Headline Numbers

| Language | GPT-2 tokens | GPT-2 vs English | XLM-R tokens | XLM-R vs English |
|---|---:|---:|---:|---:|
| English | 25,741 | 1.00× | 28,995 | 1.00× |
| Hindi | 191,828 | 7.45× | 36,634 | 1.26× |
| Tamil | 397,163 | 15.43× | 39,088 | 1.35× |
| Kannada | 349,772 | 13.59× | 39,602 | 1.37× |

All four languages contain the same 997 parallel sentences.

## Routing Recommendation

Do not route or budget requests from language identity alone. Evaluate the
actual tokenizer/model pair and use **input tokens per request** for production
cost. For this controlled cross-language audit, **tokens per parallel sentence**
is the best single comparison number because it holds the evaluation unit
constant across languages.

The multilingual tokenizer should be treated as evidence for the tested
language/corpus combination, not as a universal production choice without a
representative workload benchmark.

## Biggest Caveat

FLORES-200 is a machine-translation benchmark derived from web content, not
production traffic. Results may differ for conversational text, code-switching,
informal spelling, long prompts and domain-specific terminology.

## Production Metric

Monitor **p95 input tokens per request by language and tokenizer route**.
In the XLM-R experiment, mean tokens/sentence ranged from 29.1 to 39.7 while
p95 ranged from 47 to 65, showing why mean token count alone can hide tail
workloads.
