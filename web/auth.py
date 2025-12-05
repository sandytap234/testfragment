import hmac
import hashlib
import json
from urllib.parse import unquote
from fastapi import HTTPException

def validate_telegram_data(init_data: str, bot_token: str) -> dict:
    if not bot_token:
        raise HTTPException(500, "BOT_TOKEN not set")
    try:
        data_part, hash_part = init_data.rsplit("&hash=", 1)
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        check_hash = hmac.new(secret, data_part.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(check_hash, hash_part):
            raise HTTPException(403, "Invalid hash")

        user_data = {}
        for param in data_part.split("&"):
            if param.startswith("user="):
                user_json = unquote(param[5:])
                user = json.loads(user_json)
                user_data["id"] = user["id"]
                user_data["username"] = user.get("username", "")
        return user_data
    except Exception:
        raise HTTPException(400, "Invalid init data")