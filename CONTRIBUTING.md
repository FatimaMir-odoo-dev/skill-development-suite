# Contributing

Thank you for your interest in contributing to this project!
Issue fixes, bug reports, documentation improvements, tests, and thoughtful discussions are very welcome.

## About Feature Suggestions

This project has a defined scope and set of goals. Feature suggestions are evaluated against that scope and may not be accepted. The maintainer may prioritize bug fixes and stability over new features. Suggestions accompanied by a concrete implementation (such as a pull request or proof-of-concept) are more likely to be reviewed and considered.

If your contribution isn't accepted, please don't be discouraged, this is a normal part of the review process and not a reflection on the quality of your work.

---

## Ways to Contribute

If you're unsure where to begin, start by looking through issues labeled `help-wanted`. These represent areas where contributions are most needed.

> ⚠️ **Security issues**
> If you discover a security vulnerability, do not open a public issue.
> Please follow the instructions in `SECURITY.md`.

You can also help by:

### 🐞 Reporting Bugs

Bug reports are essential to improving project stability. A good report helps others reproduce the issue and work toward a fix.

Please open a GitHub issue and include:

- A short description of the problem
- Impacted versions / your operating system and environment
- Clear steps to reproduce
- Current behavior vs. expected behavior
- Relevant logs, screenshots, or error messages (if available)

If you're a programmer, try investigating/fixing yourself, and consider making a Pull Request instead.

### 📚 Improving Documentation

Documentation fixes, clarifications, and examples are highly appreciated. You don't need to be an Odoo expert — even pointing out missing information, unclear wording, or broken links is valuable.

### 💻 Contributing Code via Pull Requests

Small, focused pull requests are preferred. Contributions may be revised or declined to fit the project's goals.

- Reference related issues in your pull request (e.g. `Fixes #42`)
- Feature or enhancement PRs should usually be based on an existing feature request with prior discussion and demonstrated interest
- Pull requests that introduce new features without prior discussion may not be merged

---

## How to Contribute

### 1. Open an Issue First (When Appropriate)

To avoid duplicate work and align on scope, it's usually a good idea to discuss changes before writing code.

> **Note:** If you are submitting a pull request that clearly fixes a bug, opening a separate issue is not required — describe the issue directly in the PR.

### 2. Fork and Create a Branch

Fork the repository and create a dedicated branch for your change.

### 3. Make Your Changes

- Keep changes focused and aligned with the project's goals
- Follow the existing code structure and style

### 4. Run Checks

Ensure that any applicable local checks (linting, formatting, pre-commit hooks) pass before submitting.

### 5. Submit a Pull Request

When opening a pull request, please describe:

- What the change does
- Which issue it addresses (if applicable)
- Any known limitations or follow-up work

---

## Development Guidelines

**Supported Versions:** This module targets Odoo 16.0 and above. When opening a pull request, please specify which Odoo version you developed and tested against.

Any development environment is fine.
> p.s: The maintainer develops primarily on Windows 10 using PyCharm

- Code must follow [OCA development guidelines](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md)
- Ensure `flake8` and other configured checks pass
- Keep changes consistent with standard Odoo module layout and naming conventions
- Avoid introducing new dependencies unless discussed first

Before submitting:

- Rebase your branch on the target branch to minimize conflicts
- Resolve merge conflicts manually if necessary
- Match the surrounding code style (whitespace, formatting, structure)

### Commit Messages

Please follow this format:

```
[TAG] module: short description

Optional longer explanation.
References (issue or PR).
```

**Example:**

```
[FIX] my_module: correct field validation logic
```

**Common tags:**

| Tag | Usage |
|-----|-------|
| `[FIX]` | Bug fixes |
| `[ADD]` | New enhancements |
| `[REF]` | Refactors |

---

## 📄 License

This project is licensed under **LGPL-3.0**. By contributing to this repository, you agree that your contributions will be licensed under the same LGPL-3.0 license. No separate contributor license agreement (CLA) is required.

---

Thank you for taking the time to contribute, your help is genuinely appreciated.
```
