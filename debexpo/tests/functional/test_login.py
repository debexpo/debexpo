from debexpo.tests import *
from pylons import session

class TestLoginController(TestController):
    _AUTHDATA = {'email': 'email@example.com',
                 'password': 'password',
                 'commit':'Commit'}

    def setUp(self):
        self._setup_models()
        self._setup_example_user()

    def tearDown(self):
        self._remove_example_user()

    def test_index(self):
        response = self.app.get(url(controller='login', action='index'))
        # Test response...

    def test__login(self):
        response = self.app.post(url(controller='login', action='index'),
                                 self._AUTHDATA)
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))

    def test__login_path_before_login(self):
        response = self.app.get(url(controller='packages', action='my'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('login')))
        response = self.app.post(url(controller='login', action='index'),
                                 self._AUTHDATA)
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url(controller='packages', action='my')))

    def test_logout_loggedout(self):
        response = self.app.get(url(controller='login', action='logout'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('index')))

    def test_logout_loggedin(self):
        response = self.app.post(url(controller='login', action='index'),
                                 self._AUTHDATA)
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('my')))
        response = self.app.get(url(controller='login', action='logout'))
        self.assertEquals(response.status_int, 302)
        self.assertTrue(response.location.endswith(url('index')))
