# Writing a package

What every writer and reviewer of a package keeps beyond the definition's own rules, which it never restates: the practice that has held in writing Quoll so far.

- **Terms before use.** Every term is met where it is defined before it is used, in the order a reader meets the text: a lead and an entry's text as much as a view's items.
- **Obligations, not mechanisms.** A header states what must hold for its users, and who keeps it; how it is kept is a body's, and what may change unnoticed is the code's. A header sketches no mechanism, and names no programming language's types.
- **Entries short.** A *Because* gives a general reason, with no anecdote naming a particular module or case; a *Rejected* keeps only the options someone would propose again, and none a *Because* already answers.
- **Examples short**, a few lines; a domain in an example is `acme.example`, and `acme.test` in a test.
- **Patch or rewrite.** Where a change stays in the items it is about, patch them, then search every term it touches and read each place found. Where one change threads through most of a file, rewrite the file from what it must keep rather than item by item: an edit reaches fewer places than it should, and a rewrite is closed over its inputs.
