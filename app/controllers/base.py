from app.http_utils import Response
from app.session import SessionManager
from app.template_engine import render

class BaseController:
    def page(self, template, **model):
        return Response(render(template, **model))

class ProtectedController(BaseController):
    def ensure_authenticated(self, request):
        session = SessionManager.get(request)
        if not session.get("username"):
            return False
        return True
