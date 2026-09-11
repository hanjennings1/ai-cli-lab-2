from models.person import Person
from models.project import Project


class User(Person):     #Inherits from Person class instead
    """Represents a single user (admin-managed) who owns zero or more Projects.

    Relationship: User -> Project is one-to-many.
    """

    def __init__(self, name, email):
        # Person.__init__ handles name/email validation and assignment
        super().__init__(name, email)
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


    # Show name, email, and project count for quick CLI debugging
    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, projects={len(self.projects)})"