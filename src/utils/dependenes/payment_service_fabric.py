from src.repositories.repositories import PaymentRepository
from src.services.payment_service import PaymentService


def payment_service_fabric():
    return PaymentService(PaymentRepository())
