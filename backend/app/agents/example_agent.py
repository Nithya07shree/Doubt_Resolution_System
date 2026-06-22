from app.agents.base_agent import BaseAgent
from app.logger import get_logger

logger = get_logger("example_agent")

class ExampleAgent(BaseAgent):
    def run(self, query: str, simplified_explanation: str, intent_profile: dict, validation_feedback: str = None) -> tuple:
        """
        Creates a concrete, step-by-step real-world example representing the simplified explanation.
        """
        topic = intent_profile.get("topic", "General")

        system_instruction = (
            "You are an Example Agent in a multi-agent system.\n"
            "Your task is to create a concrete, contextual real-world example matching the simplified explanation.\n\n"
            f"Context Profile:\n"
            f"- Topic: {topic}\n\n"
            "Guidelines:\n"
            "- Design a specific, realistic scenario or step-by-step walk-through (e.g. concrete numbers, code snippets, or physical numbers).\n"
            "- Format with clean, structured Markdown (using headings, bold text, code blocks, or tables).\n"
            "- Ensure it is actionable and helps the student 'visualize' the simplified concept in action.\n"
            "- Avoid abstract hand-waving; provide actual inputs, process steps, and final outputs."
        )

        if validation_feedback:
            system_instruction += (
                f"\n\nCRITICAL FIX REQUIRED (from validation review):\n"
                f"{validation_feedback}\n"
                f"Please adjust the concrete example to address this feedback."
            )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": (
                f"Student Doubt: {query}\n\n"
                f"Simplified Explanation & Analogy:\n{simplified_explanation}\n\n"
                "Please generate a concrete, step-by-step example illustrating this concept."
            )}
        ]

        fallback_msg = (
            "An error occurred while generating the concrete example.\n"
            "Example: Imagine trying to run a sample program but the environment is temporarily loading. "
            "We will restore our interactive examples shortly!"
        )

        return self.execute(
            messages=messages,
            system_fallback_msg=fallback_msg
        )
