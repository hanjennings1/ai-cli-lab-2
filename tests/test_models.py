import pytest

from models.user import User
from models.project import Project
from models.task import Task


class TestUser:
    def test_create_user_success(self):
        user = User("Jordan", "jordan@example.com")
        assert user.name == "Jordan"
        assert user.email == "jordan@example.com"
        assert user.projects == []

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            User("", "jordan@example.com")

    def test_empty_email_raises(self):
        with pytest.raises(ValueError):
            User("Jordan", "")

    def test_add_project(self):
        user = User("Jordan", "jordan@example.com")
        project = Project("Website Redesign")
        user.add_project(project)
        assert project in user.projects

    def test_to_dict_and_from_dict_round_trip(self):
        user = User("Jordan", "jordan@example.com")
        project = Project("Website Redesign", description="Redo homepage")
        user.add_project(project)

        data = user.to_dict()
        rebuilt = User.from_dict(data)

        assert rebuilt.name == user.name
        assert rebuilt.email == user.email
        assert len(rebuilt.projects) == 1
        assert rebuilt.projects[0].title == "Website Redesign"


class TestProject:
    def test_create_project_success(self):
        project = Project("Website Redesign", description="Redo homepage", due_date="2026-10-01")
        assert project.title == "Website Redesign"
        assert project.description == "Redo homepage"
        assert project.due_date == "2026-10-01"
        assert project.tasks == []

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Project("")

    def test_project_gets_unique_id(self):
        project_a = Project("Project A")
        project_b = Project("Project B")
        assert project_a.id != project_b.id

    def test_add_task(self):
        project = Project("Website Redesign")
        task = Task("Wireframe homepage")
        project.add_task(task)
        assert task in project.tasks

    def test_find_task_found(self):
        project = Project("Website Redesign")
        task = Task("Wireframe homepage")
        project.add_task(task)

        found = project.find_task("Wireframe homepage")
        assert found is task

    def test_find_task_not_found(self):
        project = Project("Website Redesign")
        found = project.find_task("Nonexistent task")
        assert found is None

    def test_to_dict_and_from_dict_round_trip(self):
        project = Project("Website Redesign", description="Redo homepage", due_date="2026-10-01")
        task = Task("Wireframe homepage", assigned_to="Jordan")
        project.add_task(task)

        data = project.to_dict()
        rebuilt = Project.from_dict(data)

        assert rebuilt.title == project.title
        assert rebuilt.id == project.id  # confirms the id is preserved, not reassigned
        assert len(rebuilt.tasks) == 1
        assert rebuilt.tasks[0].title == "Wireframe homepage"
        assert rebuilt.tasks[0].assigned_to == "Jordan"


class TestTask:
    def test_create_task_success(self):
        task = Task("Wireframe homepage", assigned_to="Jordan")
        assert task.title == "Wireframe homepage"
        assert task.status == "open"
        assert task.assigned_to == "Jordan"

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Task("")

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError):
            Task("Wireframe homepage", status="not-a-real-status")

    def test_mark_complete(self):
        task = Task("Wireframe homepage")
        task.mark_complete()
        assert task.status == "complete"

    def test_status_setter_rejects_invalid_value(self):
        task = Task("Wireframe homepage")
        with pytest.raises(ValueError):
            task.status = "not-a-real-status"

    def test_to_dict_and_from_dict_round_trip(self):
        task = Task("Wireframe homepage", status="in_progress", assigned_to="Jordan")

        data = task.to_dict()
        rebuilt = Task.from_dict(data)

        assert rebuilt.title == task.title
        assert rebuilt.status == task.status
        assert rebuilt.assigned_to == task.assigned_to