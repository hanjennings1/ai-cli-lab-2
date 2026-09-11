from models.task import Task


class Project:
    """Represents a project owned by a single User, containing zero or more Tasks.

    Relationship: Project -> Task is one-to-many.
    """

    next_id = 1     # class attribute - shared counter across ALL Project instances

    def __init__(self, title, description="", due_date=None):
        # Only title is required - description/due_date are optional
        if not title or not title.strip():
            raise ValueError("Project title cannot be empty.")

        # Assign this project the current counter value, then bump it
        # so the next project created gets a different id
        self.id = Project.next_id
        Project.next_id += 1

        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.due_date = due_date
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
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [task.to_dict() for task in self.tasks],
        }


    @classmethod
    def from_dict(cls, data):
        # Rebuild the project via __init__ (this assigns a new auto id)
        project = cls(
            data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
        )

        # Overwrite with the original saved id, so it doesn't change on reload
        project.id = data["id"]

        # Keep the shared counter ahead of any id loaded from file,
        # so future new projects never collide with a loaded id
        if data["id"] >= Project.next_id:
            Project.next_id = data["id"] + 1

        # Rebuild each nested task, then attach it
        for task_data in data["tasks"]:
            task = Task.from_dict(task_data)
            project.add_task(task)

        return project


    # Show title and task count for quick CLI debugging
    def __repr__(self):
        return f"Project(title={self.title!r}, tasks={len(self.tasks)})"