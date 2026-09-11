class ProjectSummaryService:
    """Builds prompts and formats output for AI-generated project insights.

    Supports three types of output: a project summary, a risk note, and
    a next-step suggestion - all built from the same project/task data.
    """

    VALID_TYPES = ("summary", "risk", "next-steps")

    def _project_context(self, project):
        # Turn a Project object's data into a plain-text block the model can read
        lines = [
            f"Project: {project.title}",
            f"Description: {project.description or 'None provided'}",
            f"Due date: {project.due_date or 'Not set'}",
            "Tasks:",
        ]

        if not project.tasks:
            lines.append("  (no tasks yet)")
        else:
            for task in project.tasks:
                assignee = task.assigned_to or "Unassigned"
                lines.append(f"  - {task.title} [{task.status}] (assigned to: {assignee})")

        return "\n".join(lines)


    def build_prompt(self, project, summary_type):
        # Validate the requested type before building anything
        if summary_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid summary_type: {summary_type!r}. Must be one of {self.VALID_TYPES}."
            )

        # Shared project/task data, reused across all three prompt types
        context = self._project_context(project)

        # Type-specific instructions for the model
        if summary_type == "summary":
            instructions = (
                "Write a concise project summary covering overall progress, "
                "what's been completed, and what's still open."
            )
        elif summary_type == "risk":
            instructions = (
                "Identify potential risks to this project - overdue or "
                "unassigned tasks, unclear ownership, or scope concerns."
            )
        else:  # "next-steps"
            instructions = (
                "Suggest concrete next steps the team should take to move "
                "this project forward, based on the current task statuses."
            )

        return (
            "You are assisting with project management for a software team.\n"
            f"{instructions}\n\n"
            f"Here is the project data:\n{context}\n\n"
            "Base your response only on the data provided - do not invent "
            "details that aren't present."
        )


    def is_usable_response(self, response_text):
        # A usable response just needs to be non-empty text
        if not response_text or not response_text.strip():
            return False
        return True


    def format_output(self, response_text, summary_type):
        # Pick a heading based on which type of insight this is
        headings = {
            "summary": "Project Summary",
            "risk": "Risk Notes",
            "next-steps": "Suggested Next Steps",
        }
        heading = headings[summary_type]

        return f"\n{heading}\n{response_text.strip()}\n"


    def generate_insight(self, ai_client, project, summary_type):
        # Build the prompt from the project data and requested type
        prompt = self.build_prompt(project, summary_type)

        # Send it through the AI client
        response = ai_client.send(prompt)

        # Reject unusable responses before formatting/returning anything
        if not self.is_usable_response(response):
            raise RuntimeError("AI response was empty or unusable.")

        # Return the formatted, ready-to-display result
        return self.format_output(response, summary_type)