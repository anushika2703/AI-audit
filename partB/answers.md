# Part B — Capacity Reconciliation

## B1. KV-cache bytes/token

Given:

- layers = 28
- KV heads = 8
- head dimension = 128
- KV precision = FP16 = 2 bytes
- one K and one V tensor

Therefore:

`2 × 28 × 8 × 128 × 2 = 114,688 bytes/token`

For 4096 tokens:

`114,688 × 4096 = 469,762,048 bytes`

= **448 MiB per 4096-token sequence**.

Available memory under the supplied assumptions:

`24 GB × 0.92 − 1.6 GB = 20.48 GB`

Approximate full 4096-token sequences:

`20.48 GB / 469,762,048 ≈ 43.6`

So the expected maximum is approximately **43 concurrent full-length sequences**.

The load test supports the capacity boundary: at prompt length 3584,
KV-cache utilization is 0.93 at batch 24, 0.97 at batch 32 and 0.97 at batch
48. Preemptions appear at batch 32 (7) and rise to 23 at batch 48.

---

## B2. Long-context anomaly

For prompt 3584 / generation 512:

| Batch | Reported tok/s | Preempted | KV util |
|---:|---:|---:|---:|
| 24 | 1607.4 | 0 | 0.93 |
| 32 | 1384.0 | 7 | 0.97 |
| 48 | 1298.5 | 23 | 0.97 |

Increasing batch beyond 24 decreases throughput because the KV cache is near
capacity and scheduler preemption begins.

**Deployment change:** cap long-context batch at 24 or dynamically lower batch
as prompt length increases. Based on the measured sweep, batch 24 is about
16% better than batch 32 and 24% better than batch 48 in reported throughput.

---

## B3. Reported throughput vs honest goodput

The harness's `reported_tok_s` counts prompt + generation tokens.

For batch 24:

`24 × 512 / 61.16 = 200.9 generated tok/s`

Independent check:

`1607.4 × (512 / (3584 + 512)) = 200.9 generated tok/s`

Therefore the honest generation goodput is **~201 generated tokens/s**.

The report's claim that longer prompts provide better throughput is a
counter-metric error: long prompts contain many more prompt tokens, inflating
the reported total-token rate.

The batch-48 recommendation is also unsupported: the observed value is
1298.5 reported tok/s with 23 preempted sequences, not ~3200 tok/s.

---

## B4. Counter to pull

Pull **KV-cache utilization together with scheduler preemption count/rate**.
If the proposed mechanism is correct, utilization should be near saturation
and preemptions should rise once the safe long-context batch is exceeded. The
provided data already show 0 preemptions at batch 24/0.93 utilization, 7 at
batch 32/0.97 and 23 at batch 48/0.97.
