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

__docformat__ = 'reStructuredText'

import sys
import docutils

from copy import deepcopy, copy
from textwrap import wrap

from docutils import core, frontend, nodes, utils, writers, languages, io
from docutils.utils.error_reporting import SafeString
from docutils.transforms import writer_aux
from docutils.parsers.rst import roles

from functools import update_wrapper
from functools import partial
from types import MethodType

import shutil

COLORS = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
STYLES = ('bold', 'dim', 'italic', 'underline', 'blink', 'blink-fast', 'inverse', 'strikethrough', 'crossed')

class ANSICodes(object):

  @staticmethod
  def get_color_code(code, fg):
    FG = 30
    BG = 40
    FG_256 = 38
    BG_256 = 48

    if code in COLORS:
      shift = FG if fg else BG
      return str(shift + COLORS.index(code))
    elif isinstance(code, int) and 0 <= code <= 255:
      shift = FG_256 if fg else BG_256
      return str(shift) + ';5;%d' % int(code)
    elif not isinstance(code, str) and hasattr(code, "__len__") and len(code) == 3:
      for c in code:
        if not 0 <= c <= 255:
          raise Exception('Invalid color "%s"' % code)

      r, g, b = code
      shift = FG_256 if fg else BG_256
      return str(shift) + ';2;%d;%d;%d' % (int(r), int(g), int(b))

    raise Exception('Invalid color "%s"' % code)

  @staticmethod
  def get_style_code(code):
    if code in STYLES:
      return str(1 + STYLES.index(code))
    raise Exception('Invalid style "%s"' % code)

  @staticmethod
  def codes_for(fg=None, bg=None, styles=None):
    out = []

    if fg:
      out.append(ANSICodes.get_color_code(fg, True))

    if bg:
      out.append(ANSICodes.get_color_code(bg, False))

    if styles:
      out += [ANSICodes.get_style_code(s) for s in styles]

    return out

  @staticmethod
  def to_ansi(codes):
    return '\x1b[' + ';'.join(codes) + 'm'

  NONE = '0'
  RESET = to_ansi.__func__(NONE)

  BOLD = get_style_code.__func__('bold')
  ITALIC = get_style_code.__func__('italic')

class Writer(writers.Writer):

  def __init__(self):
    writers.Writer.__init__(self)
    self.translator_class = ANSITranslator

  def translate(self):
    visitor = self.translator_class(self.document)
    self.document.walkabout(visitor)
    self.output = visitor.output

  def get_transforms(self):
    return writers.Writer.get_transforms(self) + [writer_aux.Admonitions]


class ANSITranslator(nodes.NodeVisitor):

  class Context(object):

    def __init__(self):
      self.output = ''
      self.indent_level = 0
      self.in_list = False
      self.has_title = False
      self.list_counter = 0
      self.node_type = ''

  class StyleContext(object):

    def __init__(self):
      self.styles = set()
      self.fg = ANSICodes.NONE
      self.bg = ANSICodes.NONE

  def __init__(self, document):
    nodes.NodeVisitor.__init__(self, document)
    self.output = ''
    self.lines = ['']
    self.line = 0
    self.indent_width = 2
    self.termsize = shutil.get_terminal_size((80, 20))

    self.ctx = self.Context()
    self.ctx_stack = []
    self.style = self.StyleContext()
    self.style_stack = []

  def push_ctx(self, **kwargs):
    self.ctx_stack.append(self.ctx)
    self.ctx = deepcopy(self.ctx)
    for k, v in kwargs.items():
      setattr(self.ctx, k, v)

  def pop_ctx(self):
    self.ctx = self.ctx_stack.pop()

  def push_style(self, fg=None, bg=None, styles=[]):
    self.style_stack.append(self.style)
    self.style = deepcopy(self.style)
    if fg:
      self.style.fg = ANSICodes.get_color_code(fg, True)
    if bg:
      self.style.bg = ANSICodes.get_color_code(bg, False)
    self.style.styles |= {ANSICodes.get_style_code(s) for s in styles}

    self._restyle()

  def pop_style(self):
    self.style = self.style_stack.pop()
    reset = self.style.fg == ANSICodes.NONE and \
            self.style.bg == ANSICodes.NONE and \
            not self.style.styles
    self._restyle(reset)

  def append(self, *args):
    if len(self.lines[self.line]) == 0:
      self.lines[self.line] += ' ' * self.ctx.indent_level * self.indent_width

    for a in args:
      self.lines[self.line] += str(a)

  def newline(self, n=1):
    self.lines.extend([''] * n)
    self.line += n

  def prevline(self, n=1):
    self.line -= n

  def nextline(self, n=1):
    self.line += n

  def popline(self):
    l = self.lines.pop(self.line)
    self.line -= 1
    return l

  def replaceline(self, newline, strict=True):
    if strict:
      self.lines[self.line] = newline
    else:
      self.lines[self.line] = ''
      self.append(newline)

  def addlines(self, lines, strict=False):
    if strict:
      self.lines.extend(lines)
      self.line += len(lines)
      self.newline()
    else:
      for l in lines:
        self.append(l)
        self.newline()

  def _restyle(self, reset=False):
    if reset:
      self.append(ANSICodes.RESET)

    styles = list(self.style.styles)
    if self.style.fg != '0':
      styles.append(self.style.fg)
    if self.style.bg != '0':
      styles.append(self.style.bg)

    if styles:
      self.append(ANSICodes.to_ansi(styles))

  @staticmethod
  def _wrapper(func, *args, **kwargs):
    def wrapped(self, node):
      func(self, *args, **kwargs)
    return wrapped

  def strip_empty_lines(self):
    remove_last_n = 0
    for x in self.lines[::-1]:
      if len(x.strip()) != 0:
        break
      remove_last_n += 1
    if remove_last_n != 0:
      self.lines = self.lines[:-remove_last_n]

  # Structural nodes

  def visit_document(self, node):
    self.push_ctx()

  def depart_document(self, node):
    self.pop_ctx()
    if self.ctx.has_title:
      self.pop_ctx()
    self.strip_empty_lines()

    self.output = '\n'.join(self.lines)

  def wrap_current_line(self):
    indent = self.ctx.indent_level * self.indent_width
    sublines = wrap(self.curline, width = self.termsize.columns - indent,
        subsequent_indent = ' ' * indent)
    self.popline()
    self.addlines(sublines, strict=True)

  def visit_paragraph(self, node):
    pass

  def depart_paragraph(self, node):
    self.wrap_current_line()
    if not self.ctx.in_list:
      self.newline()

  def visit_title(self, node):
    self.push_style(styles=['bold'])

  def depart_title(self, node):
    self.pop_style()
    self.push_ctx(has_title = True, indent_level = self.ctx.indent_level + 1)
    self.newline(2)

  def visit_subtitle(self, node):
    self.prevline(2)
    self.append(' - ')

  def depart_subtitle(self, node):
    self.nextline(2)

  def visit_Text(self, node):
    self.append(node.astext())

  def depart_Text(self, node):
    pass

  def visit_section(self, node):
    pass

  def depart_section(self, node):
    if self.ctx.has_title:
      self.pop_ctx()

  # Style nodes

  def visit_inline(self, node):
    pass

  def depart_inline(self, node):
    pass

  visit_strong = _wrapper.__func__(push_style, styles=['bold'])
  depart_strong = _wrapper.__func__(pop_style)

  visit_emphasis = _wrapper.__func__(push_style, styles=['italic'])
  depart_emphasis = _wrapper.__func__(pop_style)

  def visit_TextElement(self, node):
    ansi_props = [x[5:] for x in node.attributes['classes'] if x.startswith('ansi-')]
    style = {
      'fg': next((x[3:] for x in ansi_props if x.startswith('fg-') and x[3:] in COLORS), None),
      'bg': next((x[3:] for x in ansi_props if x.startswith('bg-') and x[3:] in COLORS), None),
      'styles': (x for x in ansi_props if x in STYLES)
    }
    self.push_style(**style)

  def depart_TextElement(self, node):
    self.pop_style()

  # Lists

  def visit_enumerated_list(self, node):
    self.push_ctx(in_list = True, list_counter = 1)

  def depart_enumerated_list(self, node):
    self.pop_ctx()
    if not self.ctx.in_list:
      self.newline()

  def visit_bullet_list(self, node):
    self.push_ctx(in_list = True, list_counter = 0)

  def depart_bullet_list(self, node):
    self.pop_ctx()
    if not self.ctx.in_list:
      self.newline()

  def visit_list_item(self, node):
    if self.ctx.list_counter:
      self.append(str(self.ctx.list_counter) + '. ')
      self.ctx.list_counter += 1
    else:
      self.append('* ')
    self.push_ctx(indent_level = self.ctx.indent_level + 1)

  def depart_list_item(self, node):
    self.pop_ctx()

  # Misc

  def visit_block_quote(self, node):
    self.push_ctx(indent_level = self.ctx.indent_level + 1)

  def depart_block_quote(self, node):
    self.pop_ctx()

  def visit_raw(self, node):
    pass

  def depart_raw(self, node):
    pass

  def visit_literal_block(self, node):
    pass

  def depart_literal_block(self, node):
    sublines = self.curline.split('\n')
    self.replaceline(sublines[0])
    self.newline()
    self.addlines(sublines[1:])
    self.newline()

  def depart_line(self, node):
    if len(self.curline.strip()) == 0:
      self.newline()
    else:
      self.wrap_current_line()

  def visit_line_block(self, node):
    indent = self.ctx.indent_level + (1 if self.ctx.node_type == 'line_block' else 0)
    self.push_ctx(indent_level = indent, node_type = 'line_block')

  def depart_line_block(self, node):
    self.pop_ctx()
    if self.ctx.node_type != 'line_block':
      self.newline()

  def __getattr__(self, name):
    if name.startswith('visit_') or name.startswith('depart_'):
      def noop(*args, **kwargs):
        pass
      return noop
    if name == 'curline':
      return self.lines[self.line]
    raise AttributeError(name)

def rst2ansi(input_string):

  overrides = {}
  overrides['input_encoding'] = 'unicode'

  def style_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [nodes.TextElement(rawtext, text, classes=[name])], []

  for color in COLORS:
    roles.register_local_role('ansi-fg-' + color, style_role)
    roles.register_local_role('ansi-bg-' + color, style_role)
  for style in STYLES:
    roles.register_local_role('ansi-' + style, style_role)

  return docutils.core.publish_string(input_string, settings_overrides=overrides, writer=Writer())
