# AI Usage

AI tools were used as an engineering and research assistant throughout the
assessment.

## How AI was used

- Break the assignment into A1–A4, B1–B4 and C tasks.
- Identify candidate bugs, conceptual issues and suspicious-looking code.
- Suggest controlled experiments and comparison designs.
- Help interpret measured deltas and organize the audit trail.
- Help structure the final memos and documentation.
- Help reason about alternative tokenizers, denominators and routing metrics.

## What I personally validated

I executed the commands locally, installed missing dependencies, inspected
errors, prepared and verified the corpus, ran the tokenizer experiments, and
checked the numerical outputs used in the final conclusions.

The final findings were accepted only when they were supported by measured
results from the supplied data or by calculations directly derived from the
model specification/load-test log.

## Example of AI-assisted hypothesis rejection

A fixed random seed initially looked suspicious because the benchmark does not
use randomness in its analysis. Instead of calling it a bug, I tested it.
Removing/resetting the random state produced zero change in the measured
metrics, so the final assessment explicitly classifies it as harmless/redundant.

Similarly, the original hypothesis that Indic tokenization difficulty was
inherent to the languages was not accepted without testing. The multilingual
XLM-R comparison substantially reduced the observed language inflation, so the
final explanation was revised toward tokenizer/model-vocabulary mismatch.

## Principle

AI suggestions were treated as hypotheses, not evidence. Measurements from
the repository and reproducible calculations determined the final claims.
