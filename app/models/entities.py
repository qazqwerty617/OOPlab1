from dataclasses import dataclass
from decimal import Decimal

@dataclass
class BaseEntity:
    id: int | None = None

@dataclass
class Subscriber(BaseEntity):
    full_name: str = ""
    phone_number: str = ""
    address: str = ""
    is_blocked: bool = False

    def status(self) -> str:
        return "Заблокований" if self.is_blocked else "Активний"

@dataclass
class Service(BaseEntity):
    name: str = ""
    monthly_price: Decimal = Decimal("0.00")

@dataclass
class Invoice(BaseEntity):
    subscriber_id: int = 0
    amount: Decimal = Decimal("0.00")
    description: str = ""
    is_paid: bool = False

class PaymentAction:
    def apply(self, invoice: Invoice) -> Invoice:
        raise NotImplementedError

class FullPayment(PaymentAction):
    def apply(self, invoice: Invoice) -> Invoice:
        invoice.is_paid = True
        return invoice
