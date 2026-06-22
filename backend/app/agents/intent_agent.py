import json
from app.agents.base_agent import BaseAgent
from app.logger import get_logger

logger = get_logger("intent_agent")

class IntentAgent(BaseAgent):
    def run(self, query: str) -> tuple:
        """
        Analyzes the student query to profile its topic, skill level, and intent type.
        Returns:
            Tuple of (parsed_json_dict, prompt_tokens, completion_tokens)
        """
        system_instruction = (
            "You are an Intent Analysis Agent in a multi-agent system.\n"
            "Your task is to analyze the user's student academic query and profile it.\n"
            "You MUST return a JSON object with the following exact keys:\n"
            "1. 'topic': A short string identifying the core subject/topic (e.g., 'Calculus', 'SQL Databases', 'Quantum Mechanics').\n"
            "2. 'skill_level': Categorize the user's understanding level as one of: 'Beginner', 'Intermediate', or 'Advanced'. Use vocabulary, query structure, and detail level to infer this.\n"
            "3. 'intent_type': Categorize the style of query as one of: 'Conceptual', 'Practical/Troubleshooting', or 'Academic'.\n"
            "4. 'key_terms': A JSON list of 2-5 critical technical keywords or terms from the query.\n"
            "You must respond ONLY with the raw JSON object, no Markdown boxes, no preambles."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Analyze the following student doubt:\n\n{query}"}
        ]

        fallback_str = json.dumps({
            "topic": "General Inquiry",
            "skill_level": "Intermediate",
            "intent_type": "Conceptual",
            "key_terms": ["Inquiry"]
        })

        content, p_tok, c_tok = self.execute(
            messages=messages,
            system_fallback_msg=fallback_str,
            response_format={"type": "json_object"}
        )

        try:
            parsed_data = json.loads(content)
            # Ensure keys exist
            for key in ["topic", "skill_level", "intent_type", "key_terms"]:
                if key not in parsed_data:
                    raise KeyError(f"Missing key: {key}")
            return parsed_data, p_tok, c_tok
        except Exception as e:
            logger.error(f"Failed to parse JSON response from IntentAgent: {e}. Raw content: {content}")
            return json.loads(fallback_str), p_tok, c_tok
