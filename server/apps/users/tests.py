from .factories import UserFactory
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TestsUserCreate(TestCase):

    def setUp(self):
        self.email = 'user1@example.com'
        self.username = 'user1'
        self.password = '123strong432password'
        self.user_model = get_user_model()

    def test_create_user(self):
        user = self.user_model.objects.create_user(
            email=self.email,
            password=self.password,
            username=self.username
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        self.username = 'admin'

        user = self.user_model.objects.create_superuser(
            email=self.email,
            password=self.password,
            username=self.username
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class TestRegisterApi(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.email = 'user2@example.com'
        self.username = 'user2'
        self.password = 'a2khgn7vang017am'
        self.url = reverse('user_create')
        self.payload = {
            'email': self.email,
            'username': self.username,
            'password': self.password,
        }
        self.fields = ['id', 'username']

    def test_create_user_request_return_201(self):
        response = self.client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_request_return_400_if_send_too_long_username(self):
        self.payload['username'] = 'a' * 151
        response = self.client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_request_return_400_if_send_not_valid_email(self):
        self.payload['email'] = 'not@valid@email'
        response = self.client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_request_return_400_if_send_data_without_email(self):
        del self.payload['email']
        response = self.client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_request_return_400_if_send_data_without_password(self):
        del self.payload['password']
        response = self.client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_request_return_400_if_send_data_without_username(self):
        del self.payload['username']
        response = self.client.post(self.url, data=self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_request_add_data_to_db(self):
        count = CustomUser.objects.count()
        self.client.post(self.url, data=self.payload)
        self.assertEqual(CustomUser.objects.count(), count + 1)

    def test_create_user_request_add_correct_data_to_db(self):
        response = self.client.post(self.url, data=self.payload)
        pk = response.json().get('id')
        # TODO: add compare method to models or extend APITestCase
        # created vshagur@gmail.com, 2021-07-28
        user = CustomUser.objects.get(pk=pk)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.username, self.username)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_request_return_correct_json(self):
        response = self.client.post(self.url, data=self.payload)
        data = response.json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(data.get('username'), self.username)


class TestUserDetailApi(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.anon_client = APIClient()
        self.auth_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.auth_client.force_authenticate(user=self.user, token=refresh.access_token)
        self.url = reverse('user_detail', args=(self.user.id,))
        self.fields = ['id', 'username']

    def test_get_user_info_request_return_200_if_auth_user(self):
        response = self.auth_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_info_request_return_401_if_anon_user(self):
        response = self.anon_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_info_request_return_correct_json_if_auth_user(self):
        response = self.auth_client.get(self.url)
        data = response.json()
        self.assertCountEqual(data.keys(), self.fields)
        self.assertEqual(data.get('id'), self.user.id)
        self.assertEqual(data.get('username'), self.user.username)

    def test_get_user_info_request_return_403_if_send_id_not_equal_user_id(self):
        new_user = UserFactory()
        url = reverse('user_detail', args=(new_user.id,))
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_info_request_return_404_if_send_not_exist_id(self):
        # TODO: move args value to constant
        # created vshagur@gmail.com, 2021-07-28
        url = reverse('user_detail', args=(999999999,))
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
