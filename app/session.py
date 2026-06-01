import secrets
from http import cookies

_sessions: dict[str, dict] = {}

class SessionManager:
    @staticmethod
    def get(request) -> dict:
        raw_cookie = request.headers.get("Cookie", "")
        jar = cookies.SimpleCookie(raw_cookie)
        sid = jar.get("SID")
        if sid and sid.value in _sessions:
            return _sessions[sid.value]
        return {}

    @staticmethod
    def login(headers, username: str):
        sid = secrets.token_urlsafe(24)
        _sessions[sid] = {"username": username}
        headers.append(("Set-Cookie", f"SID={sid}; HttpOnly; Path=/"))

    @staticmethod
    def logout(request, headers):
        raw_cookie = request.headers.get("Cookie", "")
        jar = cookies.SimpleCookie(raw_cookie)
        sid = jar.get("SID")
        if sid:
            _sessions.pop(sid.value, None)
        headers.append(("Set-Cookie", "SID=; Max-Age=0; Path=/"))
