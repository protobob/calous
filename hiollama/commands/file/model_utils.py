"""Utility functions for model capabilities."""

def check_model_vision_support(model_name: str) -> bool:
    """Check if a model supports vision capabilities.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        bool: True if the model supports vision, False otherwise
    """
    if not model_name:
        return False
    
    # First check: Models with vision in their name
    vision_indicators = ["-vision", "vision-", "vis-", "-vis", "vit-", "-vit"]
    model_lower = model_name.lower()
    
    # Check for vision indicators in model name
    if any(indicator in model_lower for indicator in vision_indicators):
        return True
    
    # Check for known vision models by name patterns
    known_vision_models = [
        "llava", "bakllava", "moondream", "cogvlm", "qwen-vl", 
        "yi-vl", "qwen-vision", "llama3-vision", "phi3-vision"
    ]
    
    for vision_model in known_vision_models:
        if vision_model in model_lower:
            return True
    
    # Look for multimodal capabilities in model tags
    try:
        import ollama
        model_info = ollama.show(model_name)
        if hasattr(model_info, "modelfile"):
            modelfile = model_info.modelfile.lower()
            if "multimodal" in modelfile or "vision" in modelfile:
                return True
                
        # Check for vision in the model tags
        if hasattr(model_info, "details") and hasattr(model_info.details, "tags"):
            tags = model_info.details.tags
            if "vision" in tags or "multimodal" in tags:
                return True
    except Exception:
        # If we can't query the model, assume it doesn't support vision
        pass
        
    return False
