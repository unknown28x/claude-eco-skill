# Low-cost recipes

Every tool result stays in the context and is re-read on each later call.
A 20k-token file read at the start of a 100-call session costs 2M re-read tokens.

## Reading
- Search first (file list, then matching lines with line numbers and a result cap), then read
  with an offset and a limit.
- Never a whole file "to have a look" beyond ~300 lines.
- Never the same file twice. After a successful edit, do not re-read.
- Generated or minified files, lockfiles, logs: never in full. `wc -l`, `head`, `tail`, `grep -c`.
- Large JSON: extract the useful keys with a short script; do not print the rest.

## Running
- Always bound the output: `| head -40`, `| tail -20`, `--quiet`, `-q`, `--silent`.
- Tests: run the relevant file or test, not the whole suite; print failures only.
- Installs and builds: redirect to a file, show only the end (`> out.log 2>&1; tail -15 out.log`).
- One compound command instead of five calls. A scratch script for a sequence of steps.
- Long command: run it in the background, no polling.

## Batching
- Independent calls (several searches, several reads) go in the **same** message.
- Each round trip avoided saves one full re-read of the context.

## Browser and images
- Read the page text or accessibility tree instead of taking a screenshot. Screenshot only to
  judge visuals, at reduced scale when detail is not needed, zoomed on the useful region.
- Chain predictable browser actions in a single batched call when the tool allows it.
- One proof screenshot at the end, not one per step.

## Writing
- Targeted edit instead of rewriting a whole file.
- No documentation, summary or report file that was not requested.
- Do not paste code into the reply when it is already in a file: give `path:line`.

## Replying
- Answer first. No restating the request, no list of what was just done beyond 3 lines, no options
  you do not recommend.
- Ask a question only when the answer changes the work.
