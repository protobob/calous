import json
import math
import logging
from typing import Dict, Any, List
from asteval import Interpreter
from ..base import FunctionCallingPlugin

logger = logging.getLogger(__name__)

class CalculatorPlugin(FunctionCallingPlugin):
    """
    Calculator Plugin for CALOUS

    Provides safe mathematical calculation functionality for LLM function calling.
    This plugin uses the asteval library for sandboxed evaluation of mathematical expressions.
    Supported math functions include sqrt, sin, cos, log, and operators like +, -, *, /, and ^ (exponentiation).
    This plugin only provides function calling capabilities, not user commands.
    """

    def __init__(self):
        super().__init__(
            name="calculator",
            version="1.0.0",
            description="Provides safe mathematical calculation functionality using a sandboxed evaluator."
        )
        # Set up asteval interpreter with math symbols
        self.asteval = Interpreter(usersyms=math.__dict__)

    def initialize(self) -> bool:
        logger.info("Calculator plugin initialized successfully")
        return True

    def get_function_schemas(self) -> List[Dict[str, Any]]:
        preamble = (
            "You have access to a calculator tool that lets you evaluate mathematical expressions like `2 + 2`, `sqrt(16)`, or `log(10)`.\n"
            "However, you are NOT allowed to use or refer to this tool unless ALL of the following conditions are met:\n\n"
            "1. The user has clearly asked a direct math question.\n"
            "2. The expression is unambiguous and contains numbers or math symbols.\n"
            "3. You are certain the calculator is needed.\n\n"
            "If these conditions are NOT met:\n"
            "- Do NOT use the calculator.\n"
            "- Do NOT mention calculations.\n"
            "- Do NOT simulate tool calls or invent math examples.\n"
            "- Do NOT answer unasked math questions.\n\n"
            "This tool exists for direct, explicit user-initiated math only. You are NOT a math tutor. Do not initiate, infer, or guess math behavior.\n\n"
            "Examples:\n"
            "User: 'What's 3 + 4?' → ✅ Call the calculator with '3 + 4'\n"
            "User: 'Tell me about the moon.' → ❌ Do not mention or use the calculator\n\n"
            "When in doubt, say nothing about math. Obey this strictly.\n\n"
        )
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    # User-facing description (short)
                    "description": "Perform safe mathematical calculations using common math functions and operators.",
                    # LLM-facing description (long, strict preamble)
                    "llm_description": preamble + "Perform safe mathematical calculations. Use common math functions like sqrt, sin, cos, log, and operators like +, -, *, /, ^ (for exponentiation).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Mathematical expression to evaluate (e.g., '2+2', 'sqrt(16)', '3^2')."
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]

    def execute_function(self, function_name: str, **kwargs) -> str:
        result = self.call_function(function_name, kwargs)
        return json.dumps(result, ensure_ascii=False)

    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if function_name != "calculate":
            return {"error": f"Unknown function: {function_name}", "success": False}

        expression = arguments.get("expression", "").strip()

        if not expression:
            return {"error": "Empty expression provided.", "success": False}

        # Replace common human syntax with Python-compatible operators
        expression = expression.replace("^", "**")

        try:
            # Clear previous errors
            self.asteval.error = []
            result = self.asteval(expression)

            if self.asteval.error:
                raise ValueError(
                    "; ".join([err.get_error() for err in self.asteval.error])
                )

            return {"result": result, "expression": expression, "success": True}
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {"error": str(e), "success": False}

    @property
    def is_active(self) -> bool:
        return True
