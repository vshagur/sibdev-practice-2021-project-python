import warnings

from apps.users.factories import UserFactory
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test_func(self, *args, **kwargs)

    return do_test


class CustomAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.anon_client = APIClient()
        self.auth_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.auth_client.force_authenticate(user=self.user, token=refresh.access_token)

    def create_auth_client(self, user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.force_authenticate(user=user, token=refresh.access_token)

        return client
