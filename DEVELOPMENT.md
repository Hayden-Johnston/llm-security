# Detection research and production roadmap

## Current scope and priorities

The current pipeline establishes untuned classifier baselines. Detection quality
should be developed before the proxy or a public frontend. The intended execution
model is one thread per provider, with models on each provider evaluated serially.
Keep that scheduling policy explicit in configuration and run metadata.

First make failed or incomplete experiments unmistakable, then freeze evaluation
inputs and develop classification questions. Build production enforcement after
the detection tradeoffs are understood.

## Developing classification questions

### Define the decision before tuning the wording

Choose an initial protected application, such as a document-answering assistant
that must not follow instructions embedded in retrieved documents. Define:

- The legitimate task and authorized instructions.
- Attacker-controlled inputs: user messages, documents, tool results, or history.
- Protected assets and prohibited outcomes, such as unauthorized tool use or disclosure.
- The action associated with each outcome: allow, block, escalate, or unavailable.
- Acceptable false-positive rates, latency, and classifier-call budgets.

Distinguish prompt injection from harmful content, ordinary instructions, and
quoted discussions of attacks. Document label rules and how ambiguous examples
are adjudicated. A suspicious phrase alone does not establish an attack.

### Preserve context and provenance

Provide the detector with the legitimate task, source role and trust level, and
the candidate content in distinct fields where supported. Delimiters aid
interpretation but do not establish an enforceable security boundary.

Split documents along meaningful boundaries while retaining source IDs, offsets,
and surrounding context. Evaluate overlap, instructions spread across chunks,
long benign documents, and truncation behavior. Record what text the classifier
actually received. Measure document-level false positives as document length and
chunk count increase; chunk-level metrics alone are insufficient.

### Compare question designs experimentally

Retain the current broad question as a baseline. Candidate decomposed questions
can ask whether untrusted content attempts to:

- Override the authorized task or claim higher instruction authority.
- Induce disclosure of protected information.
- Redirect tool use, destinations, or other actions beyond the authorized task.

Specify how answers combine into a decision before evaluating them. These are
hypotheses to test, not established improvements. Avoid questions that require
context the detector has not received. Include benign examples containing quoted
attacks, security documentation, code, and legitimate changes to a user's request.

Version exact question text, context construction, model configuration, score
meaning, thresholds, and answer aggregation. Do not assume scores from different
models or questions have equivalent calibration. Choose thresholds on development
data, then freeze the policy for final evaluation.

### Develop deterministic gates and escalation

Use deterministic checks for explicit policy constraints and signals that route
content to further inspection. Evaluate the security consequences of every
short-circuit path. The absence of a keyword should not automatically establish
that content is safe.

Compare rules alone, a single classifier, rules plus classifier, decomposed
questions, context chunking, and escalation on identical examples. Measure recall
at comparable false-positive rates, legitimate task completion, calls per request,
and latency. Additional calls must demonstrate a useful improvement.

Record gate decisions, question versions, scores, thresholds, escalation reasons,
and final actions. Test attacks aimed at manipulating the detector's verdict and
inputs deliberately designed to trigger expensive escalation. Bound decoding,
chunk counts, input sizes, and additional calls.

## Publication requirements

### Reproducible inputs and execution

- Freeze dataset revisions, splits, example IDs and content hashes. Compare models
  on the same examples; clearly label partial or exploratory comparisons.
- Record model artifact revisions, quantization, serving version, inference
  settings, context limits, hardware, concurrency, and timing methodology.
- Record the code commit and dirty state, dependency lock, complete effective
  configuration, question versions, thresholds, and routing policy.
- Preserve immutable raw scores and per-example outcomes with schema versions.
  Record expected, attempted, successful, failed, and excluded example counts.
- Record start/end times and explicit complete, failed, or interrupted run status.
  Never infer completion solely from the presence of a results file.

### Evaluation discipline

Keep development and final test data separate. Question changes, routing changes,
and threshold tuning belong on development data. Repeated inspection and tuning
against a test set consumes its independence.

Audit label definitions, duplicates, overlap across datasets, source concentration,
and attack-family coverage. Group related attack variants when splitting and
estimating uncertainty. Review synthetic examples and record generator provenance.
Describe unknown model training overlap rather than claiming it has been ruled out.
Check dataset licenses and redistribution terms before publishing examples.

Include representative benign traffic and hard negatives, multilingual and long
inputs, obfuscation, indirect injection, multi-turn attacks where in scope, and
attacks crossing chunk boundaries. Publish the scope and unsupported cases.

### Metrics and artifacts

Report confusion counts, recall, FPR, precision, FNR, threshold curves, uncertainty
intervals, and per-source or attack-family breakdowns. State whether rates are
fractions or percentages and define undefined metrics explicitly. Precision and
false discovery rate are undefined if the detector predicts no positives, even
when the dataset contains both classes.

Report coverage and failure rates separately from detection accuracy. Declare
exclusions and denominator policies. For model comparisons use paired examples;
for incomplete runs report coverage rather than presenting aggregate results as
a complete ranking. Use uncertainty methods appropriate to related examples.

Report end-to-end latency percentiles, throughput, calls per request, and cost or
resource usage under specified load. Explain how benchmark prevalence differs
from expected deployment prevalence and how that changes precision.

Include a sandboxed protected application with synthetic assets and tools.
Compare attack success and legitimate task completion with and without the
defense; classifier labels alone do not establish application protection.

Publish a reproducible command, manifest, metric definitions, raw results where
permitted, controlled ablations, representative error analysis, and limitations.
An effective initial report would test whether context-aware routing improves
recall at a fixed false-positive and resource budget.

## Production readiness

### Experiment runner: first priority

Propagate provider failures to the main process and return a nonzero exit status.
Joining a raw thread waits for it but does not re-raise its exception. Futures with
explicit result collection are one option. Define whether other providers finish
or are cancelled, and preserve provider-level outcomes either way.

Support durable checkpoints and resume without silently omitting or duplicating
examples. Record request errors and attempts separately; timeouts are not benign
classifications. Use bounded retries for appropriate transient errors, explicit
timeouts, and bounded concurrency. Validate score ranges and returned identity.

Use collision-resistant run identity or atomic allocation. Distinct model files
within one launch are separate from the risk of two processes allocating the same
run directory. Namespace outputs by provider and model if model names can repeat.

Make configuration control actual behavior. Keep manifests aligned with execution.
Version metric computation and support explicit regeneration: the current
measurement script skips any run whose measurements.json already exists, so
updated formulas do not automatically update saved output.

Add meaningful tests for metric calculations, undefined metrics, configuration,
sample identity, worker exception propagation, partial results, checkpoint/resume,
and result validation. Add a small local integration test with a controlled fake
HTTP server. Verify installation and the CLI in a clean environment in CI.

### Proxy and enforcement

Define fail-open, fail-closed, or degraded behavior per protected operation when
detection is unavailable. Implement request deadlines, overload handling, bounded
queues, cancellation, rate limits, and resource budgets.

Authenticate callers, isolate tenants and credentials, and protect network traffic.
Define retention, access, and redaction for sensitive prompts and traces. Treat
stored attack text as untrusted when rendering it in review interfaces.

Enforce tool permissions, destination restrictions, and authorization independently
of classifier scores. A detector can reduce risk without being the sole barrier
protecting secrets or privileged actions.

Monitor latency, errors, coverage, decision distribution, escalation volume, and
false-positive reports. Version policy changes, support rollback, and introduce
enforcement through shadow evaluation and controlled rollout. Define ownership
for incidents, drift review, and disputed decisions.

### Frontend

Start with an experiment-review interface: compare compatible runs, inspect false
positives and negatives, show coverage and uncertainty, and trace decisions through
gates and classifiers. Add publication dashboards after the underlying artifacts
and comparisons are reliable.

## Reference

OWASP's prompt injection prevention guidance covers indirect injection, layered
controls, least privilege, and evaluation of protected outcomes:
https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
