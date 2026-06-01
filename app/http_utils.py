from urllib.parse import parse_qs

class Response:
    def __init__(self, body=b"", status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or [("Content-Type", "text/html; charset=utf-8")]

    @classmethod
    def redirect(cls, location: str):
        return cls(b"", 302, [("Location", location)])

def read_form(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length).decode("utf-8")
    parsed = parse_qs(body)
    return {k: v[0] for k, v in parsed.items()}
