import re

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def mock_lead_capture(state: dict) -> dict:
    name = state.get("name")
    email = state.get("email")
    platform = state.get("platform")
    
    if not all([name, email, platform]):
        return {"success": False, "msg": "Missing required data."}
        
    if not is_valid_email(email):
        return {"success": False, "msg": "Invalid email formatting."}
        
    
    return {"success": True, "msg": "You're all set! Our team will reach out soon."}
