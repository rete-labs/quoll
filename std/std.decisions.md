**STD-1. Expose the native file-system module through the public root [fs] facade, including its default interface, so dependents use [std.fs.path].**
*Stated by* [fs.path].
*Because* inclusion gives dependents the native file-system surface without publishing the internal module tree or copying its statements.
*Accepting* the public root interface and internal module sharing `fs` in their separate namespaces.
*Rejected* providing no public root interface, which leaves dependents without a public file-system surface; exposing the internal module directly, which makes its layout public; and restating its items at the root, which creates two copies to drift.
