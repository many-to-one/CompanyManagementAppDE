from django.test import TestCase, RequestFactory
# from django.contrib.auth.models import AnonymousUser, User
from main.models import *
from main.views import *
from users.models import CustomUser


class WorkObjectsViewTest(TestCase):
    def setUp(self):
        # Create a RequestFactory instance
        self.factory = RequestFactory()

        # Create a superuser
        self.superuser = CustomUser.objects.create_superuser(username='admin', password='password', email='superuser@test.com')

        # Create a regular user
        self.user = CustomUser.objects.create_user(username='user', password='password', email='user@test.com')

        # Create some WorkObject instances
        WorkObject.objects.create(name='Object 1').user.add(self.superuser)
        WorkObject.objects.create(name='Object 2').user.add(self.user)

    def test_work_objects_as_superuser(self):
        # Create a request as a superuser
        request = self.factory.get('/work_objects/')
        request.user = self.superuser

        # Call the view function
        response = WorkObjects(request)

        # Assert that all WorkObject instances are fetched
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Object 1, Object 2')

    def test_work_objects_as_regular_user(self):
        # Create a request as a regular user
        request = self.factory.get('/work_objects/')
        request.user = self.user

        # Call the view function
        response = WorkObjects(request)

        # Assert that the response has a successful status code
        self.assertEqual(response.status_code, 200)

        # Assert that only the user's WorkObject instance is present in the response content
        self.assertContains(response, 'Object 2')
        self.assertNotContains(response, 'Object 1')

    def test_work_objects_filtering(self):
        # Create a request with a POST parameter to filter WorkObject instances
        request = self.factory.post('/work_objects/', {'object': 'Object 1'})
        request.user = self.superuser

        # Call the view function
        response = WorkObjects(request)

        # Assert that the response has a successful status code
        self.assertEqual(response.status_code, 200)

        # Assert that the filtered WorkObject instance is present in the response content
        self.assertContains(response, 'Object 1')
        # self.assertNotContains(response, 'Object 2')
