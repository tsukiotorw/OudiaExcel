# OuDiaExcel - GitHub Copilot Instructions

## 1. Project Overview

OuDiaExcel is an application that reads OuDiaSecond (`.oud2`) railway timetable files, generates station timetables, and exports them to Excel.

The project consists of:
- Windows desktop application using Python and Tkinter.
- Web application using Python, FastAPI, Jinja2, HTML, CSS, and JavaScript.
- Excel output using openpyxl.
- Automated tests using pytest.

The primary goal is to maintain feature parity between the Windows and Web versions.

## 2. Essential Development Principles

- Always inspect the existing source code before making changes.
- Never assume that a class, function, method, attribute, or file exists without verifying it.
- Follow the existing architecture and coding conventions.
- Prefer small, incremental changes over large modifications.
- Avoid unnecessary refactoring and changes unrelated to the requested task.
- Preserve existing functionality and avoid regressions.
- Reuse existing domain models and application-layer logic whenever possible.
- Do not duplicate business logic between the Windows and Web versions unnecessarily.
- Do not implement behavior based on assumptions. Ask the user when requirements or existing behavior are unclear.
- Treat the current GitHub `main` branch as the source of truth.

## 3. Development Workflow

Before implementing a change:

1. Understand the requested functionality.
2. Inspect the relevant files and existing implementation.
3. Identify the actual classes, methods, and data flow involved.
4. Explain the proposed change and its scope.
5. If important details are unclear, ask the user before proceeding.

During implementation:

- Modify only the files necessary for the task.
- Keep changes small and easy to review.
- Do not change unrelated code.
- Follow existing naming conventions and project structure.
- Do not silently change existing specifications.

After implementation:

1. Review the modified code.
2. Run relevant tests.
3. Run the full test suite using `pytest -s` when appropriate.
4. Report the test results accurately.
5. Clearly distinguish automated test results from actual UI and Excel output verification.
6. Explain any remaining manual verification required.

Do not claim that functionality works unless it has actually been verified.

## 4. Code Change Instructions

When proposing code modifications, always provide:

1. Target file path.
2. Target class, function, or method name.
3. An existing code fragment or comment that can be searched for in VSCode.
4. The exact code to add, replace, or remove.
5. A code example showing the surrounding context after the change.

Avoid vague instructions such as "add this somewhere around here."

When possible, explain why the change is necessary and what other functionality may be affected.

## 5. Architecture and Domain Model

The application processing flow is:

OuDiaSecond file
→ Reader
→ Tokenizer
→ SectionBuilder
→ Parser
→ Domain Model
→ StationTimetableGenerator
→ StationTimetable
→ ExcelWriter

Important domain models include:

- Station
- Railway
- Train
- TrainType
- StopTime
- TimetableEntry
- StationTimetable
- Direction

Respect the existing responsibilities of each layer.

Do not move business logic into UI or route handlers when it belongs in the domain or application layer.

Do not introduce unnecessary architectural changes.

## 6. Windows and Web Feature Parity

The Windows desktop version is the reference implementation for functionality that is being migrated to the Web version.

When migrating a feature:

1. Inspect the Windows implementation first.
2. Understand its behavior and settings.
3. Inspect the existing Web implementation.
4. Reuse shared domain and application logic where appropriate.
5. Implement the Web version incrementally.
6. Verify settings persistence and restoration.
7. Verify preview behavior.
8. Verify Excel output behavior.

A feature is not considered fully migrated merely because it appears correctly in the Web interface.

## 7. Important Existing Specifications

Observe the following established specifications:

- Stations with the same name share station alias settings.
- Stations configured as unmarked do not display their destinations.
- Upbound and downbound destinations must be handled separately when they differ.
- Train type legend visibility and train type display in timetable cells are separate settings.
- Display settings must remain consistent between saved settings, restored settings, preview, and Excel output.

Do not change these specifications without explicit user approval.

## 8. Testing

- Use pytest.
- Prefer the existing test structure and conventions.
- Add tests for new functionality and regression fixes.
- Do not remove or weaken existing tests merely to make them pass.
- Investigate the cause of test failures rather than modifying tests to hide problems.
- Report the actual number of passed, failed, and skipped tests when available.

Full test command:

`pytest -s`

Web application startup command:

`python -m uvicorn src.web.main:app --reload`

Actual browser and Excel verification must be distinguished from automated tests.

## 9. Git and Repository Management

- The `main` branch is the primary development branch.
- Do not create branches unless requested.
- Do not commit or push changes without explicit user approval.
- Do not discard or overwrite existing user modifications.
- Check the working tree before suggesting Git operations.
- Use Japanese commit messages.

Examples:

- `駅略称設定を追加`
- `行先凡例の表示を修正`
- `Excel出力の文字色を修正`

## 10. Communication

- Communicate in Japanese.
- Explain technical terms briefly when necessary.
- Do not overwhelm the user with large amounts of code or unrelated suggestions.
- Work incrementally and wait for user confirmation when a change needs to be applied or verified.
- Prioritize the user's latest source code and test results over assumptions or outdated information.
- Clearly distinguish implemented, unimplemented, and unverified functionality.

## 11. Priority

When instructions conflict, prioritize:

1. The user's explicit and latest instructions.
2. Existing project specifications and verified behavior.
3. This document.
4. General coding preferences.

The primary objective is to develop OuDiaExcel safely and incrementally while maintaining consistency between the Windows and Web applications.
