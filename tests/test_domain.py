from decimal import Decimal
from app.models.entities import Invoice, FullPayment, Subscriber
from app.router import Router

class Dummy:
    def index(self, request, **kwargs):
        return "ok"

def test_payment_polymorphism_marks_invoice_paid():
    invoice = Invoice(amount=Decimal("100.00"))
    result = FullPayment().apply(invoice)
    assert result.is_paid is True

def test_subscriber_status():
    assert Subscriber(is_blocked=True).status() == "Заблокований"

def test_custom_router_resolves_dynamic_route():
    r = Router(); d = Dummy(); r.add("GET", r"/items/(?P<id>\d+)", d, "index")
    action, kwargs = r.resolve("GET", "/items/7")
    assert action(None) == "ok"
    assert kwargs["id"] == "7"
