import pytest

from models.project import Project
from models.task import Task
from services.project_summary_service import ProjectSummaryService


class TestProjectSummaryService:
    def test_build_prompt_rejects_invalid_type(self):
        service = ProjectSummaryService()
        project = Project("Website Redesign")

        with pytest.raises(ValueError):
            service.build_prompt(project, "not-a-real-type")

    def test_build_prompt_includes_project_data(self):
        service = ProjectSummaryService()
        project = Project("Website Redesign", description="Redo homepage", due_date="2026-10-01")
        task = Task("Wireframe homepage", assigned_to="Jordan")
        project.add_task(task)

        prompt = service.build_prompt(project, "summary")

        assert "Website Redesign" in prompt
        assert "Redo homepage" in prompt
        assert "2026-10-01" in prompt
        assert "Wireframe homepage" in prompt
        assert "Jordan" in prompt

    def test_build_prompt_handles_empty_project(self):
        service = ProjectSummaryService()
        project = Project("Empty Project")  # no description, due_date, or tasks

        prompt = service.build_prompt(project, "summary")

        assert "Empty Project" in prompt
        assert "None provided" in prompt  # fallback text for missing description
        assert "Not set" in prompt        # fallback text for missing due_date
        assert "no tasks yet" in prompt

    def test_build_prompt_varies_by_type(self):
        service = ProjectSummaryService()
        project = Project("Website Redesign")

        summary_prompt = service.build_prompt(project, "summary")
        risk_prompt = service.build_prompt(project, "risk")
        next_steps_prompt = service.build_prompt(project, "next-steps")

        # Each type should produce genuinely different instructions
        assert summary_prompt != risk_prompt
        assert risk_prompt != next_steps_prompt

    def test_is_usable_response_true_for_real_text(self):
        service = ProjectSummaryService()
        assert service.is_usable_response("This is a real summary.") is True

    def test_is_usable_response_false_for_empty_or_blank(self):
        service = ProjectSummaryService()
        assert service.is_usable_response("") is False
        assert service.is_usable_response("   ") is False
        assert service.is_usable_response(None) is False

    def test_format_output_includes_correct_heading(self):
        service = ProjectSummaryService()

        summary_output = service.format_output("Some text", "summary")
        risk_output = service.format_output("Some text", "risk")
        next_steps_output = service.format_output("Some text", "next-steps")

        assert "Project Summary" in summary_output
        assert "Risk Notes" in risk_output
        assert "Suggested Next Steps" in next_steps_output

    def test_format_output_strips_whitespace(self):
        service = ProjectSummaryService()
        result = service.format_output("   Text with padding   ", "summary")

        assert "Text with padding" in result
        assert "   Text with padding   " not in result  # confirms it was stripped

    def test_generate_insight_returns_formatted_result(self):
        service = ProjectSummaryService()
        project = Project("Website Redesign")
        task = Task("Wireframe homepage", assigned_to="Jordan")
        project.add_task(task)

        class FakeAIClient:
            def send(self, prompt):
                return "This project is progressing well."

        result = service.generate_insight(FakeAIClient(), project, "summary")

        assert "Project Summary" in result
        assert "This project is progressing well." in result

    def test_generate_insight_raises_on_unusable_response(self):
        service = ProjectSummaryService()
        project = Project("Website Redesign")

        class FakeAIClient:
            def send(self, prompt):
                return "   "  # blank/unusable

        with pytest.raises(RuntimeError):
            service.generate_insight(FakeAIClient(), project, "summary")

    def test_generate_insight_propagates_client_failure(self):
        service = ProjectSummaryService()
        project = Project("Website Redesign")

        class FakeAIClient:
            def send(self, prompt):
                raise RuntimeError("AI service request failed.")

        with pytest.raises(RuntimeError):
            service.generate_insight(FakeAIClient(), project, "summary")