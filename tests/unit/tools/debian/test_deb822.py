#   test_deb822.py - unit testing for deb822
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2019-2025 Baptiste Beauplat <lyknode@debian.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

from tests import TestController
from tempfile import NamedTemporaryFile

from debexpo.tools.debian.changes import Changes, ExceptionChanges
from debexpo.tools.debian.control import Control, ExceptionControl
from debexpo.tools.debian.dsc import Dsc, ExceptionDsc

DEB822_ASSERT_RAISES_ARGS = (
    [ExceptionChanges, Changes],
    [ExceptionDsc, Dsc, "main"],
    [ExceptionControl, Control],
)


class TestDeb822(TestController):
    # deb822 throw an exception on instantiation at least when it detects two
    # differents encodings both with decoding errors.
    #
    # This 5 bytes seed has been reduced from a tar archive uploaded as a
    # .changes which trigger the exception. It is invalid UTF-8 and it is
    # detected as TIS-620 by chardet, also invalid.
    def test_invalid_input(self):
        for args in DEB822_ASSERT_RAISES_ARGS:
            with NamedTemporaryFile() as file:
                file.write(b'\xdb\xca\xb5\x65\xd9')
                file.flush()
                args.insert(2, file.name)
                self.assertRaises(*args)
