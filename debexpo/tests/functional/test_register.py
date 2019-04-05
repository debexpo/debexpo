from debexpo.tests import TestController, url
from debexpo.model import meta
from debexpo.model.users import User
from debexpo.lib import constants
import pylons.test


class TestRegisterController(TestController):

    def setUp(self):
        self._setup_models()

    def test_maintainer_signup(self, actually_delete_it=True):
        count = meta.session.query(User) \
            .filter(User.email == 'mr_me@example.com') \
            .count()
        self.assertEquals(count, 0)

        pylons.test.pylonsapp.config['debexpo.testsmtp'] = '/tmp/debexpo.msg'
        self.app.post(url(controller='register', action='register'),
                      {'name': 'Mr. Me',
                       'password': 'password',
                       'password_confirm': 'password',
                       'commit': 'yes',
                       'email': 'mr_me@example.com',
                       'sponsor': '0'})

        count = meta.session.query(User) \
            .filter(User.email == 'mr_me@example.com') \
            .count()
        self.assertEquals(count, 1)

        user = meta.session.query(User) \
            .filter(User.email == 'mr_me@example.com') \
            .one()

        # delete it
        if actually_delete_it:
            meta.session.delete(user)
        else:
            return user

    def test_maintainer_signup_with_duplicate_name(self):
        self.test_maintainer_signup(actually_delete_it=False)

        self.app.post(url(controller='register', action='register'),
                      {'name': 'Mr. Me',
                       'password': 'password',
                       'password_confirm': 'password',
                       'commit': 'yes',
                       'email': 'mr_me_again@example.com',
                       'sponsor': '0'})

        count = meta.session.query(User) \
            .filter(User.email == 'mr_me_again@example.com') \
            .count()
        self.assertEquals(count, 0)
        # The assertion is that there are no matching users by
        # email address.
        #
        # That is because both user accounts have the same name,
        # and that is not permitted by the backend.
        #
        # You might think it's silly to assert that we don't
        # do anything. Really, the point is to make sure that
        # the backend does not crash; before we wrote this test,
        # this case would actuallly raise an unhandled
        # IntegrityError from the database.

        # Now, finally, delete that User that we created.
        meta.session.delete(
            meta.session.query(User).filter(
                User.email == 'mr_me@example.com').one())

    def test_sponsor_signup_wrong_email(self):
        pylons.test.pylonsapp.config['debexpo.testsmtp'] = '/tmp/debexpo.msg'
        response = self.app.post(url(controller='register', action='register'),
                                 {'name': 'Mr. Me',
                                  'password': 'password',
                                  'password_confirm': 'password',
                                  'commit': 'yes',
                                  'email': 'mr_me@example.org',
                                  'sponsor': '1'})
        self.assertEqual(response.status_int, 200)
        testtext = '{}'.format('A sponsor account must be registered with your',
                               ' @debian.org address')
        self.assertTrue(testtext in response)
        count = meta.session.query(User) \
            .filter(User.email == 'mr_me@example.com') \
            .count()
        self.assertEquals(count, 0)

    def test_sponsor_signup(self):
        pylons.test.pylonsapp.config['debexpo.testsmtp'] = '/tmp/debexpo.msg'
        response = self.app.post(url(controller='register', action='register'),
                                 {'name': 'Mr. Me Debian',
                                  'password': 'password',
                                  'password_confirm': 'password',
                                  'commit': 'yes',
                                  'email': 'mr_me@debian.org',
                                  'sponsor': '1'})

        self.assertEqual(response.status_int, 200)
        user = meta.session.query(User) \
            .filter(User.email == 'mr_me@debian.org') \
            .first()
        self.assertEquals(user.status, constants.USER_STATUS_DEVELOPER)

        user = meta.session.query(User) \
            .filter(User.email == 'mr_me@debian.org') \
            .one()
        meta.session.delete(user)

    def test_activation_wrong_key(self):
        response = self.app.get(url(controller='register', action='activate',
                                    id='that_key_should_not_exist'),
                                expect_errors=True)
        self.assertEqual(response.status_int, 404)

    def test_successful_activation(self):
        self.test_maintainer_signup(actually_delete_it=False)
        user = meta.session.query(User) \
            .filter(User.email == 'mr_me@example.com') \
            .one()
        response = self.app.get(url(controller='register', action='activate',
                                    id=user.verification),
                                expect_errors=True)
        self.assertEqual(response.status_int, 200)
        meta.session.delete(user)
