from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.finance.library.mixins import ProcessLibraryPaymentMixin


class ProcessLibraryPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            fine_id = request.data.get("fine")
            amount = request.data.get("amount")
            payment_method = request.data.get("payment_method")

            if not all([fine_id, amount, payment_method]):
                return Response({"error": "Missing required fields."}, status=400)

            processor = ProcessLibraryPaymentMixin(
                fine_id=fine_id,
                amount=amount,
                payment_method=payment_method,
                current_user=request.user,
            )

            result = processor.run()
            return Response(
                {"message": "Library fine paid successfully", "data": result},
                status=200,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)
