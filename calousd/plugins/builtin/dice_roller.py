"""
Dice Roller Plugin for CALOUS

Provides D&D-style dice rolling functionality for LLM function calling.
This plugin only provides function calling capabilities, not user commands.
"""

import json
import random
import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

from ..base import FunctionCallingPlugin, PluginCapability

logger = logging.getLogger(__name__)


class DiceRollResult:
    def __init__(self, expression: str):
        self.expression = expression
        self.total = 0
        self.rolls = []
        self.roll_groups = []
        self.modifier = 0
        self.breakdown = ""
        self.success = True
        self.error = ""
        self.summary = ""

    def to_dict(self, verbose: bool = False) -> Dict[str, Any]:
        result = {
            "result": self.total,
            "expression": self.expression,
            "rolls": self.rolls,
            "roll_groups": self.roll_groups,
            "modifiers": self.modifier if self.modifier != 0 else None,
            "success": self.success,
            "summary": self.summary,
        }
        if verbose:
            result["breakdown"] = self.breakdown
        return result


class DiceRollerPlugin(FunctionCallingPlugin):
    DICE_PATTERN = r'(\d*)d(\d+)([+-]\d+)?'

    def __init__(self):
        super().__init__(
            name="dice_roller",
            version="2.0.0",
            description="Provides D&D-style dice rolling functionality"
        )

    def initialize(self) -> bool:
        logger.info("Dice roller plugin initialized successfully")
        return True

    def get_function_schemas(self) -> List[Dict[str, Any]]:
        return [{
            "type": "function",
            "function": {
                "name": "roll_dice",
                "description": "Roll dice using D&D style notation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dice_expression": {
                            "type": "string",
                            "description": "Dice expression (e.g., '2d6+3', '1d20+2d4-5')"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Include breakdown",
                            "default": False
                        }
                    },
                    "required": ["dice_expression"]
                }
            }        }]

    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if function_name != "roll_dice":
            return {"error": f"Unknown function: {function_name}", "success": False}

        expr = arguments.get("dice_expression", "").strip().lower().replace(" ", "")
        verbose = arguments.get("verbose", False)

        if not expr or not re.search(r'd\d+', expr):
            return {"error": "Invalid or empty dice expression.", "success": False}

        if expr.count('d') > 10:
            return {"error": "Expression too complex (max 10 dice sets).", "success": False}

        if not re.match(r'^[\d+d+\-]+$', expr):
            return {"error": "Illegal characters in expression.", "success": False}

        try:
            result = self._roll(expr, verbose)
            result["meta"] = {
                "timestamp": datetime.now().isoformat(),
                "complex_expression": not re.fullmatch(self.DICE_PATTERN, expr),
                "verbose_output": verbose
            }
            return result
        except Exception as e:
            return {"error": str(e), "success": False}

    def _roll(self, expr: str, verbose: bool) -> Dict[str, Any]:
        if re.fullmatch(self.DICE_PATTERN, expr):
            return self._roll_simple(expr, verbose)
        return self._roll_complex(expr, verbose)

    def _roll_simple(self, expr: str, verbose: bool) -> Dict[str, Any]:
        match = re.fullmatch(self.DICE_PATTERN, expr)
        if not match:
            return {"error": f"Invalid expression: {expr}", "success": False}

        count, sides, mod = match.groups()
        count = int(count) if count else 1
        sides = int(sides)
        modifier = int(mod) if mod else 0

        if not (1 <= count <= 100 and 1 <= sides <= 1000):
            return {"error": "Dice count/sides out of bounds.", "success": False}

        rolls = [random.randint(1, sides) for _ in range(count)]
        subtotal = sum(rolls)
        total = subtotal + modifier

        result = DiceRollResult(expr)
        result.total = total
        result.rolls = rolls
        result.modifier = modifier
        result.roll_groups.append({
            "dice": f"{count}d{sides}",
            "count": count,
            "sides": sides,
            "rolls": rolls,
            "subtotal": subtotal
        })
        if verbose:
            mod_str = f" {'+' if modifier >= 0 else '-'} {abs(modifier)}"
            result.breakdown = f"{count}d{sides}: {rolls} = {subtotal}{mod_str} = {total}"
        result.summary = f"Rolled {expr} = {total}"
        return result.to_dict(verbose)

    def _roll_complex(self, expr: str, verbose: bool) -> Dict[str, Any]:
        parts = re.findall(r'([+-]?\d*d\d+|[+-]?\d+)', expr)
        result = DiceRollResult(expr)

        for part in parts:
            if 'd' in part:
                sign = -1 if part.startswith('-') else 1
                part = part.lstrip('+-')
                count_str, sides_str = part.split('d')
                count = int(count_str) if count_str else 1
                sides = int(sides_str)
                if not (1 <= count <= 100 and 1 <= sides <= 1000):
                    return {"error": "Dice count/sides out of bounds.", "success": False}

                rolls = [random.randint(1, sides) for _ in range(count)]
                subtotal = sum(rolls) * sign
                result.total += subtotal
                result.rolls.extend([r * sign for r in rolls])
                result.roll_groups.append({
                    "dice": f"{'-' if sign == -1 else ''}{count}d{sides}",
                    "count": count,
                    "sides": sides,
                    "rolls": [r * sign for r in rolls],
                    "subtotal": subtotal
                })
                if verbose:
                    result.breakdown += f" {'-' if sign == -1 else '+'} {count}d{sides}: {rolls} = {subtotal}"  
            else:
                mod = int(part)
                result.total += mod
                result.modifier += mod
                if verbose:
                    result.breakdown += f" {'+' if mod >= 0 else '-'} {abs(mod)}"

        result.summary = f"Rolled {expr} = {result.total}"
        if verbose:
            result.breakdown += f" = {result.total}"
        return result.to_dict(verbose)

    @property
    def is_active(self) -> bool:
        return True
