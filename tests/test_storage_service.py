import json

from models.user import User
from models.project import Project
from services.storage_service import StorageService
from models.task import Task


class TestStorageService:
    def test_load_users_no_file_returns_empty_list(self, tmp_path):
        filepath = tmp_path / "does_not_exist.json"
        storage = StorageService(filepath=str(filepath))

        users = storage.load_users()

        assert users == []

    def test_load_users_malformed_json_returns_empty_list(self, tmp_path, capsys):
        filepath = tmp_path / "broken.json"
        filepath.write_text("")  # empty file / invalid JSON

        storage = StorageService(filepath=str(filepath))
        users = storage.load_users()

        assert users == []

        # Confirm a warning was actually printed, not just skipped without any feedback.
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_load_users_with_valid_data(self, tmp_path):
        filepath = tmp_path / "data.json"
        raw_data = [
            {
                "name": "Jordan",
                "email": "jordan@example.com",
                "projects": [],
            }
        ]
        filepath.write_text(json.dumps(raw_data))

        storage = StorageService(filepath=str(filepath))
        users = storage.load_users()

        assert len(users) == 1
        assert users[0].name == "Jordan"
        assert users[0].email == "jordan@example.com"

    def test_save_users_writes_valid_json(self, tmp_path):
        filepath = tmp_path / "data.json"
        storage = StorageService(filepath=str(filepath))

        user = User("Jordan", "jordan@example.com")
        project = Project("Website Redesign")
        user.add_project(project)

        storage.save_users([user])

        # Confirm the file actually exists and contains valid, correct JSON
        assert filepath.exists()
        saved_data = json.loads(filepath.read_text())
        assert len(saved_data) == 1
        assert saved_data[0]["name"] == "Jordan"
        assert saved_data[0]["projects"][0]["title"] == "Website Redesign"

    def test_save_users_creates_missing_directory(self, tmp_path):
        # A nested path that doesn't exist yet - tests the os.makedirs() call
        filepath = tmp_path / "nested" / "folder" / "data.json"
        storage = StorageService(filepath=str(filepath))

        storage.save_users([])

        assert filepath.exists()

    def test_save_then_load_round_trip(self, tmp_path):
        filepath = tmp_path / "data.json"
        storage = StorageService(filepath=str(filepath))

        user = User("Jordan", "jordan@example.com")
        project = Project("Website Redesign", description="Redo homepage")
        task = Task("Wireframe homepage", assigned_to="Jordan")
        project.add_task(task)
        user.add_project(project)

        storage.save_users([user])
        reloaded_users = storage.load_users()

        assert len(reloaded_users) == 1
        assert reloaded_users[0].name == "Jordan"
        assert len(reloaded_users[0].projects) == 1
        assert reloaded_users[0].projects[0].title == "Website Redesign"
        assert len(reloaded_users[0].projects[0].tasks) == 1
        assert reloaded_users[0].projects[0].tasks[0].title == "Wireframe homepage"