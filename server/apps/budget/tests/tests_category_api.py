from ..factories import CategoryFactory
from ..models.budget.category import Category
from ..serializers import CategoryListSerializer
from .common import CustomAPITestCase
from apps.users.factories import UserFactory
from django.urls import reverse
from rest_framework import status


class TestCategoryCreateApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.fields = ['name', 'category_type', 'id']
        self.url = reverse('category-list')
        self.name = 'TestCategoryName'
        self.category_type = 'IN'
        self.payload = {
            'name': self.name,
            'category_type': self.category_type,
        }

    def test_create_category_request_return_201(self):
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_request_return_401_if_user_not_login(self):
        response = self.anon_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_request_return_400_if_send_wrong_category_type(self):
        self.payload['category_type'] = 'ZZ'
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_request_return_400_if_send_data_without_name(self):
        del self.payload['name']
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_request_return_400_if_send_data_without_category_type(self):
        del self.payload['category_type']
        response = self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_request_add_data_to_db(self):
        count = Category.objects.count()
        self.auth_client.post(self.url, data=self.payload)
        self.assertEqual(Category.objects.count(), count + 1)

    def test_create_category_request_add_correct_data_to_db(self):
        response = self.auth_client.post(self.url, data=self.payload)
        pk = response.json().get('id')
        category = Category.objects.get(pk=pk)
        self.assertEqual(category.name, self.name.lower())
        self.assertEqual(category.category_type, self.category_type)
        self.assertEqual(category.owner, self.user)

    def test_create_category_request_return_correct_json(self):
        response = self.auth_client.post(self.url, data=self.payload)
        data = response.json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(data.get('name'), self.name.lower())
        self.assertEqual(data.get('category_type'), self.category_type)


class TestCategoryListApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.fields = ['name', 'category_type', 'id']
        self.url = reverse('category-list')
        self.count = 50
        self.count1 = 23
        self.new_user = UserFactory()
        CategoryFactory.create_batch(size=self.count1, owner=self.new_user)
        CategoryFactory.create_batch(size=self.count, owner=self.user)
        self.categories = Category.objects.filter(owner=self.user)

    def test_get_list_category_request_return_200(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_category_request_return_401_if_user_not_login(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_category_return_correct_number_of_objects(self):
        data = self.auth_client.get(self.url).json()
        self.assertEqual(len(data), self.count)

    def test_get_list_category_return_correct_number_of_objects_for_other_user(self):
        client = self.create_auth_client(self.new_user)
        data = client.get(self.url).json()
        self.assertEqual(len(data), self.count1)

    def test_get_list_category_return_correct_json_format_of_object(self):
        response = self.auth_client.get(self.url)

        for obj in response.json():
            with self.subTest(obj=obj):
                self.assertCountEqual(obj.keys(), self.fields)

    def test_get_list_category_return_correct_data_values(self):
        response = self.auth_client.get(self.url)
        expected = CategoryListSerializer(self.categories, many=True)
        self.assertSequenceEqual(response.json(), expected.data)


class TestCategoryDeleteApi(CustomAPITestCase):

    def setUp(self):
        super().setUp()
        self.count = 5
        self.count1 = 3
        self.new_user = UserFactory()
        CategoryFactory.create_batch(size=self.count, owner=self.user)
        CategoryFactory.create_batch(size=self.count1, owner=self.new_user)
        self.pk = Category.objects.first().id
        self.url = reverse('category-detail', args=(self.pk,))

    def test_delete_category_request_return_204(self):
        response = self.auth_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_category_request_return_401_if_user_not_login(self):
        response = self.anon_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_request_delete_data_from_db(self):
        self.auth_client.delete(self.url)
        expected = self.count + self.count1 - 1
        self.assertEqual(Category.objects.count(), expected)

    def test_delete_category_request_return_403_if_user_not_owner(self):
        client = self.create_auth_client(self.new_user)
        response = client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
