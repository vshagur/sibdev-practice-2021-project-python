import unittest
from datetime import date
from urllib.parse import urljoin

from ..factories import CategoryFactory, TransactionFactory
from .common import CustomAPITestCase
from apps.users.factories import UserFactory
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import status


class TestSummaryGetApiEmptyDb(CustomAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('category-summary')

    def test_get_summary_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_summary_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TODO: clarify the task
    # created vshagur@gmail.com, 2021-08-1
    @unittest.skip('work is not correct, buisness logic problem')
    def test_get_summary_request_return_correct_data(self):
        data = self.auth_client.get(self.url).json()
        self.assertEqual(data, [])

    @unittest.skip('work is not correct, buisness logic problem')
    def test_get_summary_request_return_correct_data_if_one_category_exist(self):
        CategoryFactory.create(owner=[self.user, ], category_type='EX')
        data = self.auth_client.get(self.url).json()
        self.assertEqual(data, [])


class TestSummaryGetApi(CustomAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('category-summary')
        self.count = 4
        self.amounts = (1.01, 7.16, 3.02)
        self.new_user = UserFactory()
        CategoryFactory.create_batch(size=50, owner=self.new_user)
        self.categories = (
            CategoryFactory.create(owner=self.user, category_type='EX'),
            CategoryFactory.create(owner=self.user, category_type='IN'),
            CategoryFactory.create(owner=self.user, category_type='EX'),
        )

        for idx in (range(3)):
            TransactionFactory.create_batch(
                size=self.count,
                owner=self.user,
                category=self.categories[idx],
                amount=self.amounts[idx]
            )

    def test_get_summary_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_summary_request_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_summary_request_return_correct_count_objects(self):
        data = self.auth_client.get(self.url).json()
        self.assertEqual(len(data), 3)

    def test_get_summary_request_return_correct_data(self):
        data = self.auth_client.get(self.url).json()
        for idx in (range(3)):
            with self.subTest(category=self.categories[idx], amount=self.amounts[idx]):
                expected = model_to_dict(self.categories[idx])
                del expected['owner']
                expected['total_by_expenses'] = \
                    str(round(self.count * self.amounts[idx], 2))
                self.assertIn(expected, data)


class TestFilterByDateSummaryGetApi(CustomAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('category-summary')

        self.dates = [
            (2016, 1, 13), (2016, 11, 13), (2017, 7, 2), (2017, 8, 21), (2018, 12, 7),
            (2019, 1, 1), (2019, 5, 9), (2020, 1, 28), (2020, 6, 13), (2020, 1, 13),
        ]

        self.amount = 321.01
        self.new_user = UserFactory()
        self.category = CategoryFactory.create(owner=self.user)
        self.end_date_querysting = '?end_date=2019-05-10'
        self.start_date_querysting = '?start_date=2016-12-31'
        self.querysting = f'{self.start_date_querysting}&{self.end_date_querysting[1:]}'

        for date_ in self.dates:
            TransactionFactory.create(
                owner=self.user,
                category=self.category,
                amount=self.amount,
                date=date(*date_)
            )

    def test_get_summary_with_filters_request_return_200(self):
        url = urljoin(self.url, self.querysting)
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_summary_request_with_filters_return_401_if_user_not_login(self):
        url = urljoin(self.url, self.querysting)
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_summary_with_filters_request_return_correct_count_objects(self):
        url = urljoin(self.url, self.querysting)
        data = self.auth_client.get(url).json()
        self.assertEqual(len(data), 1)

    def test_get_summary_with_filters_request_return_correct_data(self):
        url = urljoin(self.url, self.querysting)
        obj = self.auth_client.get(url).json().pop()
        self.assertEqual(obj.get('name'), self.category.name)
        self.assertEqual(obj.get('id'), self.category.id)
        self.assertEqual(obj.get('total_by_expenses'), str(round(5 * self.amount, 2)))

    def test_get_summary_with_filters_request_return_correct_data_if_only_end_date(self):
        url = urljoin(self.url, self.end_date_querysting)
        obj = self.auth_client.get(url).json().pop()
        self.assertEqual(obj.get('name'), self.category.name)
        self.assertEqual(obj.get('id'), self.category.id)
        self.assertEqual(obj.get('total_by_expenses'), str(round(7 * self.amount, 2)))

    def test_get_summary_with_filters_request_return_correct_data_if_only_start_date(
            self):
        url = urljoin(self.url, self.start_date_querysting)
        obj = self.auth_client.get(url).json().pop()
        self.assertEqual(obj.get('name'), self.category.name)
        self.assertEqual(obj.get('id'), self.category.id)
        self.assertEqual(obj.get('total_by_expenses'), str(round(8 * self.amount, 2)))
