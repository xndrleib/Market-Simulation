# Repository Guidelines

This file defines how automated coding agents (and humans) should work in this repository.

## Goals

- Produce correct, maintainable Python code.
- Prefer small, composable modules over monoliths.
- Ensure progress is observable via **structured logging** (console + file) and **tqdm**.
- Keep code style consistent: **PEP8**, NumPy-style docstrings, and clear documentation in `docs/`.
- Make results reproducible: deterministic configs, fixed seeds, and well-defined environments.
---

## Coding standards

### Style & formatting

- Follow **PEP8**.
- Prefer `black`. If not configured, keep formatting consistent and avoid stylistic churn.
- Keep functions short and focused. Avoid implicit global state.
- Avoid “clever” code; optimize for readability.

### Types

- Add type hints to public functions and key internal boundaries.

### NumPy-style docstrings

Use NumPy-style docstrings for all public modules, classes, and functions. Minimum expectations:

- One-line summary
- Parameters / Returns
- Raises (if applicable)
- Notes (optional)
- Examples (optional but encouraged for utilities)

---

## Logging & progress reporting (required)

### Use `logging` (not `print`) for normal output

* All user-visible progress and status should go through the `logging` module.
* Prefer structured, actionable messages (what is happening, how long it took, key metrics).
* Never spam logs per-item unless explicitly requested; aggregate where possible.

---

## Testing expectations

* Add or update tests for behavior changes.
* Prefer fast unit tests; keep integration tests small.
* Use `pytest`.

---

## Documentation expectations (`docs/`)

* Higher-level documentation belongs in `docs/`, not scattered across code comments.
* When introducing a new feature or workflow, add a short doc:
  * purpose
  * how to run
  * key design decisions
  * expected inputs/outputs

---

## Agent workflow rules

### Before editing

* Scan the repo for:
  * existing utilities and patterns
  * code style tooling (pyproject.toml, black config)
* Prefer extending existing abstractions rather than adding parallel ones.

### While editing

* Make minimal, focused commits in spirit (even if not actually committing).
* Avoid large refactors unless required to implement the change safely.
* Preserve public APIs unless there’s a strong reason to change them.

### After editing

* Ensure:
  * code runs (at least import-level sanity)
  * tests updated/added (if applicable)
  * docstrings added/updated
  * logging usage is appropriate
* Update `docs/` if the change affects usage or architecture.

---

## Safety and data handling

* Do not hardcode secrets (API keys, tokens).
* Avoid writing personally identifiable data to logs.

---

## What not to do

* Don’t replace `logging` with `print`.
* Don’t add noisy per-sample logs.
* Don’t add heavyweight frameworks without clear value and documentation.
