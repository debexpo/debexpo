from debexpo.tests import *

class TestPackagesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='packages', action='index'))
        # Test response...
