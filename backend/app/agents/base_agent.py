import traceback
import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
from app.logger import get_logger

logger = get_logger("base_agent")

class BaseAgent:
    def __init__(self):
        """Initializes the OpenAI client using environment settings."""
        self.api_key = settings.OPENAI_API_KEY
        # If API key is empty or placeholder, let's log a warning but proceed. 
        # API calls will fail, triggering the graceful fallback code path cleanly.
        if not self.api_key or self.api_key == "your-openai-api-key-here":
            logger.warning("Warning: OPENAI_API_KEY is not configured or contains the default placeholder. Fallbacks will trigger.")
        
        self.client = OpenAI(api_key=self.api_key)

    @retry(
        reraise=True,  # Reraises the last exception to allow the execute method's try/except to capture it
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError))
    )
    def _call_openai(
        self, 
        messages: list, 
        model: str = "gpt-4o-mini", 
        temperature: float = 0.7, 
        response_format: dict = None
    ) -> tuple:
        """
        Inner API execution wrapper configured with tenacity retries 
        specifically for transient RateLimit and Connection errors.
        """
        logger.info(f"Initiating network call to OpenAI API using model: {model}")
        
        kwargs = {}
        if response_format:
            kwargs["response_format"] = response_format

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs
        )
        
        content = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        
        logger.info(f"API call succeeded. Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}")
        return content, prompt_tokens, completion_tokens

    def execute(
        self, 
        messages: list, 
        system_fallback_msg: str, 
        model: str = "gpt-4o-mini", 
        temperature: float = 0.7, 
        response_format: dict = None
    ) -> tuple:
        """
        Public execution wrapper. Wraps network requests in robust error checks.
        If all retries fail, records critical stack trace and serves graceful fallback responses.
        """
        try:
            return self._call_openai(
                messages=messages, 
                model=model, 
                temperature=temperature, 
                response_format=response_format
            )
        except Exception as e:
            tb = traceback.format_exc()
            logger.critical(
                f"BaseAgent critical failure. All retries exhausted or non-retryable error raised. "
                f"Error: {e}\nStack Trace:\n{tb}"
            )
            # Return graceful fallback and 0 token usage
            return system_fallback_msg, 0, 0
