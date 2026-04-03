# Security Policy

## Supported versions

`datareadme` is early-stage software, so security fixes will be applied to the latest code on `main`.

## Reporting a vulnerability

Please do not open public GitHub issues for suspected security vulnerabilities.

Instead:

- open a private GitHub security advisory if available
- or contact the maintainer directly through GitHub

When reporting, include:

- what you found
- how to reproduce it
- any affected files or inputs
- whether sensitive data exposure is involved

You can expect an initial response within a reasonable best-effort window, with follow-up once the issue is reproduced and assessed.

## Scope notes

This project aims to be local-first and conservative with data handling.

Current expectations:

- the default workflow is no-LLM
- future LLM integrations should avoid sending raw datasets by default
- generated documentation should be reviewed before being shared publicly
