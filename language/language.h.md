+++
[exposes]
default = "default"
layout = "layout.default"
grammar = "grammar.default"
source = "source.default"
principles = "principles.default"
"model.kernel" = "model.kernel"
"model.graph" = "model.graph"
"model.rich" = "model.rich"
"model.profile" = "model.profile"
"model.generation" = "model.generation"
+++
What the language is, for whoever reads or writes a package in it, agent or person: its [purpose], its [reach], its [writers] and [readers], its [goal], the open [measure] that is to check it and [pilot evidence] that informs it, the open [structural tooling] direction, its [paradigm] and [character], and how its statements are [formal].

## Structure

```
  purpose         a language for the maintained source of a system: permanent non-code contracts
                  and abstract designs, canonical native code with its decisions,
                  canonical Quoll and mixed sources, and the derived [model.kernel.target]s and
                  temporary design views around them; every local agent-authored change is
                  [model.kernel.generation activity], while [model.kernel.source] and
                  [model.kernel.target] distinguish authority rather than who writes
  reach           any system designed over a long series of changes, software first; the core,
                  the language as defined here, names no domain, a domain's notions, software's
                  among them, coming in a framework, as [model.profile.framework rules] has it

  writers         agents, under people's supervision or on their own; people may write a source,
                  but are not expected to
  readers         people above all, engineers and architects fluent in the design of
                  modules who build software with AI, the language assuming that
                  design and teaching none of it; and agents

  goal            a flat cost of change with the least reading: a change of a given size costs
                  the same however many came before it, over a whole workflow and every artifact
                  it maintains or generates, while people read only what a sound change needs
  paradigm        a programming language one level up, natural to engineers and architects: its
                  unit the module, and every other [paradigm] a style a framework
                  declares over modules, among its [model.profile.framework rules]
  character       simple, as elegant C is rather than convoluted C++, and grown from practice
                  rather than theory

  open:
    measure         how the [goal] is to be checked over a comparable series of changes across
                    workflows, separating agent effort from human reading and structural erosion;
                    its protocol is neither designed nor run
    pilot evidence  canonical native, Quoll-owned generation and mixed source workflows supply
                    concrete cases for their mechanisms and later decisions, with detailed evidence
                    plans belonging to work items and the separate benchmarking project
    structural tooling  model-aware rendering, IDE navigation and structural diffs over changed
                        items, relations, dependents and decisions,
                        rather than colorized text lines alone; canonical Markdown/TOML remains the
                        bootstrap representation now, while renderer, IDE, structural-diff and
                        replacement-syntax forms stay open; a programming-language-like syntax is
                        a separate migration hypothesis for a dedicated design pass informed by
                        native and document profiles, these directions being neither existing
                        tools nor another coordinate [goal]
```

## Rules

```
  ensures:
    formal  every statement is in natural language and [formal] from an agent's side: each one
            an agent can follow, and each rule one it can check, or, a judgement, weigh
```
