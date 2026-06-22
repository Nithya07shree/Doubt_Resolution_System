import json
from app.agents.base_agent import BaseAgent
from app.logger import get_logger

logger = get_logger("validation_agent")

class ValidationAgent(BaseAgent):
    def run(self, query: str, explanation: str, simplification: str, example: str) -> tuple:
        """
        Evaluates the academic quality, structural completeness, and analogy integration
        of the collective agent responses.
        Returns:
            Tuple of (validation_report_dict, prompt_tokens, completion_tokens)
        """
        system_instruction = (
            "You are a Quality Validation Agent in a multi-agent doubt resolution system.\n"
            "Your job is to critically evaluate the generated explanation, simplification, and example payload.\n\n"
            "Evaluate the content against the following criteria:\n"
            "1. Academic Rigor: Is the Explanation deep, accurate, and structured appropriately?\n"
            "2. Analogy Quality: Does the Simplification contain a clear, explicit physical or real-world analogy?\n"
            "3. Actionability: Is the Example concrete, step-by-step, and easy to visualize (with specific values, code, or math)?\n"
            "4. Completeness: Are there any placeholders, shortcuts (e.g. 'implement later'), or broken transitions?\n\n"
            "You MUST respond ONLY with a JSON object with the following exact keys:\n"
            "- 'valid': boolean (true if overall score >= 80 and no critical components are missing, false otherwise).\n"
            "- 'score': integer from 0 to 100 representing your structural quality evaluation.\n"
            "- 'feedback': A JSON array of string feedback items describing constructive critique or things to improve.\n"
            "Keep feedback extremely actionable and specific. If valid is false, these points will be used as instructions for regeneration."
        )

        user_content = (
            f"Student Query: {query}\n\n"
            f"--- GENERATED ACADEMIC EXPLANATION ---\n{explanation}\n\n"
            f"--- GENERATED SIMPLIFICATION & ANALOGY ---\n{simplification}\n\n"
            f"--- GENERATED CONCRETE EXAMPLE ---\n{example}\n\n"
            "Validate this pipeline payload now."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ]

        fallback_str = json.dumps({
            "valid": True,
            "score": 100,
            "feedback": ["Validation bypassed due to system constraints."]
        })

        content, p_tok, c_tok = self.execute(
            messages=messages,
            system_fallback_msg=fallback_str,
            response_format={"type": "json_object"}
        )

        try:
            parsed_data = json.loads(content)
            for key in ["valid", "score", "feedback"]:
                if key not in parsed_data:
                    raise KeyError(f"Missing key: {key}")
            return parsed_data, p_tok, c_tok
        except Exception as e:
            logger.error(f"Failed to parse ValidationAgent report JSON: {e}. Raw content: {content}")
            return json.loads(fallback_str), p_tok, c_tok
