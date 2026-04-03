"""
LLM Service - Gemini Integration.
"""

from dataclasses import dataclass
from typing import AsyncIterator, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    content: str
    raw_response: Optional[dict] = None


@dataclass
class StreamChunk:
    text: str
    is_final: bool = False


class LLMService:
    """Gemini LLM service for text generation."""

    def __init__(self):
        self._client = None
        self._model = None

    def _get_client(self):
        """Get or initialize Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                self._client = genai
                self._model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("Gemini client initialized")
            except ImportError:
                logger.error("google-generativeai not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        return self._client, self._model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text response from LLM."""
        try:
            _, model = self._get_client()
            if not model:
                return LLMResponse(content="LLM service not available")

            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }

            if system_instruction:
                model = model.start()

            response = await model.generate_content_async(
                prompt, generation_config=generation_config
            )

            return LLMResponse(
                content=response.text,
                raw_response=response.to_dict()
                if hasattr(response, "to_dict")
                else None,
            )

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return LLMResponse(content=f"Error: {str(e)}")

    async def generate_streaming(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamChunk]:
        """Generate streaming text response."""
        try:
            _, model = self._get_client()
            if not model:
                yield StreamChunk(text="LLM service not available")
                return

            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }

            response = await model.generate_content_async(
                prompt, generation_config=generation_config, stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield StreamChunk(text=chunk.text)

            yield StreamChunk(text="", is_final=True)

        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            yield StreamChunk(text=f"Error: {str(e)}", is_final=True)

    def generate_sync(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Synchronous text generation."""
        try:
            _, model = self._get_client()
            if not model:
                return LLMResponse(content="LLM service not available")

            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }

            response = model.generate_content(
                prompt, generation_config=generation_config
            )

            return LLMResponse(
                content=response.text,
                raw_response=response.to_dict()
                if hasattr(response, "to_dict")
                else None,
            )

        except Exception as e:
            logger.error(f"LLM sync generation failed: {e}")
            return LLMResponse(content=f"Error: {str(e)}")


llm_service = LLMService()
