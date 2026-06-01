import logging
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from app.controllers.controllers import AuthController, SubscriberController, InvoiceController
from app.dao.database import init_db
from app.http_utils import Response
from app.router import Router

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(filename="logs/app.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

router = Router()
auth = AuthController(); subscribers = SubscriberController(); invoices = InvoiceController()
router.add("GET", r"/", auth, "login_page")
router.add("GET", r"/login", auth, "login_page")
router.add("POST", r"/login", auth, "login")
router.add("POST", r"/logout", auth, "logout")
router.add("GET", r"/subscribers", subscribers, "list")
router.add("POST", r"/subscribers", subscribers, "create")
router.add("POST", r"/subscribers/(?P<id>\d+)/update", subscribers, "update")
router.add("POST", r"/subscribers/(?P<id>\d+)/block", subscribers, "block")
router.add("POST", r"/subscribers/(?P<id>\d+)/delete", subscribers, "delete")
router.add("POST", r"/subscribers/(?P<id>\d+)/services", subscribers, "add_service")
router.add("GET", r"/invoices/unpaid", invoices, "unpaid")
router.add("POST", r"/invoices", invoices, "create")
router.add("POST", r"/invoices/(?P<id>\d+)/pay", invoices, "pay")

class AppHandler(BaseHTTPRequestHandler):
    def _handle(self):
        logging.info("%s %s", self.command, self.path)
        action, kwargs = router.resolve(self.command, self.path.split("?")[0])
        response = action(self, **kwargs) if action else Response(b"<h1>404</h1>", 404)
        self.send_response(response.status)
        for key, value in response.headers:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.body)

    def do_GET(self): self._handle()
    def do_POST(self): self._handle()

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("localhost", 8000), AppHandler)
    print("Lab1 server: http://localhost:8000")
    server.serve_forever()
