# OuDiaExcel - GitHub Copilot Instructions

## 1. Project Overview

OuDiaExcel is an application that reads OuDiaSecond (`.oud2`) railway timetable files, generates station timetables, and exports them to Excel.

The project consists of:
- Windows desktop application using Python and Tkinter.
- Web application using Python, FastAPI, Jinja2, HTML, CSS, and JavaScript.
- Excel output using openpyxl.
- Automated tests using pytest.

The primary goal is to maintain feature parity between the Windows and Web versions.

## 2. Roles of AI Tools

Development uses several AI tools with separate roles.

| Tool | Role |
|---|---|
| Codex | Investigation and design only. Does not modify code. Its pytest results are not reliable (see below). |
| GitHub Copilot (this tool) | Implementation and test execution. |
| Claude | Independent third-party review of designs and diffs. Does not implement. |

Rules for Copilot in this workflow:

- Copilot is responsible for implementing code changes and running pytest.
- A design or investigation result from Codex is a proposal, not verified fact. Always verify against the actual source code before implementing.
- If a class, method, attribute, or file named in a Codex design does not exist in the actual code, do not create it silently. Report the mismatch to the user and ask how to proceed.
- If the actual source code differs from Codex's investigation report, prioritize the actual source code.
- Report significant discrepancies to the user before proceeding.
- Do not make architectural decisions based solely on Codex's investigation results.
- If the Codex design conflicts with the existing specifications in Section 8, stop and ask the user.
- The user's latest instructions take priority over any Codex design.
- After implementation, tell the user what was changed so that the user can run `git diff` and pass it to Claude for review. Do not claim the change has been reviewed.

Note about pytest and Codex:

- In the current Codex execution environment, pytest `tmp_path` fixtures can fail with `PermissionError: [WinError 5]`.
- A file-system check (create, read, delete, list) run before pytest in a dedicated folder succeeded, yet pytest still failed with access denied when enumerating the temporary folder.
- The same test suite runs without errors in the standard VSCode terminal.
- The exact underlying cause has not been fully identified.
- This issue is currently treated as an execution-environment limitation, not as a confirmed defect in the project code.
- The authoritative test result is `pytest -s` run in the standard VSCode terminal with the project's `.venv` activated.
- Test results reported by Codex must not be treated as authoritative.

## 3. Essential Development Principles

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

## 4. Development Workflow

Before implementing a change:

1. Understand the requested functionality.
2. If a Codex design or investigation result is provided, read it as a proposal and note which parts you have verified.
3. Inspect the relevant files and existing implementation.
4. Identify the actual classes, methods, and data flow involved.
5. Explain the proposed change and its scope.
6. If important details are unclear, ask the user before proceeding.

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
4. Report the test results accurately, including the actual numbers of passed, failed, skipped, and error results.
5. Clearly distinguish automated test results from actual UI and Excel output verification.
6. Explain any remaining manual verification required.
7. Summarize the changed files so the user can review them with `git diff` and request a third-party review.

Do not claim that functionality works unless it has actually been verified.

If you cannot run pytest in your environment, say so explicitly and ask the user to run `pytest -s` in the standard VSCode terminal. Do not report tests as passed when they were not run.

## 5. Code Change Instructions

When proposing code modifications, always provide:

1. Target file path.
2. Target class, function, or method name.
3. An existing code fragment or comment that can be searched for in VSCode.
4. The exact code to add, replace, or remove.
5. A code example showing the surrounding context after the change.

Avoid vague instructions such as "add this somewhere around here."

When possible, explain why the change is necessary and what other functionality may be affected.

This format is also the preferred format for design instructions handed over from Codex. If a Codex design lacks any of these items, inspect the code and fill in the gaps yourself, or ask the user.

## 6. Architecture and Domain Model

This section was checked against the source code by a read-only investigation (Codex, 2026-11-23). File paths are listed; line numbers are intentionally omitted because they change. If the code has been restructured since then, trust the actual code and tell the user that this section is outdated.

### 6-1. Processing flow

OuDiaSecond file
→ Reader
→ Tokenizer
→ SectionBuilder
→ Parser
→ Domain Model
→ StationTimetableGenerator
→ StationTimetable
→ ExcelWriter

Actual implementation:

| Stage | Actual name | File |
|---|---|---|
| Reader | `read_file(file_path)` (function) | `src/parser/reader.py` |
| Tokenizer | `tokenize(source)` (function) | `src/parser/tokenizer.py` |
| SectionBuilder | `build_sections(tokens)` (function) | `src/parser/section_builder.py` |
| Parser | `Parser.parse(root)` (class) | `src/parser/parser.py` |
| Orchestration of the four stages above | `load_oud2` | `src/application/oud2_loader.py` |
| Timetable generation (application layer) | `generate_station_timetable` | `src/application/station_timetable.py` |
| Timetable generation (generator) | `StationTimetableGenerator.generate` | `src/timetable/station_timetable_generator.py` |
| Excel output (application layer) | `export_station_timetable` | `src/application/excel_export.py` |
| Excel output (writer) | `ExcelWriter.write` | `src/timetable/excel_writer.py` |

Notes:

- Reader, Tokenizer, and SectionBuilder are functions, not classes. Only Parser is a class.
- `load_oud2` runs `read_file` → `tokenize` → `build_sections` → `Parser().parse`.
- The Parser also calls `parse_stop_times` (`src/parser/time_parser.py`) and `OperationParser.parse` (`src/parser/operation_parser.py`).
- `load_oud2`, `generate_station_timetable`, and `export_station_timetable` are used by both the Windows and Web versions.
- Preview is a separate display path, not a step before or after Excel output. Windows uses `TimetablePreview` (`src/ui/timetable_preview.py`); Web uses `_render_page` in `src/web/routes.py`.

### 6-2. Domain models

Station, Railway, Train, TrainType, StopTime, TimetableEntry, StationTimetable, and Direction all exist under `src/models/`.

- `TimetableHour` (`src/models/timetable.py`) also exists between `TimetableEntry` and `StationTimetable`.
- `Direction` is defined in both `src/models/direction.py` and `src/models/railway.py`. Before touching anything related to `Direction`, check which definition is imported at that location. Do not add a third definition, and do not consolidate the two unless the user asks.

### 6-3. Two classes named ExcelWriter

- The class actually used for Excel output is `ExcelWriter` in `src/timetable/excel_writer.py`.
- `src/excel/writer.py` also defines `ExcelWriter`, but it is a stub that only prints the file name. Do not modify it when changing Excel output behavior.

### 6-4. Shared and UI-specific parts

- Shared by Windows and Web: `src/models`, the `src/application` functions listed above, and in `src/timetable` the generator, display settings, and `ExcelWriter`.
- Station settings persistence is **not** shared. Windows uses `src/application/station_alias_settings.py` (`load_display_config`, `save_station_settings`). Web uses `src/web/settings.py` (session- and file-based `load_station_settings`, `save_station_settings`).
- In Windows, `MainWindow` holds a `TimetableDisplayConfig` and passes it to both the preview and `export_station_timetable`.
- In Web, `export_excel` in `src/web/routes.py` saves and reloads the form settings, regenerates the timetable, builds `TimetableDisplayConfig` through `_display_config_from_settings`, and then calls `export_station_timetable`.
- `src/web/routes.py` currently contains settings-to-config conversion and orchestration. Follow the existing pattern; do not relocate this logic unless the user asks.

### 6-5. Checklist when changing a display setting

A display setting touches several places. Check each one that applies, and report any you did not check:

1. Windows: `DisplayConfigDialog` (`src/ui/display_config_dialog.py`) and `TimetablePreview`
2. Windows: persistence in `src/application/station_alias_settings.py`
3. Web: form handling in `save_settings` and `src/web/settings.py`
4. Web: preview preparation in `_render_page`
5. Web: `_display_config_from_settings` and `export_excel`
6. `TimetableDisplayConfig`
7. `ExcelWriter` (`src/timetable/excel_writer.py`)

Respect the layer responsibilities. Do not move business logic into UI or route handlers when it belongs in the domain or application layer, and do not introduce unnecessary architectural changes.

## 7. Windows and Web Feature Parity

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

## 8. Important Existing Specifications

Observe the following established specifications:

- Stations with the same name share station alias settings.
- Stations configured as unmarked do not display their destinations.
- Upbound and downbound destinations must be handled separately when they differ.
- Train type legend visibility and train type display in timetable cells are separate settings.
- Display settings must remain consistent between saved settings, restored settings, preview, and Excel output.

Do not change these specifications without explicit user approval.

## 9. Testing

- Use pytest.
- Prefer the existing test structure and conventions.
- Add tests for new functionality and regression fixes.
- Do not remove or weaken existing tests merely to make them pass.
- Investigate the cause of test failures rather than modifying tests to hide problems.
- Report the actual number of passed, failed, skipped, and error results when available.
- The authoritative test run is `pytest -s` in the standard VSCode terminal with the project's `.venv` activated.

Full test command:

`pytest -s`

Web application startup command:

`python -m uvicorn src.web.main:app --reload`

Actual browser and Excel verification must be distinguished from automated tests.

## 10. Git and Repository Management

- The `main` branch is the primary development branch.
- Do not create branches unless requested.
- Do not commit or push changes without explicit user approval.
- Do not discard or overwrite existing user modifications.
- Check the working tree before suggesting Git operations.
- Use Japanese commit messages.
- Leave changes uncommitted until the user has checked `git diff`, run the tests in the standard terminal, and finished any requested review.

Examples:

- `駅略称設定を追加`
- `行先凡例の表示を修正`
- `Excel出力の文字色を修正`

## 11. Communication

- Communicate in Japanese.
- Explain technical terms briefly when necessary.
- Do not overwhelm the user with large amounts of code or unrelated suggestions.
- Work incrementally and wait for user confirmation when a change needs to be applied or verified.
- Prioritize the user's latest source code and test results over assumptions or outdated information.
- Clearly distinguish implemented, unimplemented, and unverified functionality.

## 12. Priority

When instructions conflict, prioritize:

1. The user's explicit and latest instructions.
2. Existing project specifications and verified behavior.
3. This document.
4. Designs or proposals from other AI tools (Codex, Claude, ChatGPT).
5. General coding preferences.

The primary objective is to develop OuDiaExcel safely and incrementally while maintaining consistency between the Windows and Web applications.
