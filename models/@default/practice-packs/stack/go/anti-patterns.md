# Go — anti-patterns

Idioms to avoid when writing Go. Each entry names the smell, says why it hurts,
and gives the idiomatic alternative. `codegen` must not emit these; a review
that finds one stops for a fix.

## Avoid

1. **Ignored errors** — `_ = doThing()` or an unchecked return. Failures vanish
   silently. *Instead:* handle, wrap, or return the error; ignore only with a
   comment stating why it cannot fail.
2. **Naked returns in long functions** — bare `return` with named results far
   from the signature. The reader cannot see what is returned. *Instead:* return
   values explicitly; reserve named returns for short functions or `defer` edits.
3. **`interface{}` / `any` as a shortcut** — losing the type to avoid modelling.
   *Instead:* use a concrete type, a small interface, or generics with a real
   constraint.
4. **Goroutine leaks** — starting a goroutine with no cancellation or no reader
   for its channel. *Instead:* pass a `context`, ensure every send has a receiver,
   and make the stop path explicit.
5. **Package-level mutable state** — global `var`s mutated at runtime. They defeat
   tests and create hidden coupling. *Instead:* pass dependencies in explicitly.
6. **`panic` in library code** — panicking on a recoverable condition. *Instead:*
   return an error; reserve `panic` for `main` bootstrap that cannot continue.
7. **Over-broad interfaces** — defining a many-method interface the caller barely
   uses. *Instead:* define the one- or two-method interface at the consumer.
8. **Premature generics** — a type parameter with a single instantiation.
   *Instead:* write the concrete version until a second type genuinely needs it.
