from django.test import TestCase
from main.models import *
from users.models import CustomUser
from django.utils import timezone
from datetime import datetime

class WorkObjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample CustomUser object
        user = CustomUser.objects.create(username='test_user')

        # Create a sample WorkObject object
        WorkObject.objects.create(
            name='Test Object',
            coffee_food=10.5,
        ).user.add(user)

    def test_str_representation(self):
        work_object = WorkObject.objects.get(id=1)
        self.assertEqual(str(work_object), '1')

    def test_name_field(self):
        work_object = WorkObject.objects.get(id=1)
        field = work_object._meta.get_field('name')
        self.assertTrue(field.null)
        self.assertEqual(field.max_length, 150)

    def test_coffee_food_field(self):
        work_object = WorkObject.objects.get(id=1)
        field = work_object._meta.get_field('coffee_food')
        self.assertTrue(field.null)
        self.assertEqual(field.default, 0.00)
        self.assertEqual(field.verbose_name, 'Kawa/Posiłki')

    def test_user_field(self):
        work_object = WorkObject.objects.get(id=1)
        users = work_object.user.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'test_user')


####################################################################################
####################################################################################
####################################################################################
####################################################################################


class WorkModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample CustomUser object
        user = CustomUser.objects.create(username='test_user')

        # Create a sample Work object
        work = Work.objects.create(
            date='01-01-2023',
            username='Test User',
            timestart='09:00',
            timefinish='17:00',
            diff_time='08:00',
            over_time='02:00',
            sum_time_sec=28800.0,
            sum_over_time_sec='02:00',
            work_object='Test Work Object',
            work_type='Test Work Type',
            coffee_food='Coffee',
            fuel='10.00',
            prepayment='20.00',
            phone_costs='15.00',
            payment='100.00',
            payment_hour=10.0,
        ).user.add(user)

    def test_str_representation(self):
        work = Work.objects.get(id=1)
        self.assertEqual(str(work), 'Test Work Object')

    def test_fields(self):
        work = Work.objects.get(id=1)

        self.assertEqual(work.date, '01-01-2023')
        self.assertEqual(work.username, 'Test User')
        self.assertEqual(work.timestart, '09:00')
        self.assertEqual(work.timefinish, '17:00')
        self.assertEqual(work.diff_time, '08:00')
        self.assertEqual(work.over_time, '02:00')
        self.assertEqual(work.sum_time_sec, 28800.0)
        self.assertEqual(work.sum_over_time_sec, '02:00')
        self.assertEqual(work.work_object, 'Test Work Object')
        self.assertEqual(work.work_type, 'Test Work Type')
        self.assertEqual(work.coffee_food, 'Coffee')
        self.assertEqual(work.fuel, '10.00')
        self.assertEqual(work.prepayment, '20.00')
        self.assertEqual(work.phone_costs, '15.00')
        self.assertEqual(work.payment, '100.00')
        self.assertEqual(work.payment_hour, 10.0)

    def test_user_field(self):
        work = Work.objects.get(id=1)
        users = work.user.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'test_user')

    def test_work_objects_field(self):
        # Create a sample WorkObject object
        work_object = WorkObject.objects.create(name='Test Work Object', coffee_food=10.5)
        work = Work.objects.get(id=1)
        work.work_objects.add(work_object)
        work_objects = work.work_objects.all()
        self.assertEqual(work_objects.count(), 1)
        self.assertEqual(work_objects[0].name, 'Test Work Object')
        self.assertEqual(work_objects[0].coffee_food, 10.5)


####################################################################################
####################################################################################
####################################################################################
####################################################################################


class WorkTypeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample CustomUser object
        user = CustomUser.objects.create(username='test_user')

        # Create a sample WorkType object
        WorkType.objects.create(name='Test Work Type').user.add(user)

    def test_str_representation(self):
        work_type = WorkType.objects.get(id=1)
        self.assertEqual(str(work_type), 'Test Work Type')

    def test_fields(self):
        work_type = WorkType.objects.get(id=1)
        self.assertEqual(work_type.name, 'Test Work Type')

    def test_user_field(self):
        work_type = WorkType.objects.get(id=1)
        users = work_type.user.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'test_user')


####################################################################################
####################################################################################
####################################################################################
####################################################################################


class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample CustomUser object
        user = CustomUser.objects.create(username='test_user')

        # Create a sample WorkObject object
        work_object = WorkObject.objects.create(name='Test Work Object', coffee_food=10.5)

        # Create a sample Task object
        Task.objects.create(
            date_obj=timezone.now(),
            date=datetime.now().strftime('%d-%m-%Y'),
            user=user,
            username='Test User',
            work_object=work_object,
            content='Test Task Content',
            done=False,
        )

    def test_str_representation(self):
        task = Task.objects.get(id=1)
        self.assertEqual(str(task), 'Test User')

    def test_fields(self):
        task = Task.objects.get(id=1)
        self.assertEqual(task.date, datetime.now().strftime('%d-%m-%Y'))
        self.assertEqual(task.user.username, 'test_user')
        self.assertEqual(task.username, 'Test User')
        self.assertEqual(task.work_object.name, 'Test Work Object')
        self.assertEqual(task.content, 'Test Task Content')
        self.assertFalse(task.done)


####################################################################################
####################################################################################
####################################################################################
####################################################################################


class MessageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample CustomUser object
        sender = CustomUser.objects.create(username='sender')

        # Create a sample WorkObject object
        work_object = WorkObject.objects.create(name='Test Work Object')

        # Create a sample Message object
        Message.objects.create(
            sender=sender,
            name='Test Message',
            work_object=work_object,
            content='Test Message Content',
            timestamp=timezone.now(),
            day='Monday',
            time='10:00 AM',
            for_sender_is_read=False,
            for_recipient_is_read=False,
        )

    def test_str_representation(self):
        message = Message.objects.get(id=1)
        self.assertEqual(str(message), 'Test Message')

    def test_fields(self):
        message = Message.objects.get(id=1)
        self.assertEqual(message.sender.username, 'sender')
        self.assertEqual(message.name, 'Test Message')
        self.assertEqual(message.work_object.name, 'Test Work Object')
        self.assertEqual(message.content, 'Test Message Content')
        self.assertEqual(message.day, 'Monday')
        self.assertEqual(message.time, '10:00 AM')
        self.assertFalse(message.for_sender_is_read)
        self.assertFalse(message.for_recipient_is_read)


####################################################################################
####################################################################################
####################################################################################
####################################################################################


class VacationsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample CustomUser object
        user = CustomUser.objects.create(username='test_user')

        # Create a sample Vacations object
        Vacations.objects.create(
            user=user,
            username='Test User',
            year='2023',
            date='01-01-2023',
            v_from='01-01-2023',
            v_to='05-01-2023',
            type='Annual',
            actually_days_to_use=5,
            days_used_in_current_year=3,
            days_to_use_in_last_year=2,
            days_used_in_last_year=1,
            days_planned=4,
            consideration=False,
            accepted=False,
        )

    def test_str_representation(self):
        vacations = Vacations.objects.get(id=1)
        self.assertEqual(str(vacations), '1')

    def test_fields(self):
        vacations = Vacations.objects.get(id=1)
        self.assertEqual(vacations.user.username, 'test_user')
        self.assertEqual(vacations.username, 'Test User')
        self.assertEqual(vacations.year, '2023')
        self.assertEqual(vacations.date, '01-01-2023')
        self.assertEqual(vacations.v_from, '01-01-2023')
        self.assertEqual(vacations.v_to, '05-01-2023')
        self.assertEqual(vacations.type, 'Annual')
        self.assertEqual(vacations.actually_days_to_use, 5)
        self.assertEqual(vacations.days_used_in_current_year, 3)
        self.assertEqual(vacations.days_to_use_in_last_year, 2)
        self.assertEqual(vacations.days_used_in_last_year, 1)
        self.assertEqual(vacations.days_planned, 4)
        self.assertFalse(vacations.consideration)
        self.assertFalse(vacations.accepted)


####################################################################################
####################################################################################
####################################################################################
####################################################################################


class VacationRequestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample Vacations object
        vacations = Vacations.objects.create(date='01-01-2023')

        # Create a sample VacationRequest object
        VacationRequest.objects.create(v_request=vacations)

    def test_str_representation(self):
        vacation_request = VacationRequest.objects.get(id=1)
        self.assertEqual(str(vacation_request), '01-01-2023')

    def test_fields(self):
        vacation_request = VacationRequest.objects.get(id=1)
        self.assertEqual(vacation_request.v_request.date, '01-01-2023')