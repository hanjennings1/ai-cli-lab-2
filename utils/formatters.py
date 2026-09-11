def format_project_line(project):
    # Shared one-line display format for a project, used anywhere
    # the CLI needs to list projects (currently just list-projects)
    return f"  - {project.title} ({len(project.tasks)} task(s))"