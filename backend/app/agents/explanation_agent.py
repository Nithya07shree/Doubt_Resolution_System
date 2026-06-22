from app.agents.base_agent import BaseAgent
from app.logger import get_logger

logger = get_logger("explanation_agent")

class ExplanationAgent(BaseAgent):
    def run(self, query: str, intent_profile: dict, validation_feedback: str = None) -> tuple:
        """
        Generates a comprehensive, detailed, and technically rigorous academic explanation.
        Tailors explanation depth based on the student's profiled skill level.
        Includes optional validation feedback for the internal retry loop.
        """
        topic = intent_profile.get("topic", "General")
        skill_level = intent_profile.get("skill_level", "Intermediate")
        intent_type = intent_profile.get("intent_type", "Conceptual")
        key_terms = ", ".join(intent_profile.get("key_terms", []))

        system_instruction = (
            "You are an Explanation Agent in a multi-agent doubt resolution system.\n"
            "Your task is to provide a highly comprehensive, detailed, technically rigorous, and formal academic explanation of the student's doubt.\n\n"
            f"Context Profile:\n"
            f"- Topic: {topic}\n"
            f"- Student Skill Level: {skill_level} (Provide appropriate mathematical/technical rigor for this level, but err on the side of depth)\n"
            f"- Intent Classification: {intent_type}\n"
            f"- Core Technical Terms to address: {key_terms}\n\n"
            "Guidelines:\n"
            "- Dive deep into the underlying mechanics. Be technically exact and authoritative.\n"
            "- Use precise notation, definitions, or architectural diagrams where applicable.\n"
            "- Format your response beautifully using clean Markdown (headings, bullet points, code blocks).\n"
            "- Do NOT simplify or use casual analogies here. Focus on the core engineering or scientific theory."
        )

        if validation_feedback:
            system_instruction += (
                f"\n\nCRITICAL FIX REQUIRED (from validation review):\n"
                f"{validation_feedback}\n"
                f"Please revise your detailed academic response to address these specific shortcomings."
            )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Please provide a rigorous academic explanation for this student doubt:\n\n{query}"}
        ]

        fallback_msg = (
            "An error occurred while generating the detailed academic explanation.\n"
            f"Core Topic: {topic}\n"
            "Please verify your connection and query. We apologize for the inconvenience."
        )

        return self.execute(
            messages=messages,
            system_fallback_msg=fallback_msg
        )
