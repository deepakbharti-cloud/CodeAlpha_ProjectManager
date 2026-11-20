from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import *
class PMTest(TestCase):
    def test_flow(self):
        a, b = Client(), Client()
        for c, n in ((a, 'alice'), (b, 'bob')):
            c.post('/register/', {'username': n, 'password1': 'Str0ngPass!9', 'password2': 'Str0ngPass!9'})
        a.post('/', {'name': 'Demo'}); p = Project.objects.get()
        a.post(f'/project/{p.pk}/member/', {'username': 'bob'})
        bob = User.objects.get(username='bob')
        a.post(f'/project/{p.pk}/task/', {'title': 'T1', 'assignee': bob.pk})
        t = Task.objects.get(); self.assertEqual(t.assignee, bob)
        self.assertEqual(bob.notifications.count(), 2)
        b.post(f'/task/{t.pk}/', {'text': 'on it'}); b.post(f'/task/{t.pk}/', {'status': 'doing'})
        t.refresh_from_db(); self.assertEqual(t.status, 'doing'); self.assertEqual(t.comments.count(), 1)
        self.assertEqual(User.objects.get(username='alice').notifications.count(), 1)
        self.assertEqual(b.get(f'/project/{p.pk}/').status_code, 200)
        self.assertEqual(b.get('/notifications/').status_code, 200)
        c = Client(); c.post('/register/', {'username': 'eve', 'password1': 'Str0ngPass!9', 'password2': 'Str0ngPass!9'})
        self.assertEqual(c.get(f'/project/{p.pk}/').status_code, 404)
