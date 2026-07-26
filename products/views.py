from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import списать_товар
from .models import Equipment
from django.core.exceptions import ValidationError as DjangoValidationError

class WriteOffView(APIView):
    def post(self, request):
        equipment_id = request.data.get('equipment_id')
        quantity = request.data.get('quantity')
        idempotency_key = request.headers.get('X-Idempotency-Key')

        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if equipment_id is None or quantity is None:
            return Response(
                {"detail": "Missing required fields: equipment_id and quantity."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            equipment = Equipment.objects.get(pk=equipment_id)
        except Equipment.DoesNotExist:
            return Response(
                {"detail": f"Equipment with id {equipment_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            operation = списать_товар(
                equipment_id=equipment.id,
                quantity=quantity,
                user_id=user.id,
                idempotency_key=idempotency_key
            )
            return Response({
                "status": "success",
                "operation_id": operation.id,
                "equipment_name": operation.equipment.name,
                "quantity_written_off": operation.quantity,
                "new_stock_quantity": operation.equipment.stock_quantity,
                "operation_type": operation.operation_type,
                "created_at": operation.created_at.isoformat()
            }, status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)