# Go — principles

The idiomatic stance `codegen` and `testgen` apply when writing Go. Read this
before the mechanics in `build-commands.md` and `file-layout.md`: those say *how*
to build and lay out; this says *what good Go looks like*.

## The stance

Go favours clarity over cleverness. The reader, not the writer, is the audience.
A change is good when the next person understands it without the author present.
Prefer a longer, obvious line to a short, surprising one.

## Non-negotiables

1. **Every error is handled explicitly.** Check `err` at the call site; wrap it
   with context (`fmt.Errorf("doing X: %w", err)`) or return it. Never discard it
   with `_` unless the call genuinely cannot fail and a comment says why.
2. **Accept interfaces, return structs.** A function takes the smallest interface
   it needs and returns a concrete type. Define the interface where it is
   *consumed*, not where it is implemented.
3. **Keep interfaces small.** One or two methods is typical. A large interface is
   a sign the abstraction is wrong.
4. **`context.Context` is the first parameter** of any function that does I/O,
   blocks, or may need cancelling. It is never stored in a struct.
5. **The zero value is useful.** Design types so the zero value is valid and
   ready to use; avoid mandatory constructors where a zero value would serve.
6. **Concurrency has an owner.** Every goroutine has a clear lifetime and a way to
   stop (a `context`, a closed channel). If you cannot say who stops a goroutine,
   do not start it.
7. **`gofmt` is the style.** There is no house style beyond the formatter and
   `go vet` / the linter. Do not argue layout; run the tool.
8. **Abstract only on the third use.** Do not add an interface, generic, or layer
   for a single caller. Duplication is cheaper than the wrong abstraction.
