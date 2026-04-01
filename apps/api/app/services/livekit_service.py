from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings


class LiveKitService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_access_token(
        self,
        *,
        identity: str,
        room_name: str,
        can_publish: bool,
        can_subscribe: bool,
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "iss": self.settings.livekit_api_key,
            "sub": identity,
            "nbf": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "video": {
                "room": room_name,
                "roomJoin": True,
                "canPublish": can_publish,
                "canSubscribe": can_subscribe,
            },
        }
        return jwt.encode(payload, self.settings.livekit_api_secret, algorithm="HS256")

    def build_connection_response(
        self,
        *,
        identity: str,
        room_name: str,
        can_publish: bool,
        can_subscribe: bool,
    ) -> dict[str, str]:
        token = self.generate_access_token(
            identity=identity,
            room_name=room_name,
            can_publish=can_publish,
            can_subscribe=can_subscribe,
        )
        return {
            "token": token,
            "ws_url": self.settings.livekit_ws_url,
            "room_name": room_name,
        }
