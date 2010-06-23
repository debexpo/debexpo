from debexpo.tests import *

class TestSoapController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='soap'))
        # Test response...
