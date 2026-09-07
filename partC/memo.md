# Tokenizer Fertility Audit — Routing Recommendation

## Executive Finding

The original benchmark substantially overstated the tokenization cost of Indic languages because it used GPT-2, an English-oriented tokenizer. On the corrected 997-sentence FLORES-200 evaluation corpus, GPT-2 required 7.45× as many tokens for Hindi, 15.43× for Tamil, and 13.59× for Kannada relative to English.

Using the multilingual XLM-R tokenizer, the same ratios fell to 1.26×, 1.35×, and 1.37× respectively. This shows that the large apparent language penalty was primarily a tokenizer/model-vocabulary mismatch rather than an inherent property of the languages.

## Corrected Headline Numbers

| Language | GPT-2 tokens | GPT-2 vs English | XLM-R tokens | XLM-R vs English |
|---|---:|---:|---:|---:|
| English | 25,741 | 1.00× | 28,995 | 1.00× |
| Hindi | 191,828 | 7.45× | 36,634 | 1.26× |
| Tamil | 397,163 | 15.43× | 39,088 | 1.35× |
| Kannada | 349,772 | 13.59× | 39,602 | 1.37× |

These counts cover the same 997 parallel sentences for each language.

## Routing Recommendation

Do not route or budget requests based on language identity alone. Instead, use a tokenizer/model pair with multilingual coverage such as XLM-R for multilingual traffic and estimate cost from actual token counts.

For comparative routing analysis, the primary metric should be **tokens per parallel sentence**, because the evaluation corpus is aligned across languages and token count directly represents model input burden. Tokens/word and tokens/byte should remain diagnostic metrics rather than the primary routing signal.

## Biggest Caveat

FLORES-200 is a multilingual machine-translation benchmark derived from web content, so these results may not represent production traffic such as conversational text, code-switching, informal spelling, very long prompts, or domain-specific terminology. The tokenizer comparison should therefore be repeated on representative production traffic before making a final routing policy.

## Production Metric

Monitor **p95 input tokens per request by language and tokenizer route**. In the XLM-R evaluation, mean tokens per sentence ranged from 29.1 to 39.7, while p95 ranged from 47 to 65 tokens, demonstrating that average token counts can hide substantially larger requests.