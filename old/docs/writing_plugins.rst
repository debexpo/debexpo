.. _writing-plugins:

===============
Writing plugins
===============

Writing plugins for debexpo is easy. You only need to know a bit of
python and you're away! A sample QA plugin is shown here::

    import logging

    from debexpo.lib import constants
    from debexpo.lib.base import *
    from debexpo.plugins import BasePlugin

    log = logging.getLogger(__name__)

    class YInNamePlugin(BasePlugin):

        def test_y_in_name(self):
            log.debug('Checking whether the name has a letter Y in its name')

            package_name = self.changes['Source']

            if 'y' in package_name:
                self.passed('y-in-name', None, constants.PLUGIN_SEVERITY_INFO)
            else:
                self.failed('no-y-in-name', None, constants.PLUGIN_SEVERITY_INFO)

    plugin = YInNamePlugin

    outcomes = {
        'y-in-name' : { 'name' : 'Package has the letter Y in its name' },
        'no-y-in-name' : { 'name' : 'Package has no letter Y in its name' },
    }

This plugin looks at a package and looks whether the package name has the
letter Y in it. It has two outcomes. It will pass the plugin if a letter
Y is present. It will fail the test, albeit with a low priority, if a
letter Y is not present.

A walk through
==============

Lines 1-7::

    import logging

    from debexpo.lib import constants
    from debexpo.lib.base import *
    from debexpo.plugins import BasePlugin

    log = logging.getLogger(__name__)

These are just imports of the logger, debexpo constants, and other classes
that you need not worry about. These imports and statements should always
be present in a plugin.

Line 9::

    class YInNamePlugin(BasePlugin):

This starts the definition of the plugin, which must extend on the BasePlugin
class. The name of this class doesn't matter, as you will see in a bit.

Line 11::

    def test_y_in_name(self):

This starts the actual plugin. All methods in the plugin starting with the name
"`test`" will be run. This allows you to have as many tests in each plugin as you
wish. You may also have other methods that, as long as they do not start with
the word "`test`" will not be run automatically.

Line 12::

    log.debug('Checking whether the name has a letter Y in its name')

This is a simple logging statement. This should be used well and frequently
if necessary. It uses the standard python `logging module <http://docs.python.org/lib/module-logging.html>`_.

Line 14::

    package_name = self.changes['Source']

This gets the name of the package by getting the `Source` field from the `changes` file.
Most plugin-running locations will have a `self.changes` ``debexpo.lib.changes.Changes``
object that can be used and inspected in the plugin.

Line 17::

    self.passed('y-in-name', None, constants.PLUGIN_SEVERITY_INFO)

This records a pass for the plugin. The ``passed`` and ``failed`` methods
both have three arguments:

.. autoclass:: debexpo.plugins.BasePlugin
   :members: passed,failed,info

As you can see, there is another method called ``info``. This is for outcomes
that do not mean there was a success, and similarly do not mean there was a
failure. The YInNamePlugin is actually a good example of where the ``info`` method
should be used. It defaults the severity to "info".

The `outcome` first variable of the functions should be a string relating to the
key of the ``outcomes`` dictionary at the bottom of the file. The value of each
key in this dictionary should be another dictionary with at least one key/value pair:
`name`: This should be an English string as to what the outcome actually means.

Line 21::

    plugin = YInNamePlugin

This shows that the name of the plugin really does not matter. As long as the
``plugin`` variable points to a class based on BasePlugin, it is fine.

Other plugins
=============

This is a very brief outline of a simple QA plugin. However, there are different
stages of plugin execution. The :ref:`plugins` page tells more about stock plugins,
what they do, and when they should run. You should use these plugins as a reference
for future plugins.

If you get stuck, do not hesitate to pop by the `mailing list <http://workaround.org/cgi-bin/mailman/listinfo/debexpo-devel>`_.
