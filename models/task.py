class Task:
    """Represents a single task that belongs to one Project."""

    STATUS_CHOICES = ("open", "in_progress", "complete")

    def __init__(self, title, status="open", assigned_to=None):
        # Title is required, same validation pattern as User/Project
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")

        self.title = title.strip()
        self.status = status  # goes through the @status.setter below, which validates
        self.assigned_to = assigned_to  # e.g. a contributor's name, or None if unassigned

    @property
    def status(self):
        # Getter - just returns the stored value
        return self._status

    @status.setter
    def status(self, value):
        # Setter - validates before allowing the change
        if value not in self.STATUS_CHOICES:
            raise ValueError(f"Invalid status: {value!r}. Must be one of {self.STATUS_CHOICES}.")
        self._status = value

    def mark_complete(self):
        # Updates this task's status to complete (validated by the setter)
        self.status = "complete"

    def to_dict(self):
        # Serialize this task's own fields - no nested objects here,
        # since Task is the bottom of the hierarchy
        return {
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data):
        # Rebuild the task via __init__ (re-validates title/status too)
        return cls(
            data["title"],
            status=data.get("status", "open"),
            assigned_to=data.get("assigned_to"),
        )

    # Show title, status, and assignee for quick CLI debugging
    def __repr__(self):
        return f"Task(title={self.title!r}, status={self.status!r}, assigned_to={self.assigned_to!r})"