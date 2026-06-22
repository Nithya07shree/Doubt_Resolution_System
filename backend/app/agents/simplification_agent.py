from app.agents.base_agent import BaseAgent
from app.logger import get_logger

logger = get_logger("simplification_agent")

class SimplificationAgent(BaseAgent):
    def run(self, query: str, academic_explanation: str, intent_profile: dict, validation_feedback: str = None) -> tuple:
        """
        Translates a detailed academic explanation into friendly, plain English.
        MUST frame the core concept around a clear and relatable real-world analogy.
        """
        topic = intent_profile.get("topic", "General")
        skill_level = intent_profile.get("skill_level", "Intermediate")

        system_instruction = (
            "You are a Simplification Agent in a multi-agent system.\n"
            "Your task is to take a highly complex academic explanation and translate it into a friendly, accessible, plain-prose explanation suitable for a student.\n\n"
            f"Context Profile:\n"
            f"- Topic: {topic}\n"
            f"- Targeted Student Understanding: {skill_level}\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. You MUST frame your simplified explanation around a creative, easy-to-understand physical analogy (e.g. comparing databases to library cards, CPUs to a kitchen chef, etc.).\n"
            "2. Make the tone highly encouraging, clear, and conversational, while remaining technically accurate.\n"
            "3. Structure your response using clean Markdown with distinct sections. One section should be titled '### The Analogy'.\n"
            "4. Keep it relatively concise but engaging."
        )

        if validation_feedback:
            system_instruction += (
                f"\n\nCRITICAL FIX REQUIRED (from validation review):\n"
                f"{validation_feedback}\n"
                f"Please update your simplification and analogy to address these issues."
            )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": (
                f"Student Query: {query}\n\n"
                f"Rigorous Academic Explanation:\n{academic_explanation}\n\n"
                "Please simplify this explanation and explain it using a strong physical analogy."
            )}
        ]

        fallback_msg = (
            "An error occurred while generating the simplified explanation.\n"
            "Analogy: Imagine a teacher translating a big, heavy textbook into a simple, friendly discussion. "
            "We are working to bring that friendly explanation back online shortly!"
        )

        return self.execute(
            messages=messages,
            system_fallback_msg=fallback_msg
        )
