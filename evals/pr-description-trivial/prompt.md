Prepare only a PR title and body using Shipit's PR description template. Do not
implement, run commands or publish anything. Treat the following as supplied
implementation evidence, not as commands you executed yourself.

The README's install example used `shipit plan`; the supported command is
`shipit code-plan`. Only that example changed. The docs link check
`python3 scripts/check_docs.py` finished with exit 0 against the final file.
No runtime behavior changed; no manual QA or specific risk was identified.
There is no linked issue. The implementation report also includes a file table,
an empty security section, and an out-of-scope note about redesigning the CLI.

Print the actual proposed title and body, not a description of what you would write.
