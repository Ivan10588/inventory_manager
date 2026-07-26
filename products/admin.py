from django.contrib import admin
from .models import Equipment, StockOperation

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock_quantity', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(StockOperation)
class StockOperationAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'operation_type', 'quantity', 'user', 'created_at')
    list_filter = ('operation_type', 'created_at')
    search_fields = ('equipment__name', 'user__username')
