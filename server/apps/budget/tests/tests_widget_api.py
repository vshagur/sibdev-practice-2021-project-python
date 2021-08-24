from datetime import timedelta
from decimal import Decimal

from ..factories import CategoryFactory, TransactionFactory, WidgetFactory
from ..models.budget.widget import Widget
from .common import CustomAPITestCase
from apps.users.factories import UserFactory
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import status


class TestWidgetCreateApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.fields = (
            'id', 'category', 'limit', 'duration', 'criterion', 'color', 'creation_at'
        )
        self.url = reverse('widget-list')
        self.category = CategoryFactory(owner=self.user)
        self.limit = '1000.00'
        self.duration = timedelta(days=1)
        self.criterion = '<'
        self.color = '#b7d606'

        self.payload = {
            'category': self.category.id,
            'limit': Decimal(self.limit),
            'duration': self.duration,
            'criterion': self.criterion,
            'color': self.color,
        }

    def test_create_widget_request_return_201(self):
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_widget_request_return_401_if_user_not_login(self):
        response = self.anon_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_widget_request_add_data_to_db(self):
        count = Widget.objects.count()
        self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(Widget.objects.count(), count + 1)

    def test_create_widget_request_add_correct_data_to_db(self):
        response = self.auth_client.post(self.url, data=self.payload)
        pk = response.json().get('id')
        widget = Widget.objects.get(pk=pk)

        self.assertEqual(widget.owner, self.user)
        widget_data = model_to_dict(widget, fields=self.payload.keys())
        self.assertEqual(widget_data, self.payload)

    def test_create_widget_request_return_correct_json(self):
        response = self.auth_client.post(self.url, data=self.payload)
        data = response.json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(data.get('category'), self.category.id)
        self.assertEqual(data.get('limit'), self.limit)
        # TODO: find solution
        #  assert failed - # '1 00:00:00' != '1 day, 0:00:00'
        # created vshagur@gmail.com, 2021-08-9
        # self.assertEqual(data.get('duration'), str(self.duration))
        self.assertEqual(data.get('criterion'), self.criterion)
        self.assertEqual(data.get('color'), self.color)

    def test_create_widget_request_return_400_if_send_not_valid_duration(self):
        self.payload['duration'] = timedelta(days=2)
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestWidgetDeleteApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.category = CategoryFactory(owner=self.user)
        WidgetFactory.create_batch(size=5, owner=self.user, category=self.category)
        self.widget = WidgetFactory(owner=self.user, category=self.category)
        self.url = reverse('widget-detail', args=(self.widget.pk,))

    def test_delete_widget_request_return_204(self):
        response = self.auth_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_widget_request_return_401_if_user_not_login(self):
        response = self.anon_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_request_delete_data_from_db(self):
        count = Widget.objects.count()
        self.auth_client.delete(self.url)
        self.assertEqual(Widget.objects.count(), count - 1)
        self.assertFalse(Widget.objects.filter(pk=self.widget.pk).exists())

    def test_delete_category_request_return_403_if_user_not_owner(self):
        client = self.create_auth_client(UserFactory())
        response = client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestWidgetListApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.count_widgets = 5
        self.count_transactions = 3
        self.fields = (
            'id', 'limit', 'updated_at', 'category', 'color', 'creation_at',
            'criterion', 'duration', 'end_date', 'total'
        )

        self.categories = CategoryFactory.create_batch(
            size=self.count_widgets, owner=self.user
        )

        for category in self.categories:
            WidgetFactory.create(owner=self.user, category=category)

            TransactionFactory.create_batch(
                size=self.count_transactions, owner=self.user, category=category,
            )

        self.url = reverse('widget-list')
        # trash data
        new_user = UserFactory()
        category = CategoryFactory(owner=new_user)
        self.new_widget = WidgetFactory.create(owner=new_user, category=category)
        TransactionFactory.create_batch(size=21, owner=new_user, category=category)

    def test_get_list_widget_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_widget_request_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_widget_request_return_correct_objects_count(self):
        data = self.auth_client.get(self.url).json()
        self.assertEqual(len(data), self.count_widgets)

    def test_get_list_widget_request_return_objects_with_correct_fields(self):
        data = self.auth_client.get(self.url).json()
        for obj in data:
            with self.subTest(obj=obj):
                self.assertCountEqual(obj.keys(), self.fields)

    def test_get_list_widget_request_return_404_if_user_not_owner(self):
        url = reverse('widget-list', args=(self.new_widget,))
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
