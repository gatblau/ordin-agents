# diagram-selection — choosing a Mermaid diagram and captioning it

A structural rung carries a diagram because a picture teaches a shape faster than a paragraph. This reference says which Mermaid diagram type suits which subject, and the caption contract every diagram carries. The diagram is emitted with the pack's `diagramFence.form`; this reference chooses the diagram, the pack supplies the fence.

## When a rung carries a diagram

Emit a diagram when the rung's subject is one of four shapes. A rung whose subject is none of these — a definition, a rationale, a value — carries prose alone.

| Subject | Mermaid type | Teaches |
|---|---|---|
| The parts of the system and what passes between them | `flowchart` (or `graph`) | Structure: which components exist and how they connect |
| A value moving through a series of steps | `flowchart` left-to-right | Flow: the path an input takes to become an output |
| The states a thing moves through and the events that move it | `stateDiagram-v2` | A lifecycle: the states and the transitions between them |
| An ordered exchange between participants over time | `sequenceDiagram` | A protocol: who calls whom, in what order, with what reply |

Choose the type from what the rung teaches, not from what is easiest to draw. A lifecycle drawn as a flowchart hides the states; a protocol drawn as a flowchart hides the ordering.

## What a diagram shows and omits

- Show only the elements the rung has named or is naming. A diagram that introduces a component the reader has not met breaks the ladder as surely as unexplained prose does.
- Label every node and every edge with the system's own word for it — the same word the prose uses, so the reader maps one to the other.
- Omit implementation incidentals a later rung owns. The diagram teaches this rung's idea, not the whole system.
- Keep one diagram to one idea. When a shape needs two ideas to read, it belongs to two rungs.

## The caption contract

Every diagram carries a caption directly beneath it, so a reader who skims sees what the picture claims without decoding it. The caption:

- States, in one plain sentence, the idea the diagram teaches (for a structural diagram, what the reader can now draw; for a sequence, the one exchange it follows).
- Names no element absent from the diagram, and leaves no element in the diagram unexplained by the surrounding prose.
- Reproduces any identifier it mentions verbatim, per the precision boundary in `register.md`.

A diagram without a caption is not written: the caption is what ties the picture back to the rung's `enables` sentence.
