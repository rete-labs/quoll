# Writing a package

What every writer and reviewer of a package keeps beyond the definition's own rules, which it never restates: the practice that has held in writing Quoll so far.

- **Order for the reader.** Order a lead, an entry's text and a view's items to make their reading clear, subject to the definition's `acyclic definitions` rule.
- **Obligations, not mechanisms.** A header states what must hold for its users, and who keeps it; how it is kept is a body's, and what may change unnoticed is the code's. A header sketches no mechanism, and names no programming language's types.
- **Entries short.** A *Because* gives a general reason, with no anecdote naming a particular module or case; a *Rejected* keeps only the options someone would propose again, and none a *Because* already answers.
- **Examples short**, a few lines; a domain in an example is `acme.example`, and `acme.test` in a test.
- **Patch or rewrite.** Where a change stays in the items it is about, patch them, then search every term it touches and read each place found. Where one change threads through most of a file, rewrite the file from what it must keep rather than item by item: an edit reaches fewer places than it should, and a rewrite is closed over its inputs.
- **Chunks close over their targets and consumers.** Split a large change into coherent chunks that can each be checked and reviewed with their target contract and declared consumers. Finish each chunk's dependent-site and decision-lifetime passes before settling it; whole-package consistency does not justify showing unrelated interfaces to an implementation writer.
- **A missing binding is escalated, not patched around.** When the named inputs lack a dependency or join, stop the affected work and name the binding to the orchestrator. Never widen your own reads or invent a contract to keep a chunk moving.

## Reporting

A role's prompt says whether its report is persistent or text-only. A persistent report has one exact path authorized in the prompt: `writer-report.md` for a writer and `reviewer-report.md` for a reviewer by default. These names are chosen when the prompt is written, never changed in response to a denial. The role writes that file directly; it is an authorized exception to the role's "no other file" limit. Prompt authorization bounds the role's behavior; it is not a sandbox and adds no harness permission, so the existing harness permission rules continue to govern every write. A text-only report is returned complete in the hand-back, and the orchestrator does not silently persist it as a report.

For the current harness, an orchestrator does not choose `findings.md` or a Markdown basename beginning with `REPORT`, `SUMMARY`, `FINDINGS`, or `ANALYSIS`, including case variants, for a subagent's persistent report. The guard's stated purpose is to make subagents return findings as text; where a frozen review needs a durable artifact instead, the role-qualified names above provide that explicit persistent contract. This is a naming convention chosen before execution, not leave to evade a denial.

If a persistent report cannot be written, the role returns the complete report and the exact tool error in its hand-back. On an explicit denial it stops: no retry, rename, other write method, or request for the orchestrator to write the denied path. The orchestrator surfaces the missing persistent artifact rather than treating the hand-back as a saved report. If the role finishes without the file and without attempting the authorized write, the orchestrator resumes the same agent to complete that write; it neither spawns a duplicate agent nor invents another report path.
