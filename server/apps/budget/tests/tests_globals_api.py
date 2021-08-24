from datetime import date
from decimal import Decimal
from urllib.parse import urljoin

from ..factories import CategoryFactory, TransactionFactory
from .common import CustomAPITestCase, ignore_warnings
from apps.users.factories import UserFactory
from django.urls import reverse
from rest_framework import status


class TestGlobalsGetApiEmptyDb(CustomAPITestCase):
    def setUp(self):
        super().setUp()
        self.fields = ['totals_income', 'totals_expense']
        self.url = reverse('transaction-globals')

    def test_get_globals_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_globals_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_globals_request_return_correct_data(self):
        data = self.auth_client.get(self.url).json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(Decimal(data.get('totals_income')), Decimal('0.00'))
        self.assertEqual(Decimal(data.get('totals_expense')), Decimal('0.00'))


class TestGlobalsGetApi(CustomAPITestCase):
    def setUp(self):
        super().setUp()
        self.fields = ['totals_income', 'totals_expense']
        self.url = reverse('transaction-globals')
        self.count = 100
        self.new_user = UserFactory()
        TransactionFactory.create_batch(size=30, owner=self.new_user)
        self.category = CategoryFactory.create(owner=self.user, category_type='EX')
        self.transactions = TransactionFactory.create_batch(
            size=self.count, owner=self.user, category=self.category,
        )
        self.expected = sum([obj.amount for obj in self.transactions])

    def test_get_globals_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_globals_request_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_globals_request_return_correct_data(self):
        data = self.auth_client.get(self.url).json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(Decimal(data.get('totals_income')), Decimal('0.0'))
        self.assertEqual(Decimal(data.get('totals_expense')), self.expected)


class TestFilterByDateGlobalsGetApi(CustomAPITestCase):
    def setUp(self):
        super().setUp()
        self.url_globals = reverse('transaction-globals')
        self.url = reverse('transaction-list')
        self.end_date_querysting = '?end_date=2019-05-10'
        self.start_date_querysting = '?start_date=2016-12-31'
        self.querysting = f'{self.start_date_querysting}&{self.end_date_querysting[1:]}'
        self.dates = [
            (2016, 1, 13), (2016, 11, 13), (2017, 7, 2), (2017, 8, 21), (2018, 12, 7),
            (2019, 1, 1), (2019, 5, 9), (2020, 1, 28), (2020, 6, 13), (2020, 1, 13),
        ]
        self.amount = 123.99
        self.new_user = UserFactory()
        self.category = CategoryFactory.create(owner=self.user, category_type='EX')
        for date_ in self.dates:
            TransactionFactory.create(
                owner=self.user,
                category=self.category,
                amount=self.amount,
                date=date(*date_)
            )

    @ignore_warnings
    def test_get_list_transaction_with_filters_request_return_200(self):
        url = urljoin(self.url, self.querysting)
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @ignore_warnings
    def test_get_list_transaction_request_with_filters_return_401_if_user_not_login(self):
        url = urljoin(self.url, self.querysting)
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @ignore_warnings
    def test_get_list_transaction_request_return_correct_count_filterd_objects(self):
        url = urljoin(self.url, self.querysting)
        data = self.auth_client.get(url).json()
        self.assertEqual(len(data.get('results')), 5)

    @ignore_warnings
    def test_get_list_transaction_request_return_correct_filtered_objects(self):
        url = urljoin(self.url, self.querysting)
        data = self.auth_client.get(url).json()
        self.assertEqual(len(data.get('results')), 5)

        for obj in data.get('results'):
            with self.subTest(obj=obj):
                obj_date = date(*map(int, obj.get('date').split('-')))
                self.assertTrue(date(2016, 12, 31) < obj_date < date(2019, 5, 10))

    @ignore_warnings
    def test_get_list_transaction_request_return_correct_filtered_objects_if_only_end_date(
            self):
        url = urljoin(self.url, self.end_date_querysting)
        data = self.auth_client.get(url).json()
        self.assertEqual(len(data.get('results')), 7)

        for obj in data.get('results'):
            with self.subTest(obj=obj):
                obj_date = date(*map(int, obj.get('date').split('-')))
                self.assertTrue(obj_date < date(2019, 5, 10))

    @ignore_warnings
    def test_get_list_transaction_request_return_correct_filtered_objects_if_only_start_date(
            self):
        url = urljoin(self.url, self.start_date_querysting)
        data = self.auth_client.get(url).json()
        self.assertEqual(len(data.get('results')), 8)

        for obj in data.get('results'):
            with self.subTest(obj=obj):
                obj_date = date(*map(int, obj.get('date').split('-')))
                self.assertTrue(date(2016, 12, 31) < obj_date)

    @ignore_warnings
    def test_get_globals_with_filters_request_return_200(self):
        url = urljoin(self.url_globals, self.querysting)
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @ignore_warnings
    def test_get_globals_request_with_filters_return_401_if_user_not_login(self):
        url = urljoin(self.url_globals, self.querysting)
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @ignore_warnings
    def test_get_globals_with_filters_request_return_correct_data(self):
        url = urljoin(self.url_globals, self.querysting)
        data = self.auth_client.get(url).json()
        self.assertEqual(Decimal(data.get('totals_income')), Decimal('0.0'))
        self.assertEqual(data.get('totals_expense'), str(round(5 * self.amount, 2)))
