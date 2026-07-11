# AGENTS.md

# AI Development Guide

## Project Overview

This project converts **OudiaSecond (*.oud2)** railway timetable files into Microsoft Excel station timetables.

The project is developed using:
- Visual Studio Code
- GitHub Copilot (Agent Mode)
- ChatGPT
- GitHub MCP
The objective is to build a maintainable application rather than a quick prototype.
---

# Architecture

```
Railway
 ├── Station
 └── Diagram
      └── Train
           └── StopTime
```

The domain model is the source of truth.

---

# Repository Structure

```
src/
    models/
    parser/
    excel/
    tools/

docs/
examples/
tests/
```

---

# Domain Model Rules

Railway is the root aggregate.

Railway owns:
- Station
- Diagram

Diagram owns:
- Train

Train owns:
- StopTime

StopTime references Station.

Avoid reverse references unless explicitly approved.
Avoid duplicated data.
Use the Single Source of Truth principle.
---

# Python Rules

Target version:
Python 3.13

Use:
- dataclasses
- pathlib
- argparse
- typing
- StrEnum
- logging

Do not use:
- os.path
- global variables
- mutable default arguments

Follow PEP8.
---

# Parser Design

Parser responsibilities:
- Read .oud2 files.
- Parse text.
- Construct domain objects.
- Validate data.
- Raise meaningful exceptions.

Parser must NOT:
- Generate Excel.
- Print business data.
- Access GitHub.
- Perform UI processing.

Parser should remain deterministic.
---

# Excel Design

Excel generation belongs to a dedicated module.
Business logic must never depend on Excel formatting.
Formatting rules belong to the excel package.
---

# Development Workflow

Before implementing code:
1. Understand the specification.
2. Update documentation if needed.
3. Implement.
4. Self-review.
5. Explain the implementation.
6. Commit.
---

# AI Collaboration Rules

When proposing code:
Explain:
- What changed.
- Why it changed.
- Advantages.
- Possible drawbacks.

Never silently change the domain model.
Never introduce new classes without justification.
Prefer readability over clever code.
Prefer explicit code over magic.
Keep functions small.
When uncertain, ask instead of guessing.
---

# OudiaSecond Specific Rules

Do not assume standard railway data models.
Always follow the actual OudiaSecond file format.
The parser should reproduce the source data faithfully.
Transformation belongs to later processing stages.
Keep parsing and interpretation separate.
Treat unknown sections as unsupported rather than ignoring them silently.
---


# External Resources

The asset repository is read-only.
Never modify railway assets.
Use GitHub MCP only for reading source files.
Generated files belong to this repository only.
---


# Documentation

Keep documentation synchronized with code.
Whenever the domain model changes:
Update:
- docs/domain_model.md
- AGENTS.md
- README.md (if architecture changed)
Documentation is considered part of the implementation.
---

# Testing

Every parser feature should eventually receive a unit test.
Sample files belong in:
examples/
Tests belong in:
tests/
---

# Logging

Use the logging module.
Avoid print() outside development tools.
---

# Error Handling

Raise meaningful exceptions.
Avoid returning None on failure.
Avoid silent failures.
---

# Performance

Correctness is more important than performance.
Do not optimize prematurely.
---

# Code Review Checklist

Before completing a task, verify:
- Is the design simple?
- Is duplicated data avoided?
- Is the domain model respected?
- Is documentation updated?
- Are type hints present?
- Is the implementation readable?
---

# Commit Policy

Commit only one logical change at a time.
Commit messages should use English.
Examples:
- Add domain model
- Implement OudiaSecond inspector
- Add parser for station section
- Improve parser validation
- Generate Excel timetable
---
