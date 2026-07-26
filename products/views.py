from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import списать_товар
from .models import Product
from django.core.exceptions import ValidationError as DjangoValidationError

class WriteOffView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        idempotency_key = request.headers.get('X-Idempotency-Key')

        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден."}, status=status.HTTP_404_NOT_FOUND)

        try:
            operation = списать_товар(
                product_id=product.id,
                quantity=quantity,
                user_id=user.id,
                idempotency_key=idempotency_key
            )
            return Response({
                "status": "success",
                "operation_id": operation.id,
                "new_stock": operation.product.stock_quantity
            }, status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
