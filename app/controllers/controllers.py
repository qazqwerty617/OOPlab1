from decimal import Decimal
from app.controllers.base import BaseController, ProtectedController
from app.dao.database import get_connection
from app.dao.repositories import UserDAO, SubscriberDAO, ServiceDAO, InvoiceDAO
from app.http_utils import Response, read_form
from app.models.entities import Subscriber, Invoice
from app.session import SessionManager

class AuthController(BaseController):
    def login_page(self, request, **kwargs):
        return self.page("login.html", error=None)

    def login(self, request, **kwargs):
        form = read_form(request)
        headers = [("Location", "/subscribers")]
        if UserDAO(get_connection).authenticate(form.get("username", ""), form.get("password", "")):
            SessionManager.login(headers, form["username"])
            return Response(b"", 302, headers)
        return self.page("login.html", error="Неправильний логін або пароль")

    def logout(self, request, **kwargs):
        headers = [("Location", "/login")]
        SessionManager.logout(request, headers)
        return Response(b"", 302, headers)

class SubscriberController(ProtectedController):
    def list(self, request, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        return self.page(
            "subscribers.html",
            subscribers=SubscriberDAO(get_connection).all(),
            services=ServiceDAO(get_connection).all(),
        )

    def create(self, request, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        form = read_form(request)
        SubscriberDAO(get_connection).create(Subscriber(
            full_name=form["full_name"], phone_number=form["phone_number"], address=form["address"]
        ))
        return Response.redirect("/subscribers")


    def update(self, request, id, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        form = read_form(request)
        SubscriberDAO(get_connection).update(Subscriber(
            id=int(id),
            full_name=form["full_name"],
            phone_number=form["phone_number"],
            address=form["address"],
            is_blocked=form.get("is_blocked") == "on",
        ))
        return Response.redirect("/subscribers")

    def block(self, request, id, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        SubscriberDAO(get_connection).block(int(id))
        return Response.redirect("/subscribers")

    def delete(self, request, id, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        SubscriberDAO(get_connection).delete(int(id))
        return Response.redirect("/subscribers")

    def add_service(self, request, id, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        form = read_form(request)
        ServiceDAO(get_connection).subscribe(int(id), int(form["service_id"]))
        return Response.redirect("/subscribers")

class InvoiceController(ProtectedController):
    def unpaid(self, request, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        return self.page("invoices.html", invoices=InvoiceDAO(get_connection).all_unpaid(), subscribers=SubscriberDAO(get_connection).all())

    def create(self, request, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        form = read_form(request)
        InvoiceDAO(get_connection).create(Invoice(
            subscriber_id=int(form["subscriber_id"]), amount=Decimal(form["amount"]), description=form["description"]
        ))
        return Response.redirect("/invoices/unpaid")

    def pay(self, request, id, **kwargs):
        if not self.ensure_authenticated(request):
            return Response.redirect("/login")
        InvoiceDAO(get_connection).pay(int(id))
        return Response.redirect("/invoices/unpaid")
