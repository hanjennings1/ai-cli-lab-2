# Project Management CLI with AI Client Feature
**Completed Sept 11, 2026** 

## Overview
A Python command-line tool for managing a simulated multi-user project tracker. Admins can create users, assign projects to them, add and complete tasks, and generate AI-powered project insights (a summary, a risk note, or a suggested next step) based on real project/task data.

The app demonstrates object-oriented design (inheritance, encapsulation via `@property`, class attributes), local JSON persistence, a modular file structure, and integration with a local AI model (Ollama) through a clean, reusable service layer.

## Architecture

The app is organized into three layers, each with a single responsibility:

| Layer | Files | Responsibility |
|---|---|---|
| Models | `models/person.py`, `user.py`, `project.py`, `task.py` | Data and relationships. `Person` is a base class; `User` inherits from it. `User` → `Project` → `Task` is one-to-many at each level. Each model supports `to_dict()`/`from_dict()` for JSON round-tripping. |
| Services | `services/storage_service.py`, `ai_client.py`, `project_summary_service.py` | `StorageService` reads/writes `data/project_data.json`. `OllamaChatClient` is a generic, reusable client for talking to a local Ollama model (it knows nothing about projects or tasks). `ProjectSummaryService` builds the prompts, validates responses, and formats output for the AI feature; it calls the AI client but never talks to Ollama directly. |
| CLI | `main.py`, `utils/formatters.py` | Parses commands with `argparse`, routes to handler functions, and calls into the models/services. `utils/formatters.py` holds shared display formatting used by the CLI. |

This separation keeps the AI client fully reusable for other projects, keeps prompt/domain logic out of the client, and keeps the CLI focused purely on command parsing and user interaction.

## File Structure
```
ai-cli-lab-2/
├── main.py # CLI entry point - argparse commands, routes to models/services
│
├── models/
│ ├── person.py # Base class: name, email, validation
│ ├── user.py # User(Person) - owns Projects
│ ├── project.py # Project - owns Tasks, has an auto-incrementing id
│ └── task.py # Task - status controlled via @property/setter
│
├── services/
│ ├── storage_service.py # Load/save users to JSON, with error handling
│ ├── ai_client.py # OllamaChatClient - generic, reusable Ollama wrapper
│ └── project_summary_service.py # Builds prompts, validates AI output, formats result
│
├── utils/
│ └── formatters.py # Shared CLI display formatting
│
├── data/
│ └── project_data.json # Persisted users/projects/tasks
│
├── tests/ # pytest suite (44 tests) covering models, storage, and services
│
├── requirements.txt # Dependencies
└── README.md
```


## Setup

**1. Clone the repo**
```bash
git clone https://github.com/hanjennings1/ai-cli-lab-2.git
cd ai-cli-lab-2
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux/WSL
# or on Windows (not WSL): .venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

## AI Feature Setup (Required for `summarize-project`)

The `summarize-project` command uses [Ollama](https://ollama.com) to run a language model locally. All other commands work without this setup.

1. [Install Ollama](https://ollama.com/download) for your OS.
2. Pull the model used by this app:
```bash
   ollama pull llama3.2
```
3. Make sure Ollama is running (it typically starts automatically after install, or run `ollama serve`).

If Ollama isn't running or the model isn't pulled, `summarize-project` will fail gracefully with a clear error message rather than crashing the CLI.

## Running the CLI

Each command is run individually from the terminal:

```bash
python main.py <command> [options]
```

## Commands & Examples

```bash
# Create a user
python main.py add-user --name "Jordan" --email "jordan@example.com"

# Add a project to a user
python main.py add-project --user "Jordan" --title "Website Redesign" --description "Redo the homepage" --due-date "2026-10-01"

# List a user's projects
python main.py list-projects --user "Jordan"

# Add a task to a project
python main.py add-task --project "Website Redesign" --title "Wireframe homepage" --assigned-to "Jordan"

# Mark a task complete
python main.py complete-task --project "Website Redesign" --task "Wireframe homepage"

# Generate an AI insight for a project
python main.py summarize-project --project "Website Redesign" --type summary
# --type also accepts: risk, next-steps
```

Data persists automatically to `data/project_data.json` after every command.

## Running the Tests

```bash
pytest -v
```

The test suite (44 tests) covers all three model classes, `StorageService` (including malformed/missing JSON handling), `OllamaChatClient` (using `monkeypatch` to mock the AI service / no real Ollama connection required), and `ProjectSummaryService`. Tests do not require Ollama to be running.

## Features

- Create and list users
- Add projects to users and list a user's projects
- Add tasks to projects and mark them complete
- Full JSON persistence with graceful handling of missing/corrupted data files
- Object relationships: `User` → `Project` → `Task` (one-to-many), with `User` inheriting shared fields from a `Person` base class
- Controlled attribute access via `@property` (`Task.status` can't be set to an invalid value)
- Auto-incrementing project IDs via a shared class attribute
- AI-generated project insights (summary, risk note, or next-step suggestion) via a local Ollama model

## Known Issues / Limitations

- **Project titles are assumed to be unique across the whole system.** Commands like `add-task`, `complete-task`, and `summarize-project` look up a project by title across *all* users; if two users have identically-titled projects, the first match found will be used.
- **No update/delete commands** for users, projects, or tasks: the CLI currently supports create, read (list), and complete/mark-done only.
- **AI output quality depends on the local model.** Responses are generated by `llama3.2` and will vary between runs; the app checks that a response is non-empty and usable, but doesn't validate its content beyond that.
- **Single-shot CLI only** - each command requires a new `python main.py ...` invocation; there's no interactive/session mode.

## Maintenance Notes

- All external dependencies are tracked in `requirements.txt` and can be regenerated with `pip freeze > requirements.txt` after installing new packages.
- New CLI commands can be added by defining a new `subparsers.add_parser(...)` block in `build_parser()`, writing a corresponding `handle_*` function, and registering it in the `handlers` dict inside `main()`.
- New model fields should be added to both the class's `__init__` and its `to_dict()`/`from_dict()` methods to keep JSON persistence consistent.