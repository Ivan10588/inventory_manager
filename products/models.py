from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Equipment(models.Model):
    """Модель оборудования (аналог Product в inventory-системе)."""
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    stock_quantity = models.PositiveIntegerField("Остаток на складе", default=0)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (остаток: {self.stock_quantity})"


class StockOperation(models.Model):
    """История операций со складом (списания, поступления и т.д.)."""
    OPERATION_CHOICES = [
        ("write_off", "Списание"),
        ("arrival", "Поступление"),
        ("adjustment", "Корректировка"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="operations",
        verbose_name="Оборудование"
    )
    quantity = models.IntegerField("Количество")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь"
    )
    operation_type = models.CharField(
        "Тип операции",
        max_length=20,
        choices=OPERATION_CHOICES,
        default="write_off"
    )
    idempotency_key = models.CharField(
        "Ключ идемпотентности",
        max_length=64,
        blank=True,
        null=True,
        help_text="Позволяет избежать дублирования операций при повторных запросах."
    )
    created_at = models.DateTimeField("Дата операции", auto_now_add=True)

    class Meta:
        verbose_name = "Операция по складу"
        verbose_name_plural = "Операции по складу"
        indexes = [
            models.Index(fields=['idempotency_key']),
        ]

    def clean(self):
        if self.quantity <= 0 and self.operation_type == "write_off":
            raise ValidationError("При списании количество должно быть больше 0.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operation_type}: {self.equipment.name}, {self.quantity} шт."
