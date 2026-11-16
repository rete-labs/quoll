**STD-1. Expose the native file-system module's default interface at the public root `fs` path, so dependents use [std.fs.path].**
*Stated by* [fs.path].
*Because* explicit exposure gives dependents the native file-system surface without publishing the internal module tree or copying its statements.
*Accepting* an internal root default interface declaring the exposure while remaining unexposed itself.
*Rejected* providing no public file-system path, which leaves dependents without a public file-system surface; exposing the internal module directly, which makes its layout public; and restating its items at the root, which creates two copies to drift.
