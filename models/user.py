from models.project import Project

class User:
    """Represents a single user (admin-managed) who owns zero or more Projects.

    Relationship: User -> Project is one-to-many.
    """

    def __init__(self, name, email):
        # Validate before assigning anything to self 
        # reject empty or whitespace-only values so 'bad data' never enters the system
        if not name or not name.strip():
            raise ValueError("User name cannot be empty.")
        if not email or not email.strip():
            raise ValueError("User email cannot be empty.")

        # Store the stripped versions 
        # so downstream code (display, comparisons, JSON) never has to worry about stray whitespace
        self.name = name.strip()
        self.email = email.strip()

        # Every user starts with no projects. Must be created fresh here
        # (never as a default argument) so instances don't share one list
        self.projects = []

    # Append project to this user's list
    def add_project(self, project):
        self.projects.append(project)

    # Recursively serialize nested projects/tasks for JSON
    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "projects": [project.to_dict() for project in self.projects],
        }


    @classmethod
    def from_dict(cls, data):
        # Rebuild the user via __init__ (re-validates the data too)
        user = cls(data["name"], data["email"])

        # Rebuild each nested project, then attach it
        for project_data in data["projects"]:
            project = Project.from_dict(project_data)
            user.add_project(project)

        return user