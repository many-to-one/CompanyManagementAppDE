from django.test import TestCase, RequestFactory
from matplotlib.pyplot import summer
from Adest.main.views import WorkObjects, workObjectView
# from django.contrib.auth.models import AnonymousUser, User
from main.models import *
from main.views_ import *
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
        self.assertContains(response, 'Object 2')
        self.assertContains(response, 'Object 1')

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
        # self.assertContains(response, 'Object 2')


##############################################################################################


class WorkObjectViewTest(TestCase):
    def setUp(self):
        # Create a RequestFactory instance
        self.factory = RequestFactory()

    def test_work_object_view(self):
        # Create a user
        user1 = CustomUser.objects.create(username='user1', email='user1@test.com')
        user2 = CustomUser.objects.create(username='user2', email='user2@test.com')

        # Create a work object
        work_object = WorkObject.objects.create(name='Test Object')
        work_object.user.add(user1, user2)
        work_object.save()

        # Create works
        work1 = Work.objects.create(
            work_object=work_object.name,
            payment=20,
            username=user1.username,
        )
        work1.save()

        work2 = Work(
            work_object=work_object.name,
            payment=20,
            username=user2.username,
        )
        work2.save()

        # total_payment = Work.objects.filter(
        #     work_object=work_object.name
        #     ).aggregate(
        #     total_payment=Sum('payment')
        #     )['total_payment']

        # Create a message
        message1 = Message.objects.create(work_object=work_object, content='Test message1')
        message2 = Message.objects.create(work_object=work_object, content='Test message2')

        # context = {
        #     'total_payment': total_payment
        # }

        # Create a request
        request = self.factory.get(f'/work_objects/{work_object.id}')
        request.user = user1

        # Call the view function
        response = workObjectView(request, pk=work_object.id)

        # Assert that the response has a successful status code
        self.assertEqual(response.status_code, 200)

        # Assert that the necessary data is present in the response context
        self.assertContains(response, work_object)
        self.assertContains(response, 'user1')
        self.assertContains(response, 'user2')
        # self.assertEqual(context['total_payment'], 40)
        # self.assertEqual(response.context['total_prepayment'], '0:00')
        # self.assertEqual(response.context['total_phone_costs'], '0:00')
        # self.assertEqual(response.context['total_payment'], '0:00')
