from debexpo.tests import *

class TestMyController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='my', action='index'))
        # Test response...
