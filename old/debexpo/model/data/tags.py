import debexpo.lib.constants

TAGS = {
  debexpo.lib.constants.SPONSOR_METRICS_TYPE_TECHNICAL: [
    ('CDBS', 'cdbs',
     'Your package makes use of the <a '
     'href="https://build-common.alioth.debian.org/">The Common Debian '
     'Build System</a>'),
    ('(Plain) debhelper', 'debhelper',
     'Your package makes use of the <a '
     'href="https://kitenet.net/~joey/code/debhelper/">debhelper</a> '
     'build system'),
    ('(Short) dh-style debhelper', 'dh',
     'Your package makes use of short <tt>dh(1)</tt> style build system'),
    ('No build helper / home brewed debian/rules', 'yada',
     'Your package is using a completely customized, yet <a '
     'href="https://www.debian.org/doc/debian-policy/ch-source.html'
     '#s-debianrules">policy compliant</a> <tt>debian/rules</tt> file, which '
     'does not make use of either debhelper or CDBS.'),
    ('NMUs', 'nmu', 'Your package is a <a '
     'href="https://www.debian.org/doc/manuals/developers-reference/pkgs.html'
     '#nmu">NMU</a>'),
    ('QA uploads', 'qa', 'Your package is a <a '
     'href="https://www.debian.org/doc/manuals/developers-reference/pkgs.html'
     '#nmu-qa-upload">QA upload</a>'),
    ('Backports', 'backports', 'Your package is a <a '
     'href="https://backports.debian.org/">backported package</a>'),
    ('Modified tarballs (but good reasons)', 'modified-tarballs',
     'Your package modified the original source tarball somehow. It does not '
     'match the original checksum anymore but you have a <a '
     'href="https://www.debian.org/doc/manuals/developers-reference'
     '/best-pkging-practices.html#bpp-origtargz">good reason</a> to do so'),
    ('Library package', 'library-package', 'You are packaging a <a '
     'href="https://www.debian.org/doc/debian-policy/ch-sharedlibs.html">'
     'policy compliant library</a>'),
    ('VCS snapshot tarballs', 'vcs-tarball', 'Your package is not based on a '
     'original source tarball at all but is based on a VCS snapshot',),
    ('contrib/non-free packages', 'non-free-package', 'Your package it '
     'targetting the <tt>contrib</tt> or <tt>non-free</tt> branches (<a '
     'href="https://www.debian.org/doc/debian-policy/ch-archive.html'
     '#s-sections">Information</a>)'),
    ('1.0 format packages', '1.0-format', 'Your package is using the 1.0 '
     'format (the traditional source format that is)'),
    ('3.0 format packages', '3.0-format', 'Your package is using the <a '
     'href="https://wiki.debian.org/Projects/DebSrc3.0">3.0/quilt</a> format'),
    ('Embedded code copies', 'embedded-code-copies', 'Your package  <a '
     'href="https://www.debian.org/doc/debian-policy/ch-source.html'
     '#s-embeddedfiles">makes use of embedded code copies in a reasonable '
     'way</a>'),
    ('DEP-5 copyright', 'dep5', 'Your package does make use of <a '
     'href="http://dep.debian.net/deps/dep5/">DEP-5</a> copyright files'),
    ('No Lintian cleanliness (but good reasons)', 'not-lintian-clean',
     'Your package is not <a href="https://lintian.debian.org/">Lintian clean'
     '</a> down to the informational level but you have a good reason why not'),
    ],

  debexpo.lib.constants.SPONSOR_METRICS_TYPE_SOCIAL: [
    ('Prospective DM/DD', 'prospective-dm-dd', 'You are willing to become a '
     '<a href="https://wiki.debian.org/DebianMaintainer">Debian Maintainer'
     '</a>/<a href="https://wiki.debian.org/DebianDeveloper">Debian Developer'
     '</a> some day'),
    ('(Willing to be) DM', 'applicant-is-dm', 'You are a <a '
     'href="https://wiki.debian.org/DebianMaintainer">Debian Maintainer</a> '
     'already, or you plan to become one soon'),
    ('(Willing to enter) NM', 'applicant-is-nm', 'You are in the <a '
     'href="https://nm.debian.org/">New Maintainer</a> process to become a '
     'developer or you plan to apply soon'),
    ('Signed GPG key', 'signed-gpg-key', 'Your GPG matches the <a href="'
     'https://lists.debian.org/debian-devel-announce/2010/09/msg00003.html'
     '">guidelines of the Debian keyring maintainers</a> and/or is signed by '
     'any Debian developer'),
    ('One time uploads', 'no-one-time-upload', 'Your package is a single shot '
     'upload'),
    ('Sharing a time zone', 'sharing-time-zone', 'You share a time zone with '
     'your sponsors. This can be useful to get together more easily'),
    ('Possibility to meet-up', 'possibility-to-meetup', 'You are living close '
     'to your sponsor and you are willing to meet him eventually'),
    ('Having already packages in Debian', 'maintainer-already', 'You do '
     'already have one or more packages in Debian'),
    ('Maintainer is not upstream', 'maintainer-is-not-upstream', 'You are not '
     'upstream of the package you are proposing to Debian'),
    ('Notable user base', 'notable-user-base', 'You can show us that people '
     'are already using your program and consider it useful'),
    ('Minimizing differences to derivatives', 'package-in-a-derivative',
     'Your package feeds changes introduced by any derivative back to Debian '
     'to minimize differences'),
    ]
}
