from datetime import date, timedelta

from ..factories import CategoryFactory, TransactionFactory
from ..models.budget.category import Category
from ..models.budget.transaction import Transaction
from ..paginators import PAGE_SIZE
from .common import CustomAPITestCase, ignore_warnings
from apps.users.factories import UserFactory
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# TODO: delete ignore_warnings decorator after debuging tests
# created vshagur@gmail.com, 2021-07-31

class TestTransactionCreateApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.fields = ['amount', 'date', 'category', 'id']
        self.url = reverse('transaction-list')
        self.amount = '123.34'
        self.date = date(1980, 3, 3)
        self.category = CategoryFactory.create(owner=self.user)
        self.payload = {
            'amount': self.amount,
            'date': self.date,
            'category': self.category,
        }

    def test_create_transaction_request_return_201(self):
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_transaction_request_return_401_if_user_not_login(self):
        response = self.anon_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_transaction_request_return_400_if_send_wrong_date(self):
        self.payload['date'] = date.today() + timedelta(1)
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_transaction_request_return_400_if_send_amount_equal_zero(self):
        self.payload['amount'] = 0
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_transaction_request_return_400_if_send_wrong_amount(self):
        self.payload['amount'] = 'blablabla'
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_transaction_request_return_400_if_user_not_category_owner(self):
        new_user = UserFactory()
        auth_client = APIClient()
        refresh = RefreshToken.for_user(new_user)
        auth_client.force_authenticate(user=new_user, token=refresh.access_token)
        response = auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_transaction_request_add_data_to_db(self):
        count = Transaction.objects.count()
        self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(Category.objects.count(), count + 1)

    def test_create_transaction_request_add_correct_data_to_db(self):
        response = self.auth_client.post(self.url, data=self.payload)
        pk = response.json().get('id')
        transaction = Transaction.objects.get(pk=pk)
        transaction_data = model_to_dict(transaction, fields=self.payload.keys())
        self.assertEqual(transaction.owner, self.user)
        self.assertCountEqual(transaction_data, self.payload)

    def test_create_transaction_request_return_correct_json(self):
        response = self.auth_client.post(self.url, data=self.payload)
        data = response.json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(data.get('date'), str(self.date))
        self.assertEqual(data.get('amount'), self.amount)
        self.assertEqual(data.get('category'), self.category.id)


class TestTransactionListApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.fields = ['amount', 'date', 'category', 'id']
        self.url = reverse('transaction-list')
        self.count = 63
        self.count1 = 18
        self.new_user = UserFactory()
        self.category1 = CategoryFactory.create(owner=self.new_user)
        self.category = CategoryFactory.create(owner=self.user)
        TransactionFactory.create_batch(
            size=self.count,
            owner=self.user,
            category=self.category,
        )

        TransactionFactory.create_batch(
            size=self.count1,
            owner=self.new_user,
            category=self.category1,
        )

    @ignore_warnings
    def test_get_list_transaction_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @ignore_warnings
    def test_get_list_transaction_request_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @ignore_warnings
    def test_get_list_transaction_return_correct_number_of_objects(self):
        data = self.auth_client.get(self.url).json()
        results = data.get('results', None)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), PAGE_SIZE)  # pagination limit

    @ignore_warnings
    def test_get_list_transaction_return_correct_number_of_objects_for_other_user(self):
        client = self.create_auth_client(self.new_user)
        data = client.get(self.url).json()
        results = data.get('results', None)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), self.count1)


class TestTransactionDeleteApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.count = 4
        self.count1 = 11
        self.new_user = UserFactory()
        self.category1 = CategoryFactory.create(owner=self.new_user)
        self.category = CategoryFactory.create(owner=self.user)
        TransactionFactory.create_batch(
            size=self.count,
            owner=self.user,
            category=self.category,
        )

        self.pk = Transaction.objects.last().id

        TransactionFactory.create_batch(
            size=self.count1,
            owner=self.new_user,
            category=self.category1,
        )
        self.url = reverse('transaction-detail', args=(self.pk,))

    def test_get_delete_transaction_request_return_204(self):
        response = self.auth_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_delete_transaction_request_return_401_if_user_not_login(self):
        response = self.anon_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_transaction_request_delete_data_from_db(self):
        self.auth_client.delete(self.url)
        expected = self.count + self.count1 - 1
        self.assertEqual(Transaction.objects.count(), expected)

    def test_delete_transaction_request_return_403_if_user_not_owner(self):
        client = self.create_auth_client(self.new_user)
        response = client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTransactionUpdateApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.category = CategoryFactory.create(owner=self.user)

        self.transaction = TransactionFactory.create(
            owner=self.user,
            category=self.category,
        )

        self.amount = '123.34'
        self.date = date(1980, 3, 3)

        self.new_category = CategoryFactory.create(
            owner=self.user,
            category_type='EX'
        )

        self.payload = {
            'amount': self.amount,
            'date': self.date,
            'category': self.new_category,
        }

        self.url = reverse('transaction-detail', args=(self.transaction.id,))

    def test_update_transaction_request_return_200(self):
        response = self.auth_client.put(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_transaction_request_return_401_if_user_not_login(self):
        response = self.anon_client.put(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_transaction_request_update_db_data(self):
        self.auth_client.put(self.url, data=self.payload)

        try:
            transaction = Transaction.objects.get(pk=self.transaction.id)
        except ObjectDoesNotExist:
            self.assertTrue(False)

        transaction_data = model_to_dict(transaction, fields=self.payload.keys())
        self.assertCountEqual(transaction_data, self.payload)


class TestTransactionPartialUpdateApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.category = CategoryFactory.create(owner=self.user)

        self.transaction = TransactionFactory.create(
            owner=self.user,
            category=self.category,
        )

        self.amount = '123.34'
        self.date = date(1980, 3, 3)

        self.new_category = CategoryFactory.create(
            owner=self.user,
            category_type='EX'
        )

        self.payload = {
            'date': self.date,
        }

        self.url = reverse('transaction-detail', args=(self.transaction.id,))

    def test_partial_update_transaction_request_return_200(self):
        response = self.auth_client.patch(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_transaction_request_return_401_if_user_not_login(self):
        response = self.anon_client.patch(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_transaction_request_update_db_data(self):
        self.auth_client.patch(self.url, data=self.payload)

        try:
            transaction = Transaction.objects.get(pk=self.transaction.id)
        except ObjectDoesNotExist:
            self.assertTrue(False)

        transaction_data = model_to_dict(transaction, fields=self.payload.keys())
        self.assertCountEqual(transaction_data, self.payload)
