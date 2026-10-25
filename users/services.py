import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str) -> str:
    """    Создание продукта в Stripe. Регистрирует наименование в каталоге Stripe.
    Без создания сущности продукта Stripe не позволит выставить счет.
    Принимает название курса или урока, возвращает уникальный ID продукта Stripe.    """
    product = stripe.Product.create(
        name=name,
        description=f"Оплата доступа к учебному материалу: {name}"
    )
    return product.id


def create_stripe_price(product_id: str, amount: float, currency: str = "rub") -> str:
    """    Создание цены для ранее созданного продукта.
    Конвертирует рубли в копейки(умножением на 100).
    Принимает ID продукта и сумму. Возвращает ID цены Stripe.    """
    # Переводим сумму в минимальные единицы валюты (копейки)
    stripe_amount = int(float(amount) * 100)

    price = stripe.Price.create(
        currency=currency,
        unit_amount=stripe_amount,
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id: str) -> tuple[str, str]:
    """    Создание платежной сессии Stripe Checkout.
    Принимает ID цены, возвращает кортеж из (ID сессии, Ссылка на оплату).    """
    # Ссылки, куда перенаправлять пользователя после успешной оплаты или отмены
    success_url = "http://127.0.0.1:8000/"

    session = stripe.Checkout.Session.create(
        success_url=success_url,
        line_items=[{"price": price_id, "quantity": 1,}],
        mode="payment",
    )
    return session.id, session.url


def retrieve_stripe_session_status(session_id: str) -> str:
    """   (Опционально) Получение текущего статуса оплаты по ID сессии Stripe.
    Возвращает строку статуса (например: 'unpaid', 'paid').    """
    session = stripe.Checkout.Session.retrieve(session_id)
    return session.payment_status
