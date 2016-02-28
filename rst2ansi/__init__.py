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

from docutils import nodes, core
from docutils.parsers.rst import roles

from .visitor import Writer
from .ansi import COLORS, STYLES

def rst2ansi(input_string, output_encoding='utf-8'):

  overrides = {}
  overrides['input_encoding'] = 'unicode'

  def style_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [nodes.TextElement(rawtext, text, classes=[name])], []

  for color in COLORS:
    roles.register_local_role('ansi-fg-' + color, style_role)
    roles.register_local_role('ansi-bg-' + color, style_role)
  for style in STYLES:
    roles.register_local_role('ansi-' + style, style_role)

  out = core.publish_string(input_string.decode('utf-8'), settings_overrides=overrides, writer=Writer(unicode=output_encoding.startswith('utf')))
  return out.decode(output_encoding)
