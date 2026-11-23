import os
import json
from typing import Dict, Any, Optional
from app.config import settings
from app.core.logging import logger

class LLMFactory:
    @staticmethod
    def get_client():
        """Retrieve Groq client if API key is configured."""
        if settings.GROQ_API_KEY and len(settings.GROQ_API_KEY.strip()) > 5:
            try:
                from groq import Groq
                return Groq(api_key=settings.GROQ_API_KEY.strip(), timeout=10.0)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
        return None

    @classmethod
    def generate_completion(
        cls,
        system_prompt: str,
        user_prompt: str,
        fallback_generator: callable
    ) -> Dict[str, Any]:
        """Execute LLM prompt with Groq, falling back gracefully to deterministic logic."""
        client = cls.get_client()
        
        if client:
            try:
                logger.info(f"Calling Groq LLM model: {settings.GROQ_MODEL}...")
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1024,
                    response_format={"type": "json_object"}
                )
                raw_content = response.choices[0].message.content
                parsed = json.loads(raw_content)
                parsed["_llm_provider"] = f"groq:{settings.GROQ_MODEL}"
                parsed["_is_fallback"] = False
                return parsed
            except Exception as e:
                logger.warning(f"Groq LLM call failed ({str(e)}). Engaging deterministic local fallback.")

        # Deterministic domain engine fallback
        fallback_result = fallback_generator()
        fallback_result["_llm_provider"] = "deterministic_local_engine"
        fallback_result["_is_fallback"] = True
        return fallback_result

