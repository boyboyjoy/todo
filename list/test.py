from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from list.forms import CreateBoardForm, ReplaceTaskForm, CreateTaskForm, AddTagForm
from list.models import Board, Task

USER_EMAIL = 'user@user.com'
BOARD_LIST_TEMPLATE = 'BoardList.html'

class WorkLoginSystem(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='test_user',
                                             email=USER_EMAIL, password='Password1234')
        test_user.save()

    def test_get_correct_login_page(self):
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'LoginPage.html')

    def test_login_by_email_and_username(self):
        login = self.client.login(username='test_user', password='Password1234')
        self.assertEqual(login, False)
        login = self.client.login(username=USER_EMAIL, password='Password1234')
        self.assertEqual(login, True)
        response = self.client.get(reverse('main-page'))
        self.assertTemplateUsed(response, BOARD_LIST_TEMPLATE)


class WorkSignUpSystem(TestCase):

    def setUp(self):
        User.objects.create_user(username='test_user1', email='test@user1.com',
                                 password='test_user1')

    def test_create_user_with_not_unique_email(self):
        username = 'test_user1'
        email = 'test@user1.com'
        password = 'test_user1'
        response = self.client.get(reverse('sign_up'))
        self.assertTemplateUsed(response, 'SignUp.html')
        self.assertEqual(User.objects.all().count(), 1)
        username = 'test_user2'
        response = self.client.post(reverse('sign_up'), {'username': username,
                                                         'email': email, 'password': password})
        self.assertEqual(User.objects.all().count(), 1)
        email = 'test@user2.com'
        response = self.client.post(reverse('sign_up'), {'username': username,
                                                         'email': email, 'password': password})
        self.assertEqual(User.objects.all().count(), 2)

    def test_validate_format_password_by_sign_up(self):
        username = 'test_user2'
        email = 'test@user2.com'
        password = '123123'
        self.client.post(reverse('sign_up'), {'username': username,
                                              'email': email, 'password': password})
        self.assertEqual(User.objects.all().count(), 1)
        password = 'Z123123'
        self.client.post(reverse('sign_up'), {'username': username,
                                              'email': email, 'password': password})
        self.assertEqual(User.objects.all().count(), 1)
        password = '123123123'
        self.client.post(reverse('sign_up'), {'username': username,
                                              'email': email, 'password': password})
        self.assertEqual(User.objects.all().count(), 1)
        password = 'Z123123123'
        self.client.post(reverse('sign_up'), {'username': username,
                                              'email': email, 'password': password})
        self.assertEqual(User.objects.all().count(), 2)


class WorkingBoardListPage(TestCase):

    def setUp(self):
        User.objects.create_user(username='user',
                                 email=USER_EMAIL, password='user1234')
        User.objects.create_superuser(username='admin', email='admin@admin.com',
                                      password='admin1234')
        admin = User.objects.get(username='admin')
        for i in range(0, 3):
            admin.board_set.create(title='admin-board #{0}'.format(i))
        user = User.objects.get(username='user')
        for i in range(0, 3):
            user.board_set.create(title='user-board #{0}'.format(i))

    def test_get_board_list_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        response = self.client.get(reverse('main-page'))
        self.assertTemplateUsed(response, BOARD_LIST_TEMPLATE)
        self.assertEqual(response.context['board_list'].count(), 3)

    def test_visibility_alien_boards(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 3)
        self.client.log_out()
        self.client.login(username='admin@admin.com', password='admin1234')
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 6)

    def test_create_board_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        response = self.client.get(reverse('create_board'))
        self.assertTemplateUsed(response, 'CreateBoard.html')
        self.assertIsInstance(response.context['create_board_form'], CreateBoardForm)

    def test_create_board(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        self.assertEqual(Board.objects.all().count(), 6)
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 3)
        response = self.client.post(reverse('create_board'), {'title': 'Board create by form', 'color': '#AAABBB'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Board.objects.all().count(), 7)
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 4)
        self.client.log_out()
        self.client.login(username='admin@admin.com', password='admin1234')
        self.assertEqual(Board.objects.all().count(), 7)
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 7)
        response = self.client.post(reverse('create_board'), {'title': 'Board create by form', 'color': '#AAABBB'})
        self.assertEqual(Board.objects.all().count(), 8)
        response = self.client.get(reverse('main-page'))
        self.assertEqual(response.context['board_list'].count(), 8)

    def test_incorrect_board_color_create(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        response = self.client.post(reverse('create_board'), {'title': 'test_Board', 'color': '123123'})
        self.assertTemplateUsed(response, 'CreateBoard.html')
        response = self.client.post(reverse('create_board'), {'title': 'test_Board', 'color': '#ABCABCABC'})
        self.assertTemplateUsed(response, 'CreateBoard.html')
        response = self.client.post(reverse('create_board'), {'title': 'test_Board', 'color': '#ABCABC'})
        self.assertEqual(response.status_code, 302)

    def test_logout_system(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('main-page'))
        self.assertTemplateUsed(response, 'LoginPage.html')


class WorkTaskListPage(TestCase):
    def setUp(self):
        User.objects.create_user(username='user',
                                 email=USER_EMAIL, password='user1234')
        User.objects.create_superuser(username='admin', email='admin@admin.com',
                                      password='admin1234')
        admin = User.objects.get(username='admin')
        admin_board = admin.board_set.create(title='admin-board #1')
        user = User.objects.get(username='user')
        user_board = user.board_set.create(title='user-board #1')
        user_board.task_set.create(description='test_task',
                                   scheduled_deadline='2020-10-10',
                                   real_deadline='2020-10-10', task_status='started')
        admin_board.task_set.create(description='test_task',
                                    scheduled_deadline='2020-10-10',
                                    real_deadline='2020-10-10', task_status='started')

    def test_get_task_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        response = self.client.get(reverse('Board', kwargs={'pk': user_board.id}))
        self.assertTemplateUsed(response, 'TaskList.html')
        self.assertEqual(response.context['task_list'].count(), 1)
        self.client.login(username='admin@admin.com', password='admin1234')
        user = User.objects.get(username='admin')
        user_board = Board.objects.filter(user_creator=user)[0]
        response = self.client.get(reverse('Board', kwargs={'pk': user_board.id}))
        self.assertTemplateUsed(response, 'TaskList.html')
        self.assertEqual(response.context['task_list'].count(), 1)

    def test_back_button_on_task_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        response = self.client.get(reverse('Board', kwargs={'pk': user_board.id}))
        response = self.client.get(reverse('main-page'))
        self.assertTemplateUsed(response, BOARD_LIST_TEMPLATE)

    def test_delete_board(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        self.assertIsInstance(user_board, Board)
        self.assertEqual(Board.objects.all().count(), 2)
        self.client.post(reverse('delete_board', kwargs={'pk': user_board.id}))
        self.assertEqual(Board.objects.all().count(), 1)

    def test_edit_board(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        response = self.client.post(reverse('edit_board', kwargs={'pk': user_board.id}), {'title': 'NewBoardTitle',
                                                                                          'color': '#AAAAAA'})
        self.assertEqual(Board.objects.filter(user_creator=user)[0].title, 'NewBoardTitle')
        self.assertEqual(response.status_code, 302)

    def test_create_task(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        self.assertEqual(Task.objects.all().count(), 2)
        response = self.client.post(reverse('create_task',
                                            kwargs={'pk': user_board.id}),
                                    {'description': 'ggwp',
                                     'scheduled_deadline': '2020-10-10',
                                     'real_deadline': '2020-10-15',
                                     'task_status': 'started'})
        self.assertEqual(Task.objects.all().count(), 3)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('create_task', kwargs={'pk': user_board.id}))
        self.assertTemplateUsed(response, 'CreateTask.html')
        self.assertIsInstance(response.context['create_task_form'], CreateTaskForm)


class WorkTaskDetailPage(TestCase):
    def setUp(self):
        User.objects.create_user(username='user',
                                 email=USER_EMAIL, password='user1234')
        User.objects.create_superuser(username='admin', email='admin@admin.com',
                                      password='admin1234')
        admin = User.objects.get(username='admin')
        admin_board = admin.board_set.create(title='admin-board #1')
        user = User.objects.get(username='user')
        user_board = user.board_set.create(title='user-board #1')
        user_board.task_set.create(description='test_task',
                                   scheduled_deadline='2020-10-10',
                                   real_deadline='2020-10-10', task_status='started')
        admin_board.task_set.create(description='test_task',
                                    scheduled_deadline='2020-10-10',
                                    real_deadline='2020-10-10', task_status='started')

    def test_get_task_detail_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        response = self.client.get(reverse('detail_task', kwargs={'board_pk': user_board.id,
                                                                  'task_pk': user_task.id}))
        self.assertTemplateUsed(response, 'DetailTask.html')
        self.assertEqual(user_task, response.context['task'])

    def test_delete_task(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        self.assertEqual(Task.objects.all().count(), 2)
        self.client.get(reverse('delete_task', kwargs={'board_pk': user_board.id,
                                                       'task_pk': user_task.id}))
        self.assertEqual(Task.objects.all().count(), 1)

    def test_replace_copy_task_page_replace(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        admin = User.objects.get(username='admin')
        user_board = Board.objects.filter(user_creator=user)[0]
        admin_board = Board.objects.filter(user_creator=admin)[0]
        admin_task = admin_board.task_set.all()[0]
        response = response = self.client.get(reverse('replace_task', kwargs={'board_pk': admin_board.id,
                                                                              'task_pk': admin_task.id}))
        self.assertEqual(response.context['board_list'].count(), 1)
        self.client.log_out()
        self.client.login(username='admin@admin.com', password='admin1234')
        response = response = self.client.get(reverse('replace_task', kwargs={'board_pk': admin_board.id,
                                                                              'task_pk': admin_task.id}))
        self.assertEqual(response.context['board_list'].count(), 2)
        self.assertIsInstance(response.context['replace_task_form'], ReplaceTaskForm)
        self.assertTemplateUsed(response, 'Replace_copy_task.html')
        self.assertEqual(user_board.task_set.all().count(), 1)
        self.client.post(reverse('replace_task', kwargs={'board_pk': admin_board.id,
                                                                    'task_pk': admin_task.id}),
                                    {'new_parent_board': user_board.id, 'replace': ['replace']})
        self.assertEqual(user_board.task_set.all().count(), 2)
        self.assertEqual(admin_board.task_set.all().count(), 0)

    def test_replace_copy_task_page_copy(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        self.assertEqual(user_board.task_set.all().count(), 1)
        self.client.post(reverse('replace_task', kwargs={'board_pk': user_board.id,
                                                         'task_pk': user_task.id}),
                         {'new_parent_board': user_board.id, 'copy': ['copy']})
        self.assertEqual(user_board.task_set.all().count(), 2)

    def test_add_tag_get_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        response = self.client.get(reverse('add_tag', kwargs={'board_pk': user_board.id,
                                                              'task_pk': user_task.id}))
        self.assertTemplateUsed(response, 'AddTag.html')
        self.assertIsInstance(response.context['add_tag_form'], AddTagForm)

    def test_add_tag_adding_tag(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        self.assertEqual(user_task.tag_set.all().count(), 0)
        self.client.post(reverse('add_tag', kwargs={'board_pk': user_board.id,
                                                    'task_pk': user_task.id}), {'tag': 'zxc'})
        user_task = user_board.task_set.all()[0]
        self.assertEqual(user_task.tag_set.all().count(), 1)
        self.assertEqual(user_task.tag_set.all()[0].text, 'zxc')

    def test_edit_task_get_page(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        response = self.client.get(reverse('edit_task', kwargs={'board_pk': user_board.id,
                                                                'task_pk': user_task.id}))
        self.assertTemplateUsed(response, 'EditTask.html')
        self.assertIsInstance(response.context['edit_task_form'], CreateTaskForm)

    def test_edit_task(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        user_task = user_board.task_set.all()[0]
        self.client.post(reverse('edit_task', kwargs={'board_pk': user_board.id,
                                                      'task_pk': user_task.id}),
                         {'description': 'new_description',
                          'scheduled_deadline': '2020-07-07',
                          'real_deadline': '2020-08-08', 'task_status': 'completed'})
        user_task = user_board.task_set.all()[0]
        self.assertEqual(user_task.description, 'new_description')
        self.assertEqual(user_task.task_status, 'completed')

    def search_by_tag(self):
        self.client.login(username=USER_EMAIL, password='user1234')
        user = User.objects.get(username='user')
        user_board = Board.objects.filter(user_creator=user)[0]
        task1 = user_board.task_set.create(description='TASK 1', scheduled_deadline='2020-01-01',
                                           real_deadline='2020-02-02', task_status='canceled')
        task2 = user_board.task_set.create(description='TASK 2', scheduled_deadline='2020-01-01',
                                           real_deadline='2020-02-02', task_status='canceled')
        response = self.client.post(reverse('add_tag', kwargs={'board_pk': user_board.id,
                                                               'task_pk': task1.id}), {'tag': 'zxc'})
        response = self.client.post(reverse('add_tag', kwargs={'board_pk': user_board.id,
                                                               'task_pk': task2.id}), {'tag': 'zxc'})
        response = self.client.get(reverse('search_tag', kwargs={'tag'}))
        self.assertEqual(len(response.context['list_for_test']), 2)
