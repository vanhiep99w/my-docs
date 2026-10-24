# Doc-type structure templates

Use these as starting shapes, not a section quota. Match the host's frontmatter/H1/TOC conventions and choose only components that teach something. Read `docs-kit-components.md` for the selected feature's integration and descriptor example; keep essential reasoning in prose around viewers.

## Architecture / design

1. **Problem and context:** user-visible pain, scope and evidence.
2. **Goals and non-goals:** invariants and deliberately excluded work.
3. **System overview:** D2 diagram for boundaries, ownership and integrations.
4. **Representative flow:** D2 request/decision or sequence view; use `mode=flow` for authored request traversal when the installed host supports it. Explain inputs, state owners, persistence, consumers and failure paths.
5. **Implementation:** CodeWalkthrough for the decisive source/config lines; SourceRef for full files where the host can resolve them.
6. **Alternatives and trade-offs:** prose/table, with reasons for the selected approach.
7. **Failure and recovery:** D2 branches or inherited state steps when they clarify behavior; use a table when a graph would add no value.
8. **Validation and open questions:** actual tests, measured versus hypothetical results, unresolved assumptions.

Use D2 `steps` for evolving system state, `tabs` for independent board alternatives, `explorer` for drill-down and `flow` for a request moving through one fixed topology. Use ExampleRef separately only when a real hosted app answers a different question. Do not add SpanWaterfall merely because the architecture is distributed; require timing data or explicitly illustrative durations relevant to the explanation.

## API reference

1. **Scope and authentication:** who calls the interface and which trust boundaries apply.
2. **Contract:** endpoint/method/version, inputs and required/optional fields; Markdown tables or registered TypeTable.
3. **Concrete messages:** ProtocolExchange for HTTP success/error variants, ordered headers and request/response bodies.
4. **Lifecycle and semantics:** idempotency, pagination, ordering, retries, concurrency and consistency where relevant.
5. **Failures:** status/error table plus prose explaining recovery; do not hide explanations in ProtocolExchange metadata that the compact UI does not render.
6. **Validation:** focused tests or reproducible commands; TerminalSession only when command context/output matters.

Keep standalone schemas/payloads as language-labelled code or JSON blocks. For non-HTTP interfaces such as messaging or database protocols, use the real message format and D2 for participant/order relationships, not a fabricated HTTP wrapper.

## Runbook / operations

1. **Symptoms and scope:** when to use this runbook, prerequisites, blast radius and stop conditions.
2. **Diagnosis:** D2 decision tree for branching checks; simple checklists remain prose/lists.
3. **Resolution:** TerminalSession for commands with explicit local/container/pod/remote context, expected results and warnings. Ordinary short code blocks are sufficient for trivial commands.
4. **Configuration change:** CodeDiff for exact before/after, with why and risk in surrounding prose.
5. **Verify recovery:** checks and success criteria; use SpanWaterfall only to explain an actual or clearly synthetic timed trace.
6. **Rollback:** scoped commands, reversibility and data-loss warnings before execution.
7. **Escalation:** evidence to collect, data to redact and escalation criteria.

Do not imply a displayed exit code, transcript or request was executed. Label synthetic outputs and provide observed results only when verified. Keep raw logs as text; they are not diagrams.

## Getting started / how-to

1. **Outcome and prerequisites:** what the reader will achieve and the supported environment.
2. **Orientation:** a small D2 flow or Fumadocs Files/path list only when readers need a mental map.
3. **Setup:** registered Steps/Tabs for procedures/variants; TerminalSession when context or expected output helps.
4. **Implementation:** CodeWalkthrough for non-obvious code and SourceRef for full files; add ExampleRef when readers need to try a real app/behavior variant, with a verified host registry and deployed URL.
5. **Verify:** concrete success checks, expected behavior and likely failure recovery.
6. **Next steps:** existing related pages, not invented links or a repetitive summary.

Do not turn each one-line install command into a separate interactive component.

## Migration / configuration change

1. Explain the old constraint and desired outcome.
2. Use CodeDiff for the exact change, with side-correct line annotations if needed.
3. Explain compatibility, resource/security trade-offs and what the diff alone does not prove.
4. Use TerminalSession for rollout/verification/rollback commands with scoped warnings.
5. Link full implementation through validated SourceRef rather than duplicating whole projects.

A diff is not an executable patch and a rendered example is not a benchmark.

## Concept / internals / concurrency lesson

1. Start from a concrete question or common misunderstanding.
2. Explain the simplest case and terms, then use D2 for causal/ownership relationships.
3. Use D2 steps for state changes; use CodeWalkthrough for source execution reasoning without claiming that the viewer runs code.
4. For RxJS or other exact-time semantics, use an event/frame table and real test code; do not invent a specialized renderer or use arbitrary latency spans as operator semantics.
5. Work through an edge case/failure and a test that distinguishes the correct model from the misconception.
6. End with an actionable choice or related lesson.

Across all types, do not generate Mermaid or hand-drawn ASCII/Unicode diagrams. Use docs-kit D2 for diagrams and preserve literal logs, output, payloads and file listings as ordinary text where appropriate.
