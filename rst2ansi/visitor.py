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

from docutils import core, frontend, nodes, utils, writers, languages, io
from docutils.utils.error_reporting import SafeString
from docutils.transforms import writer_aux
from docutils.parsers.rst import roles

from .ansi import ANSITranslator

class Writer(writers.Writer):

  def __init__(self, **options):
    writers.Writer.__init__(self)
    self.translator_class = ANSITranslator
    self.options = options

  def translate(self):
    visitor = self.translator_class(self.document, **self.options)
    self.document.walkabout(visitor)
    self.output = visitor.output

  def get_transforms(self):
    return writers.Writer.get_transforms(self) + [writer_aux.Admonitions]

