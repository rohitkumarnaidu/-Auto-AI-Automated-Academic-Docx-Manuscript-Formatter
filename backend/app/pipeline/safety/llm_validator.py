import inspect
from pydantic import BaseModel
from typing import Callable, Any, Type, Optional

# --- Optional Guardrails Import ---
try:
    import guardrails
    from guardrails import Guard
    HAS_GUARDRAILS = True
    print("[SUCCESS] Guardrails AI loaded for robust LLM validation.")
except ImportError:
    HAS_GUARDRAILS = False
    print("[INFO] Guardrails AI unavailable. Falling back to native Pydantic validation (validator_guard.py).")

# Gracefully import the old wrapper as a fallback
try:
    from app.pipeline.safety.validator_guard import validate_output as fallback_validate_output
except ImportError:
    # Extreme fallback if not found
    def fallback_validate_output(schema: Any, error_return_value: Any = None):
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                try:
                    res = func(*args, **kwargs)
                    return res
                except Exception:
                    return error_return_value or {}
            return wrapper
        return decorator

def guard_llm_output(schema: Type[BaseModel], error_return_value: Optional[Any] = None) -> Callable:
    """
    Advanced LLM Output Validator.
    Uses Guardrails AI (guardrails-ai) if available to guarantee Pydantic schema compliance.
    If unavailable, structurally falls back to `validator_guard.validate_output` which relies on native Pydantic wrappers.
    """
    
    # 1. Fallback Mode: Guardrails not installed or schema is not a BaseModel
    if not HAS_GUARDRAILS or not (isinstance(schema, type) and issubclass(schema, BaseModel)):
        return fallback_validate_output(schema, error_return_value=error_return_value)
        
    # 2. Guardrails AI Mode:
    def decorator(func: Callable) -> Callable:
        # Create the Guard instance strictly bound to the expected Pydantic schema
        guard = Guard.for_pydantic(output_class=schema)
        
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Execute the original LLM calling function. Note: Often returns a JSON string or dict.
                raw_result = func(*args, **kwargs)
                
                # If the function already returned the Pydantic model natively
                if isinstance(raw_result, schema):
                    return raw_result.model_dump()
                    
                # Format to JSON string for Guardrails
                if isinstance(raw_result, dict):
                    import json
                    raw_result_str = json.dumps(raw_result)
                elif isinstance(raw_result, str):
                    raw_result_str = raw_result
                else:
                    return raw_result
                
                # Guardrails validation execution
                # .parse() raises an error or returns a ValidationOutcome
                validated_output = guard.parse(raw_result_str)
                
                if validated_output and validated_output.validated_output:
                    val = validated_output.validated_output
                    if hasattr(val, "model_dump"):
                        return val.model_dump()
                    elif hasattr(val, "dict"):
                        return val.dict()
                    return val
                    
                # If Guardrails returned None (failed validation severely)
                print(f"[GUARDRAILS] Schema rejected JSON payload for {func.__name__}")
                return error_return_value or {}
                
            except Exception as e:
                # Catch Guardrails specific parsing errors securely
                print(f"[GUARDRAILS] Exception in {func.__name__}: {e}")
                import traceback
                traceback.print_exc()
                # Provide graceful degradation via error_return_value instead of crashing pipeline
                return error_return_value or {}
                
        return wrapper
    return decorator
