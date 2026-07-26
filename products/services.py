from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, StockOperation

@transaction.atomic
def списать_товар(product_id: int, quantity: int, user_id: int, idempotency_key: str | None = None):
    """
    Списывает товар с проверкой остатков и защитой от гонок данных.
    
    :param product_id: ID товара
    :param quantity: Количество для списания
    :param user_id: ID пользователя, выполняющего списание
    :param idempotency_key: Ключ идемпотентности (чтобы не списать дважды при повторном запросе)
    :return: Объект StockOperation
    :raises: ValidationError, если товара недостаточно или количество <= 0
    """

    if idempotency_key:
        existing = StockOperation.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    if quantity <= 0:
        raise ValidationError("Количество для списания должно быть больше 0.")

    product = Product.objects.select_for_update().get(pk=product_id)

    if product.stock_quantity < quantity:
        raise ValidationError(f"Недостаточно товара. Доступно: {product.stock_quantity}, запрошено: {quantity}")

    product.stock_quantity -= quantity
    product.save(update_fields=['stock_quantity'])

    operation = StockOperation.objects.create(
        product=product,
        quantity=quantity,
        user_id=user_id,
        operation_type='write_off',
        idempotency_key=idempotency_key,
    )

    return operation
