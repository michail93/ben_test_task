import json

from django.test import TestCase

from .models import CustomUser


class UserTransactionsTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(username="BobSmith", first_name="Bob", last_name="Smith",
                                  email="bob@smith.com", inn="566798362605", balance=12000.46)
        CustomUser.objects.create(username="PetrIvanov", first_name="Petr", last_name="Ivanov",
                                  email="ivanov@petr.com", inn="275472969038", balance=1000.0)
        CustomUser.objects.create(username="MarkIsaev", first_name="Mark", last_name="Isaev",
                                  email="isaev@mark.com", inn="441274000593", balance=540.38)
        CustomUser.objects.create(username="VladGavrilov", first_name="Vlad", last_name="Gavrilov",
                                  email="vlad@gavrilov.com", inn="441274000593", balance=650.0)
        self.test_request_json = {
                    "username": "BobSmith",
                    "inn": "441274000593",
                    "amount": 130.33
                }

    def test_invalid_inn(self):
        """
        Тест ИНН пользователей которых нет в бд
        """
        new_request_json = self.test_request_json
        new_request_json["inn"] = "000011112222"
        response = self.client.post("/transactions/", data=json.dumps(new_request_json),
                                    content_type="application/json")
        self.assertEqual(response.json()["response"], "error", "Error!")
        self.assertEqual(response.json()["message"],  "Users not found.", "Error!")

    def test_invalid_amount(self):
        """
        Тест списания суммы большей чем есть у пользователя
        """
        new_request_json = self.test_request_json
        new_request_json["amount"] = 12400.50
        response = self.client.post("/transactions/", data=json.dumps(new_request_json),
                                    content_type="application/json")
        self.assertEqual(response.json()["response"], "error", "Error!")
        self.assertEqual(response.json()["message"], "Not enough money on balance of user.", "Error!")

    def test_negative_amount(self):
        """
        Тест списания отрицательной суммы
        """
        new_request_json = self.test_request_json
        new_request_json["amount"] = -50
        response = self.client.post("/transactions/", data=json.dumps(new_request_json),
                                    content_type="application/json")
        self.assertEqual(response.json()["response"], "error", "Error!")
        self.assertEqual(response.json()["message"], "invalid amount.", "Error!")

    def test_valid_transaction(self):
        """
        Тест баланса пользователей, участвующих в транзакции
        """
        response = self.client.post("/transactions/", data=json.dumps(self.test_request_json),
                                    content_type="application/json")
        bob_smith = CustomUser.objects.get(username="BobSmith")
        mark_isaev = CustomUser.objects.get(username="MarkIsaev")
        vlad_gavrilov = CustomUser.objects.get(username="VladGavrilov")
        self.assertEqual(bob_smith.balance, 11870.13, "Error!")
        self.assertEqual(mark_isaev.balance, 605.55, "Error!")
        self.assertEqual(vlad_gavrilov.balance, 715.17, "Error!")
        self.assertEqual(response.json()["response"], "success", "Error!")
        self.assertEqual(response.json()["message"], "transaction is done.", "Error!")



