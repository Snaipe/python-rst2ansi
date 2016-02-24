# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright © 2015-2016 Franklin "Snaipe" Mathieu <http://snai.pe/>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import unicode_literals

import sys

def num_to_superscript(n):
  sups = {
    '0': '\u2070',
    '1': '\xb9',
    '2': '\xb2',
    '3': '\xb3',
    '4': '\u2074',
    '5': '\u2075',
    '6': '\u2076',
    '7': '\u2077',
    '8': '\u2078',
    '9': '\u2079'
  }
  return ''.join(sups.get(c, c) for c in str(n))

def ref_to_unicode(n):
  return '⁽' + num_to_superscript(n) + '⁾'

def u(s):
  # Useful for very coarse version differentiation.
  PY2 = sys.version_info[0] == 2
  PY3 = sys.version_info[0] == 3
  if PY3:
    return s
  else:
    # Workaround for standalone backslash
    try:
        ret_s = unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
    except TypeError:
        ret_s = s.replace(r'\\', r'\\\\')
    return ret_s
