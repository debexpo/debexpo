from debexpo.tests import TestController, url
from debexpo.model import meta
from debexpo.model.users import User

class TestRegisterController(TestController):

    def test_maintainer_signup(self):
        count = meta.session.query(User).filter(User.email=='mr_me@example.com').count()
        self.assertEquals(count, 0)

        self.app.post(url(controller='register', action='maintainer'),
                                 {'name': 'Mr. Me',
                                  'password': 'password',
                                  'password_confirm': 'password',
                                  'commit': 'yes',
                                  'email': 'mr_me@example.com'})

        count = meta.session.query(User).filter(User.email=='mr_me@example.com').count()
        self.assertEquals(count, 1)

        user = meta.session.query(User).filter(User.email=='mr_me@example.com').one()
        # delete it
        meta.session.delete(user)

