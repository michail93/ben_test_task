import json

from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import MultipleObjectsReturned

from .models import CustomUser


@method_decorator(csrf_exempt, name="dispatch")
class TransactionView(View):
    def post(self, request):
        """
        ожидает JSON вида:
        {
            'username': "str", # username пользователя со счета которого нужно снять деньги
            'inn' : "str", # ИНН на который будут переведены деньги
            'amount' : "float" # сумма которая будет переведена(с точностью до копеек)
        }
        """
        in_json = json.loads(request.body)

        if in_json["amount"] <= 0:
            return JsonResponse({
                "response": "error",
                "message": "invalid amount."
            })

        with transaction.atomic():
            try:
                user_from = CustomUser.objects.select_for_update().get(username=in_json["username"])
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    "response": "error",
                    "message": "User not found."
                })
            except MultipleObjectsReturned:
                return JsonResponse({
                    "response": "error",
                    "message": "More than one user is found."
                })

            users_to = CustomUser.objects.select_for_update().filter(inn=in_json["inn"])

            if not users_to:
                return JsonResponse({
                    "response": "error",
                    "message": "Users not found."
                })

            if user_from.balance < in_json["amount"]:
                return JsonResponse({
                    "response": "error",
                    "message": "Not enough money on balance of user."
                })

            count_users = users_to.count()

            user_from.balance = round(user_from.balance - in_json["amount"], 2)
            user_from.save()

            money_for_user = round(in_json["amount"] / count_users, 2)

            for u in users_to:
                u.balance = round(u.balance + money_for_user, 2)
                u.save()

        return JsonResponse({
            "response": "success",
            "message": "transaction is done."
        })
