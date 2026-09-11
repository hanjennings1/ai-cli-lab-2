from models.task import Task


class Project:
    """Represents a project owned by a single User, containing zero or more Tasks.

    Relationship: Project -> Task is one-to-many.
    """

    def __init__(self, title, description="", due_date=None):
        # Only title is required - description/due_date are optional
        if not title or not title.strip():
            raise ValueError("Project title cannot be empty.")

        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.due_date = due_date  # kept as a plain string, e.g. "2026-09-30"
        self.tasks = []

    def add_task(self, task):
        # Append task to this project's list
        self.tasks.append(task)

    def find_task(self, title):
        # Search this project's tasks for one matching the given title
        for task in self.tasks:
            if task.title == title:
                return task

        # No match found in the loop - explicitly return None
        return None

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        # Rebuild the project via __init__ (re-validates the data too)
        project = cls(
            data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
        )

        # Rebuild each nested task, then attach it
        for task_data in data["tasks"]:
            task = Task.from_dict(task_data)
            project.add_task(task)

        return project