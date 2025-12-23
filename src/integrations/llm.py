"""LLM integration for intelligent code analysis."""
from typing import Optional, Dict, Any
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import settings

try:
    # Try new LangChain imports first
    try:
        from langchain_community.llms import Ollama
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
    except ImportError:
        # Fallback to old imports
        from langchain.llms import Ollama
        from langchain.chat_models import ChatOpenAI
        from langchain.schema import HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available, LLM features will be limited")

logger = logging.getLogger(__name__)


class LLMIntegration:
    """LLM integration for code analysis."""

    def __init__(self):
        """Initialize LLM integration."""
        self.provider = settings.llm_provider.lower()
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM based on provider."""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, LLM features disabled")
            return

        try:
            if self.provider == "ollama":
                self.llm = Ollama(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_model,
                )
                logger.info(f"Initialized Ollama with model {settings.ollama_model}")
            elif self.provider == "openai":
                if not settings.openai_api_key:
                    logger.warning("OpenAI API key not provided")
                    return
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.3,
                    openai_api_key=settings.openai_api_key,
                )
                logger.info("Initialized OpenAI")
            else:
                logger.warning(f"Unknown LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            self.llm = None

    async def analyze_code(self, code: str, file_path: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze code using LLM.

        Args:
            code: Source code
            file_path: File path
            context: Additional context

        Returns:
            Dictionary with LLM analysis results
        """
        if not self.llm:
            return {
                "success": False,
                "error": "LLM not initialized",
                "suggestions": [],
            }

        try:
            prompt = self._build_prompt(code, file_path, context)
            
            if self.provider == "openai":
                # OpenAI uses ChatOpenAI
                messages = [HumanMessage(content=prompt)]
                response = self.llm(messages)
                result = response.content
            else:
                # Ollama uses regular LLM
                result = self.llm(prompt)

            return {
                "success": True,
                "analysis": result,
                "suggestions": self._extract_suggestions(result),
            }
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": [],
            }

    def _build_prompt(self, code: str, file_path: str, context: Optional[str] = None) -> str:
        """Build prompt for LLM.

        Args:
            code: Source code
            file_path: File path
            context: Additional context

        Returns:
            Prompt string
        """
        prompt = f"""Analyze the following Python code and provide suggestions for improvement.

File: {file_path}

Code:
```python
{code}
```

Please provide:
1. Code quality issues
2. Potential improvements
3. Best practices recommendations
4. Security concerns (if any)

Be concise and actionable in your suggestions.
"""

        if context:
            prompt += f"\nAdditional context: {context}\n"

        return prompt

    def _extract_suggestions(self, llm_response: str) -> list:
        """Extract suggestions from LLM response.

        Args:
            llm_response: LLM response text

        Returns:
            List of suggestions
        """
        # Simple extraction - can be improved with more sophisticated parsing
        suggestions = []
        lines = llm_response.split("\n")
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ["suggest", "recommend", "consider", "should", "improve"]):
                suggestions.append(line.strip())

        return suggestions[:10]  # Limit to 10 suggestions

