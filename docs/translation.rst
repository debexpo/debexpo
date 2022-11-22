Translation
===========

Debexpo is entirely translatable using django i18n system and gettext.

When working on translation, always make sure that you execute commands from the
``debexpo/`` directory, not the root of the repository.

Translate text from debexpo
---------------------------

Add a new language
~~~~~~~~~~~~~~~~~~

To add a new language, simply invoke `manage.py makemessages -l`, followed by
the language code::

    pushd debexpo
    python3 ../manage.py makemessages --keep-pot --add-location file -l de
    popd

Update translation sources
~~~~~~~~~~~~~~~~~~~~~~~~~~

To update translation sources from python code, run `manage.py makemessages
-a`::

    pushd debexpo
    python3 ../manage.py makemessages --keep-pot --add-location file -a
    popd

Work on translation
~~~~~~~~~~~~~~~~~~~

Use your favorite translation software to work on the translation files.

Generate translation binaries files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To actually show translated text on the software, django uses a binary form of
the translation files, called MO. Those file are generated automatically
generated on build time by the ``setup.py``. While developping, you might need
to update those files manually. In order to do so, run::

    pushd debexpo
    python3 ../manage.py compilemessages
    popd

Make debexpo text translatable
------------------------------

For detailed documentation, see `Django translation`_

On templates
~~~~~~~~~~~~

Use the ``trans`` and ``blocktrans`` tag.

The ``i18n`` module must be loaded at the begining for the template:

.. code-block:: django

    {% load i18n %}

    {% trans 'this one line text will be translated' %}

    {% blocktrans with local_value=my_var trimmed %}
    This text will be translated to.

    Note that no further tag will be accepeted in the blocktrans.
    Also, variable are only available from the with keyword declared in the
    block: {{ local_value }}.

    When working with text that does not need newlines (e.g. html), always use
    the 'trimmed' option of 'blocktrans'. This allow to generate much nicer po
    files.
    {% endblocktrans %}

In python code
~~~~~~~~~~~~~~

Use the gettext helper provided by django:

.. code-block:: python

    from django.utils.translation import gettext as _

    ...
    text = _("This text will be available for translation.")

.. _Django translation: https://docs.djangoproject.com/en/2.2/topics/i18n/translation/
