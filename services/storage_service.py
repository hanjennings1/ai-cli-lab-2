import json
import os

from models.user import User


class StorageService:
    """Owns reading/writing the app's JSON data file.

    Knows nothing about CLI commands or AI prompts - only how to persist
    and load a list of User objects (with their nested Projects/Tasks).
    """

    def __init__(self, filepath="data/project_data.json"):
        self.filepath = filepath

    def load_users(self):
        # No file yet - start empty
        if not os.path.exists(self.filepath):
            return []

        # Read JSON and rebuild User objects (with nested Projects/Tasks)
        with open(self.filepath, "r") as f:
            data = json.load(f)

        return [User.from_dict(user_data) for user_data in data]

    def save_users(self, users):
        # Make sure the data/ folder exists
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Serialize each user (and nested projects/tasks) to a dict
        data = [user.to_dict() for user in users]

        # Write it all out as formatted JSON
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)