# quoll

Version 0.3.0, written in [Quoll 0.3.0](package.md).

A language for the source of a system, as [purpose] has it, defined here in itself; the root states what the language is in its [model.interface], and hides how the definition keeps it: the rules of what each part below [model.uses], and the [model.decision]s behind them.

## Modules

```
  layout      how a [layout.package] lies on disk, its files and directories, and the
              [layout.project] that may hold it; its secret, the choices behind what it
              states
  grammar     how the text of a [layout.source file] is written; its secret, the choices
              behind what it states
  model       what a [model.package] means, in the language's terms alone; its secret, the
              choices behind what it states
  source      where each thing of a [model.package] is written, and what is wrong where the
              parts meet; its secret, the choices behind what it states
  principles  what every [model.package] keeps across its history and its writers, and what
              review judges of it; its secret, the choices behind what it states
```
