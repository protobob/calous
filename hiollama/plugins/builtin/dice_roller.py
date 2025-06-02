"""
Dice Roller Plugin for HiOllama

Provides D&D-style dice rolling functionality for LLM function calling.
This plugin only provides function calling capabilities, not user commands.
"""

import json
import random
import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from ..base import FunctionCallingPlugin, PluginCapability

logger = logging.getLogger(__name__)


class ParsedDiceRoll:
    """Represents a parsed dice roll expression with results."""
    
    def __init__(self, expression: str):
        self.original_expression = expression
        self.parsed_expression = ""
        self.dice_sets = []  # List of (count, sides) tuples
        self.modifiers = []  # List of (operator, value) tuples
        self.rolls = []      # List of individual dice roll results
        self.total = 0
        self.breakdown = ""  # Human-readable breakdown
        self.valid = False


class DiceRollerPlugin(FunctionCallingPlugin):
    """D&D style dice roller plugin."""
    
    # Regular expression pattern for dice notation (e.g. 2d6+3, d20-2)
    DICE_PATTERN = r'(\d*)d(\d+)([+-]\d+)?'
    
    # Complex dice pattern for multiple dice sets (e.g. 2d6+1d8+3)
    COMPLEX_DICE_PATTERN = r'((\d*)d(\d+))([+-](\d*)d(\d+)|[+-]\d+)*'
    
    def __init__(self):
        super().__init__(
            name="dice_roller",
            version="1.1.0",
            description="Provides D&D-style dice rolling functionality"
        )
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        logger.info("Dice roller plugin initialized successfully")
        return True    
        
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Return OpenAI function calling schemas for this plugin."""
        return [{
            "type": "function",
            "function": {
                "name": "roll_dice",
                "description": "Roll dice using D&D style notation for tabletop RPGs. Supports simple expressions (2d6+3) and complex ones (1d20+2d4-5).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dice_expression": {
                            "type": "string",
                            "description": "The dice expression to roll. Examples: '2d6+3' (two six-sided dice plus 3), 'd20' (one twenty-sided die), '4d8-2' (four eight-sided dice minus 2), '1d20+2d4' (one twenty-sided die plus two four-sided dice)"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Whether to include detailed breakdown of each die roll in the result",
                            "default": False
                        }
                    },
                    "required": ["dice_expression"]
                }
            }
        }]
    
    def execute_function(self, function_name: str, **kwargs) -> str:
        """Execute a function call and return the result as a string."""
        result = self.call_function(function_name, kwargs)
        return json.dumps(result, ensure_ascii=False)
    
    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call."""
        if function_name != "roll_dice":
            return {
                "error": f"Unknown function: {function_name}",
                "success": False
            }
        
        # Input validation and normalization
        dice_expression = arguments.get("dice_expression", "").strip()
        verbose = arguments.get("verbose", False)
        
        if not dice_expression:
            return {
                "error": "Dice expression cannot be empty",
                "success": False
            }
        
        # Basic validation of dice expression format
        if not re.search(r'd\d+', dice_expression):
            return {
                "error": f"Invalid dice expression format: {dice_expression}. Must include at least one dice notation (e.g., d6, 2d20)",
                "success": False,
                "help": "Examples of valid expressions: d20, 2d6+3, 1d20+2d4-5"
            }
        
        # Check for excessively complex expressions
        if dice_expression.count('d') > 10:
            return {
                "error": f"Dice expression too complex: {dice_expression}. Maximum 10 dice sets allowed.",
                "success": False
            }
            
        try:
            result = self._roll_dice(dice_expression, verbose)
            
            # Add metadata for better understanding
            result["meta"] = {
                "timestamp": self._get_timestamp(),
                "complex_expression": not self._is_simple_expression(dice_expression.lower().replace(" ", "")),
                "verbose_output": verbose
            }
            
            return result
        except Exception as e:
            logger.error(f"Error rolling dice: {e}")
            return {
                "error": f"Error rolling dice: {str(e)}",
                "success": False,
                "help": "Try a simpler dice expression or check your syntax"
            }
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _roll_dice(self, dice_expression: str, verbose: bool = False) -> Dict[str, Any]:
        """Roll dice according to the provided expression."""
        # Normalize expression: remove spaces, convert D to d
        normalized = dice_expression.lower().replace(" ", "")
        
        # Additional validation
        # Check for invalid characters
        if re.search(r'[^0-9d\+\-]', normalized):
            return {
                "error": f"Invalid characters in dice expression: {dice_expression}",
                "success": False,
                "help": "Only numbers, 'd', '+', and '-' are allowed"
            }
        
        # Check for basic syntax errors
        if normalized.endswith('+') or normalized.endswith('-'):
            return {
                "error": f"Dice expression cannot end with an operator: {dice_expression}",
                "success": False
            }
        
        if '++' in normalized or '--' in normalized or '+-' in normalized or '-+' in normalized:
            return {
                "error": f"Invalid operator sequence in: {dice_expression}",
                "success": False
            }
        
        # Handle simple dice roll first (e.g., "d20", "3d6+2")
        if self._is_simple_expression(normalized):
            return self._roll_simple_dice(normalized, verbose)
        
        # Handle complex dice expressions (e.g., "2d6+1d8+3")
        return self._roll_complex_dice(normalized, verbose)
    
    def _is_simple_expression(self, expression: str) -> bool:
        """Check if this is a simple dice expression (single dice type + optional modifier)."""
        pattern = re.compile(f'^{self.DICE_PATTERN}$')
        return bool(pattern.match(expression))
    
    def _roll_simple_dice(self, expression: str, verbose: bool) -> Dict[str, Any]:
        """Roll a simple dice expression."""
        match = re.match(f'^{self.DICE_PATTERN}$', expression)
        
        if not match:
            return {
                "error": f"Invalid dice expression: {expression}",
                "success": False
            }
        
        # Parse the expression
        count_str, sides_str, modifier_str = match.groups()
        
        # Get the count (default to 1 if not specified)
        count = int(count_str) if count_str else 1
        
        # Get the sides
        sides = int(sides_str)
        
        # Get the modifier (default to 0 if not specified)
        modifier = 0
        if modifier_str:
            modifier = int(modifier_str)
        
        # Enhanced validation
        if count <= 0 or count > 100:  # Prevent excessive dice rolling
            return {
                "error": f"Invalid dice count: {count} (must be between 1 and 100)",
                "success": False
            }
        
        if sides <= 0 or sides > 1000:  # Reasonable limit on die sides
            return {
                "error": f"Invalid dice sides: {sides} (must be between 1 and 1000)",
                "success": False
            }
        
        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(count)]
        subtotal = sum(rolls)
        total = subtotal + modifier
        
        # Create a standardized result structure
        roll_groups = [{
            "dice": f"{count}d{sides}",
            "count": count,
            "sides": sides,
            "rolls": rolls,
            "subtotal": subtotal
        }]
        
        result = {
            "result": total,
            "expression": f"{count}d{sides}{modifier_str if modifier_str else ''}",
            "rolls": rolls,
            "roll_groups": roll_groups,
            "modifiers": modifier if modifier != 0 else None,
            "success": True
        }
        
        # Add breakdown if verbose
        if verbose:
            mod_text = ""
            if modifier > 0:
                mod_text = f" + {modifier}"
            elif modifier < 0:
                mod_text = f" - {abs(modifier)}"
                
            result["breakdown"] = f"{count}d{sides}: {rolls} = {subtotal}{mod_text} = {total}"
        else:
            # Always include a minimal breakdown even when not verbose
            result["summary"] = f"Rolled {expression} = {total}"
        
        return result
    
    def _roll_complex_dice(self, expression: str, verbose: bool) -> Dict[str, Any]:
        """Roll a complex dice expression with multiple dice sets."""
        # Split the expression into components
        components = self._parse_complex_expression(expression)
        
        if not components:
            return {
                "error": f"Invalid complex dice expression: {expression}",
                "success": False
            }
        
        total = 0
        all_rolls = []
        breakdown_parts = []
        roll_groups = []  # Store individual roll groups for better result structure
        
        # Roll each dice set
        for component_type, component_value in components:
            if component_type == "dice":
                count, sides = component_value
                rolls = [random.randint(1, sides) for _ in range(count)]
                subtotal = sum(rolls)
                total += subtotal
                all_rolls.extend(rolls)
                roll_groups.append({
                    "dice": f"{count}d{sides}",
                    "count": count,
                    "sides": sides,
                    "rolls": rolls,
                    "subtotal": subtotal
                })
                
                if verbose:
                    breakdown_parts.append(f"{count}d{sides}: {rolls} = {subtotal}")
            
            elif component_type == "negative_dice":
                # Handle negative dice rolls properly
                count, sides = component_value
                rolls = [random.randint(1, sides) for _ in range(count)]
                subtotal = -sum(rolls)  # Negate the sum for negative dice
                total += subtotal
                all_rolls.extend([-roll for roll in rolls])  # Store as negative values
                roll_groups.append({
                    "dice": f"-{count}d{sides}",
                    "count": count,
                    "sides": sides,
                    "rolls": [-roll for roll in rolls],
                    "subtotal": subtotal
                })
                
                if verbose:
                    breakdown_parts.append(f"-{count}d{sides}: {rolls} = {subtotal}")
            
            elif component_type == "modifier":
                operator, value = component_value
                if operator == "+":
                    total += value
                    if verbose:
                        breakdown_parts.append(f"+ {value}")
                else:
                    total -= value
                    if verbose:
                        breakdown_parts.append(f"- {value}")
        
        # Create a standardized result structure
        result = {
            "result": total,
            "expression": expression,
            "rolls": all_rolls,
            "roll_groups": roll_groups,  # Add detailed roll groups for better analysis
            "success": True
        }
        
        # Add breakdown if verbose
        if verbose:
            result["breakdown"] = " ".join(breakdown_parts) + f" = {total}"
        else:
            # Always include a minimal breakdown even when not verbose
            result["summary"] = f"Rolled {expression} = {total}"
        
        return result
    
    def _parse_complex_expression(self, expression: str) -> List[Tuple[str, Union[Tuple[int, int], Tuple[str, int]]]]:
        """Parse a complex dice expression into components.
        
        This function only parses the expression without rolling any dice,
        separating the parsing step from the execution step.
        """
        components = []
        remaining = expression
        
        # First, find any dice expressions
        dice_matches = list(re.finditer(r'(\d*)d(\d+)', remaining))
        
        if not dice_matches:
            return []
        
        # Extract the dice parts and operators
        last_end = 0
        for match in dice_matches:
            # Check if there's an operator before this dice
            if match.start() > last_end:
                operator = remaining[last_end]
                if operator in ('+', '-'):
                    # Parse any pure modifiers that came before
                    try:
                        mod_value = int(remaining[last_end+1:match.start()])
                        components.append(("modifier", (operator, mod_value)))
                    except ValueError:
                        # If we can't parse it, the expression is invalid
                        return []
            
            # Parse the dice expression
            count_str, sides_str = match.groups()
            count = int(count_str) if count_str else 1
            sides = int(sides_str)
            
            # Validate dice parameters
            if count <= 0 or count > 100:  # Prevent excessive dice rolling
                logger.warning(f"Invalid dice count: {count}")
                return []
                
            if sides <= 0 or sides > 1000:  # Reasonable limit on die sides
                logger.warning(f"Invalid dice sides: {sides}")
                return []
            
            # Add the dice component
            if match.start() == 0 or remaining[match.start()-1] != '-':
                # Positive dice (either at start or with + operator)
                components.append(("dice", (count, sides)))
            else:
                # Negative dice (with - operator)
                # Store as a negative dice component, handled during rolling
                components.append(("negative_dice", (count, sides)))
            
            last_end = match.end()
        
        # Handle the final modifier if any
        if last_end < len(remaining):
            operator = remaining[last_end]
            if operator in ('+', '-'):
                try:
                    mod_value = int(remaining[last_end+1:])
                    components.append(("modifier", (operator, mod_value)))
                except ValueError:
                    # If we can't parse it, the expression is invalid
                    return []
        
        return components
    
    @property
    def is_active(self) -> bool:
        """Check if the plugin is available for use."""
        return True
