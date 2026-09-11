import argparse

from models.user import User
from models.project import Project
from models.task import Task
from services.storage_service import StorageService
from services.ai_client import OllamaChatClient
from services.project_summary_service import ProjectSummaryService


def build_parser():
    # Top-level parser and description shown in --help
    parser = argparse.ArgumentParser(
        prog="project-cli",
        description="Manage users, projects, and tasks from the command line."
    )

    # Enables subcommands like add-user, add-project, etc.
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-user --name <name> --email <email>
    add_user_parser = subparsers.add_parser("add-user", help="Create a new user")
    add_user_parser.add_argument("--name", required=True)
    add_user_parser.add_argument("--email", required=True)

    # add-project --user <name> --title <title> --description <desc> --due-date <date>
    add_project_parser = subparsers.add_parser("add-project", help="Add a project to a user")
    add_project_parser.add_argument("--user", required=True)
    add_project_parser.add_argument("--title", required=True)
    add_project_parser.add_argument("--description", default="")
    add_project_parser.add_argument("--due-date", default=None)

    # list-projects --user <name>
    list_projects_parser = subparsers.add_parser("list-projects", help="List a user's projects")
    list_projects_parser.add_argument("--user", required=True)

    # add-task --project <title> --title <task title> --assigned-to <name>
    add_task_parser = subparsers.add_parser("add-task", help="Add a task to a project")
    add_task_parser.add_argument("--project", required=True)
    add_task_parser.add_argument("--title", required=True)
    add_task_parser.add_argument("--assigned-to", default=None)

    # complete-task --project <title> --task <task title>
    complete_task_parser = subparsers.add_parser("complete-task", help="Mark a task complete")
    complete_task_parser.add_argument("--project", required=True)
    complete_task_parser.add_argument("--task", required=True)

    # summarize-project --project <title> --type summary|risk|next-steps
    summarize_parser = subparsers.add_parser("summarize-project", help="Generate an AI insight for a project")
    summarize_parser.add_argument("--project", required=True)
    summarize_parser.add_argument(
        "--type", choices=["summary", "risk", "next-steps"], default="summary"
    )

    return parser


def find_user(users, name):
    # Look up a user by name in the in-memory list
    for user in users:
        if user.name == name:
            return user
    return None


def find_project(user, title):
    # Look up a project by title within a specific user's projects
    for project in user.projects:
        if project.title == title:
            return project
    return None


def find_project_anywhere(users, title):
    # Search every user's projects for a matching title, since a project
    # title alone doesn't tell us which user owns it
    for user in users:
        project = find_project(user, title)
        if project is not None:
            return project
    return None


def handle_add_user(args, users):
    # Create a new User from the CLI arguments
    user = User(args.name, args.email)

    # Add it to the in-memory list so it gets saved later
    users.append(user)
 
    # Give the user running the CLI immediate feedback
    print(f"Created user: {user.name} ({user.email})")


def handle_add_project(args, users):
    # Find the target user first - can't add a project to someone who doesn't exist
    user = find_user(users, args.user)
    if user is None:
        print(f"Error: no user found with name '{args.user}'")
        return

    # Create the project and attach it to that user
    project = Project(args.title, description=args.description, due_date=args.due_date)
    user.add_project(project)

    print(f"Added project '{project.title}' to user {user.name}")


def handle_list_projects(args, users):
    # Find the target user
    user = find_user(users, args.user)
    if user is None:
        print(f"Error: no user found with name '{args.user}'")
        return

    # Nothing to show if they have no projects yet
    if not user.projects:
        print(f"{user.name} has no projects.")
        return

    # Print each project with a quick task-count summary
    print(f"Projects for {user.name}:")
    for project in user.projects:
        print(f"  - {project.title} ({len(project.tasks)} task(s))")


def handle_add_task(args, users):
    # Look up the project by title across all users
    project = find_project_anywhere(users, args.project)
    if project is None:
        print(f"Error: no project found with title '{args.project}'")
        return

    # Create the task and attach it to the matching project
    task = Task(args.title, assigned_to=args.assigned_to)
    project.add_task(task)

    print(f"Added task '{task.title}' to project '{project.title}'")


def handle_complete_task(args, users):
    # Look up the project by title across all users
    project = find_project_anywhere(users, args.project)
    if project is None:
        print(f"Error: no project found with title '{args.project}'")
        return

    # Look up the task within that project
    task = project.find_task(args.task)
    if task is None:
        print(f"Error: no task found with title '{args.task}' in project '{project.title}'")
        return

    # Goes through the @status.setter, so it's validated
    task.mark_complete()
    print(f"Marked task '{task.title}' complete in project '{project.title}'")


def handle_summarize_project(args, users):
    # Find the project across all users, same as add-task/complete-task
    project = find_project_anywhere(users, args.project)
    if project is None:
        print(f"Error: no project found with title '{args.project}'")
        return

    # Create the AI client and summary service fresh for this one call
    ai_client = OllamaChatClient()
    summary_service = ProjectSummaryService()

    try:
        # This builds the prompt, sends it, validates the response,
        # and formats it (see ProjectSummaryService.generate_insight)
        result = summary_service.generate_insight(ai_client, project, args.type)
        print(result)

    except (ValueError, RuntimeError) as e:
        # Ollama not running, model missing, empty response, etc. =
        # fail gracefully instead of crashing the whole CLI
        print(f"Could not generate {args.type} for '{project.title}': {e}")



# MAIN FUNCTION TYING IT ALL TOGETHER:
def main():
    parser = build_parser()
    args = parser.parse_args()

    # Load existing data at startup
    storage = StorageService()
    users = storage.load_users()

    # Map each subcommand name to its handler function
    handlers = {
        "add-user": handle_add_user,
        "add-project": handle_add_project,
        "list-projects": handle_list_projects,
        "add-task": handle_add_task,
        "complete-task": handle_complete_task,
        "summarize-project": handle_summarize_project,
    }

    handler = handlers[args.command]

    try:
        handler(args, users)
    except ValueError as e:
        # Catches invalid data errors raised from model __init__ methods
        # (e.g. empty name, empty title, bad status)
        print(f"Error: {e}")

    # Save after every command
    storage.save_users(users)


if __name__ == "__main__":
    main()