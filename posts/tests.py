from django.test import TestCase, Client
from posts.models import User, Post, Group


# Create your tests here.
#
class TestProfiles(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", email="test@mail.com", password="12345")

    def test_profile(self):
        response = self.client.get('/test_user/')
        self.assertEqual(response.status_code, 200, msg='Нет страницы профиля')

    def test_new_post(self):
        self.client.login(username='test_user', password='12345')
        self.client.post('/new', {'text': 'test text'})
        response = self.client.get('/test_user/')
        author = response.context['author']
        self.assertEqual(Post.objects.filter(author=author).count(), 1)

    def test_not_log_user(self):
        response = self.client.get('/new')
        self.assertRedirects(response, "/auth/login/?next=/new")

    def test_new_post_index(self):
        self.client.login(username='test_user', password='12345')
        self.client.post('/new', {'text': 'test text 1256789999'})
        #  проверка index
        response = self.client.get('')
        self.assertContains(response, "test text 1256789999", count=None, status_code=200, msg_prefix='', html=True)
        # проверка user page
        response = self.client.get('/test_user/')
        self.assertContains(response, "test text 1256789999", count=None, status_code=200, msg_prefix='', html=True)
        # проверка post page
        # author = User.objects.get(username='test_user') # возможно не понадобится
        # post_id = Post.objects.get(author=author).id
        response = self.client.get('/test_user/1/', follow=True)
        self.assertContains(response, "test text 1256789999", count=None, status_code=200, msg_prefix='', html=False)

    def test_auth_edit(self):
        self.client.login(username='test_user', password='12345')
        self.client.post('/new', {'text': 'test text 1256789999'})
        self.client.post('/test_user/1/edit/', {'text': 'test text 13666'})
        # проверка index
        response = self.client.get('')
        self.assertContains(response, "test text 13666", count=None, status_code=200, msg_prefix='', html=True)

    def test_404(self):
        response = self.client.get('/ser/1/', follow=True)
        self.assertEqual(response.status_code, 404)


class TestPictures(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", email="test@mail.com", password="12345")

    def test_tag(self):
        self.client.login(username='test_user', password='12345')
        Post.objects.create(text='test', author=self.user)
        with open('media/posts/1.jpg', 'rb') as img:
            self.client.post("/test_user/1/edit/", {'text': 'post with image', 'image': img})
        response = self.client.get('/test_user/1', follow=True)
        self.assertContains(response, "img")

    def test_group(self):  # !
        self.client.login(username='test_user', password='12345')
        Group.objects.create(title='cat', slug='catt', description='catze')
        self.group = Group.objects.get(id=1)
        Post.objects.create(text='test1717171771717171717171711771171711771717171', author=self.user, group=self.group)
        with open('media/posts/1.jpg', 'rb') as img:
            self.client.post("/test_user/1/edit/",
                             {'text': 'post with 111111111111111111111111111111111image', 'image': img})
        response = self.client.get('/', follow=True)
        self.assertContains(response, "img")
        response = self.client.get('/', follow=True)
        # print(response.content.decode())
        self.assertContains(response, "img")

    def test_format(self):  # !
        self.client.login(username='test_user', password='12345')
        Post.objects.create(text='test', author=self.user)
        with open('media/posts/12.txt', 'rb') as img:
            self.client.post("/test_user/1/edit/", {'text': 'post with image', 'image': img})
        response = self.client.get('/test_user/1', follow=True)
        self.assertEqual(response.status_code, 200)


class TestFollow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", email="test@mail.com", password="12345")
        User.objects.create_user(username="pacian", email="testtwo@mail.com", password="12345")


    # # Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок.
    def test_auth_foll(self):
        Post.objects.create(text='test', author=self.user)
        self.client.login(username='pacian', password='12345')
        # авторизованный в подписках
        self.client.get('/test_user/follow', follow=True)
        response = self.client.get('/follow/', follow=True)
        self.assertContains(response, "test_user")
        # # авторизованный нет в подписках
        self.client.get('/test_user/unfollow', follow=True)
        response = self.client.get('pacian/follow/', follow=True)
        self.assertNotContains(response, "test_user")

    def test_comment(self):
        Post.objects.create(text='rondo bondo', author=self.user)
        response = self.client.post('/test_user/1/comment',{'comment':'12sd'})
        self.assertNotEqual(response.status_code, 200)