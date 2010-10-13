.. _plugins:

=======
Plugins
=======

debexpo has many "plugins" for different purposes. Some are to make sure packages
are in a good condition for the archive, some make sure the packages can even
be imported as they might be damaged in the upload and some simply find information
about the package, such as the programming language used.

Here is a list of the plugins installed by standard with debexpo:

buildsystem
===========

This plugin looks at the package and by looking at the package's `Build-Depends`, it
tries to work out what build system the package is using. The possible options are:

* CDBS
* debhelper
* debhelper v7
* unknown

This is an informational QA plugin and should only be run in that stage, between
upload and successful importing.

changeslist
===========

This plugin emails the ``debexpo.changes_list`` email address with an email on every
package upload in exactly the same format as the `debian-devel-changes <http://lists.debian.org/debian-devel-changes/>`_
mailing list.

This is a post-successful-upload plugin and should only be run in that stage, after
the package has successfully been imported into the archive.

checkfiles
==========

This plugin checks whether all the files referenced in the `changes` file are present.
It also checks each file's md5sum to make sure it matches the md5sum given in the
`changes` file.

If any part of this plugin fail, the whole upload should fail as this is a critical
error.

This is a post-upload plugin and should only be run in that stage, straight after
the package has been uploaded onto the system, but before any package manipulation.

closedbugs
==========

This plugin checks on the `Debian BTS <http://bugs.debian.org/>`_ whether bugs that
are reported to be closed in the package upload do actually belong to the package
being uploaded.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

controlfields
=============

This plugin looks for additional ``debian/control`` fields, such as `Vcs-Browser`
and `Homepage`.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

debianqa
========

This plugin tests a number of things with the uploaded package against information
in Debian:

* whether the package is an NMU
* whether the package is already in Debian
* whether the package maintainer is the Debian maintainer
* whether the package introduces a new maintainer
* whether the package closes any wnpp bugs
* finds information about any ITPs closed
* finds previous sponsors of the package

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

diffclean
=========

This package looks at the package's `diff.gz` and makes sure that it is clean.
This means that it does not include any changes to files outside of the `debian`
directory as this is considered bad practice.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

getorigtarball
==============

This package looks whether the package is missing an `original tarball` and if
so, it tries to download the appropriate file from the Debian archives. You
can set your favourite Debian mirror with the ``debexpo.debian_mirror`` config
option.

This is a post-upload plugin and should only be run in that stage, straight after
the package has been uploaded onto the system, but before any package manipulation.

gpgsigned
=========

This plugin checks to see whether the `changes` and `dsc` files have been GPG
signed.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

lintian
=======

This plugin runs `lintian <http://lintian.debian.org/>`_ on the package.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

maintaineremail
===============

This plugin looks to see whether the email of the uploader of the package is
the same as the email of the maintainer of the package.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

native
======

This plugin looks to see whether the package is a native package.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.

notupoader
==========

This plugin checks to make sure that the uploader of the package is the owner
of any subsequent package uploads of the same name.

If the plugin finds that there has been a previous upload of the package, and
the previous uploader is different from the new uploader, the import will stop.

This is a post-upload plugin and should only be run in that stage, straight after
the package has been uploaded onto the system, but before any package manipulation.

removepackage
=============

This plugin removes a package and all of its associated comments, metrics and
information from the database.

This is a post-upload-to-debian plugin that should only be run after the package
has been uploaded to Debian.

watchfile
=========

This plugin checks to see whether the package has a watch file. If it does,
then the plugin will check the watch file to make sure it works. If it does
work, then it will report back on any new upstream versions.

This is an information QA plugin and should only be run in that stage, between
upload and successful importing.
