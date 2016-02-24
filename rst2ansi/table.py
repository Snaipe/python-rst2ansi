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

from docutils import nodes

from textwrap import wrap

from .unicode import u

class CellDimCalculator(nodes.NodeVisitor):

  def __init__(self, document, cols, rows, width):
    nodes.NodeVisitor.__init__(self, document)
    self.cols = cols
    self.rows = rows
    self.width = width
    self.height = 0

  def visit_paragraph(self, node):
    first_line = node.astext().split('\n')[0]

    # handle weird table sizing from simple rst tables
    # disregard cells spanning multiple columns, as
    # these don't contribute to the cell width calculation
    if len(first_line) >= self.width:
        self.width = len(first_line) + 2

    sublines = wrap(node.astext(), width = self.width)
    self.height = int(len(sublines) / self.rows)
    raise nodes.StopTraversal

  def visit_table(self, node):
    c = TableSizeCalculator(self.document)
    node.walkabout(c)
    self.height = int(c.height / self.rows)
    raise nodes.StopTraversal

  def visit_literal_block(self, node):
    self.height = int(len(node.astext().split('\n')) / self.rows)
    raise nodes.StopTraversal

  visit_Text = visit_literal_block

  def __getattr__(self, name):
    if name.startswith('visit_') or name.startswith('depart_'):
      def noop(*args, **kwargs):
        pass
      return noop
    raise AttributeError(name)


class TableSizeCalculator(nodes.NodeVisitor):

  def __init__(self, document):
    nodes.NodeVisitor.__init__(self, document)
    self.level = 0
    self.widths = []
    self.heights = []
    self.rows = 0

  def __getattr__(self, name):
    if name.startswith('visit_') or name.startswith('depart_'):
      def noop(*args, **kwargs):
        pass
      return noop
    raise AttributeError(name)

  def visit_table(self, node):
    if self.level > 0:
      raise SkipChildren
    self.level += 1

  def depart_table(self, node):
    self.width = sum(self.widths) + (len(self.widths) + 1)
    self.height = sum(self.heights) + (len(self.heights) + 1)
    self.level -= 1

  def visit_tgroup(self, node):
    self.cols = node.attributes['cols']

  def visit_colspec(self, node):
    self.widths.append(node.attributes['colwidth'])

  def visit_row(self, node):
    self.rows += 1
    self.heights.append(1)
    self.col = 0

  def visit_entry(self, node):
    cols = node.attributes.get('morecols', 0) + 1
    rows = node.attributes.get('morerows', 0) + 1
    width = sum(self.widths[self.col:self.col + cols]) + (cols - 1)

    c = CellDimCalculator(self.document, cols, rows, width)
    node.walkabout(c)

    # Correct invalid column sizing for simple rst tables
    if c.width > width and cols == 1:
        self.widths[self.col] = c.width

    self.heights[-1] = max(self.heights[-1], c.height)
    self.col += 1
    raise nodes.SkipChildren

class TableDrawer(nodes.NodeVisitor):

  def __init__(self, props, document, **options):
    nodes.NodeVisitor.__init__(self, document)
    self.props = props
    self.level = 0
    self.lines = ['']
    self.line = 0
    self.cursor = 0
    self.col = 0
    self.row = 0
    self.nb_rows = 0
    self.options = options

    def unicode_intersection(char, next):
      switch = {
          ('─', '│'): '┬',
          ('┐', '│'): '┐',
          ('┘', '│'): '┤',
          ('┘', '─'): '┴',
          ('┴', '│'): '┼',
          ('│', '─'): '├',
          ('┤', '─'): '┼',
          (' ', '─'): '┘',
          ('└', '─'): '└',

          ('═', '│'): '╤',
          ('╕', '│'): '╕',
          ('╛', '│'): '╡',
          ('╛', '═'): '╧',
          ('╧', '│'): '╪',
          ('│', '═'): '╞',
          ('╡', '═'): '╪',
          (' ', '═'): '╛',
          ('╘', '═'): '╘',
        }
      return switch[(u(char), u(next))]

    if options.get('unicode', False):
      self.char_single_rule = '─'
      self.char_double_rule = '═'
      self.char_vertical_rule = '│'
      self.get_intersection = unicode_intersection
      self.top_left = '┌'
      self.top_right = '┐'
      self.bottom_left = '╘'
    else:
      self.char_single_rule = '-'
      self.char_double_rule = '='
      self.char_vertical_rule = '|'
      self.get_intersection = lambda *args: '+'
      self.top_left = self.bottom_left = self.top_right = '+'

  def __getattr__(self, name):
    if name.startswith('visit_') or name.startswith('depart_'):
      def noop(*args, **kwargs):
        pass
      return noop
    if name == 'curline':
      return self.lines[self.line]
    raise AttributeError(name)

  def _draw_rule(self):
    self.lines[self.line] += self.top_left + self.char_single_rule * (self.props.width - 2) + self.top_right
    self.lines.extend([self.char_vertical_rule + ' ' * (self.props.width - 1)] * (self.props.height - 2))
    self.lines.extend([self.bottom_left + ' ' * (self.props.width - 1)])
    self.line += 1
    self.cursor = 0

  def visit_table(self, node):
    if self.level > 0:
      raise SkipChildren
    self.level += 1
    self._draw_rule()

  def depart_table(self, node):
    self.level -= 1

  def visit_row(self, node):
    self.col = 0
    self.cursor = 0

  def depart_row(self, node):
    self.line += self.props.heights[self.row] + 1
    self.row += 1
    self.local_row += 1

  def visit_thead(self, node):
    self.nb_rows = len(node.children)
    self.local_row = 0

  visit_tbody = visit_thead

  def visit_entry(self, node):
    cols = node.attributes.get('morecols', 0) + 1
    rows = node.attributes.get('morerows', 0) + 1

    width = sum(self.props.widths[self.col:self.col + cols]) + (cols - 1)
    height = sum(self.props.heights[self.row:self.row + rows]) + (rows - 1)

    rule = self.char_double_rule if self.local_row + rows - 1 == self.nb_rows - 1 else self.char_single_rule
    sep = self.char_vertical_rule

    # Draw the horizontal rule

    line = self.lines[self.line + height]
    int1 = self.get_intersection(line[self.cursor], rule)
    int2 = self.get_intersection(line[self.cursor + width + 1], rule)
    line = line[:self.cursor] + int1 + (width * rule) + int2 + line[self.cursor + width + 2:]
    self.lines[self.line + height] = line

    # Draw the vertical rule

    for i in range(height):
      line = self.lines[self.line + i]
      line = line[:self.cursor + width + 1] + sep + line[self.cursor + width + 2:]
      self.lines[self.line + i] = line

    line = self.lines[self.line - 1]
    int3 = self.get_intersection(line[self.cursor + width + 1], sep)
    line = line[:self.cursor + width + 1] + int3 + line[self.cursor + width + 2:]
    self.lines[self.line - 1] = line

    self.col += cols
    self.cursor += width + 1

    # Do not recurse
    raise nodes.SkipChildren

class TableWriter(nodes.NodeVisitor):

  def __init__(self, props, document, **options):
    nodes.NodeVisitor.__init__(self, document)
    self.props = props
    self.level = 0
    self.line = 0
    self.cursor = 0
    self.col = 0
    self.row = 0
    self.nb_rows = 0
    self.options = options

  def __getattr__(self, name):
    if name.startswith('visit_') or name.startswith('depart_'):
      def noop(*args, **kwargs):
        pass
      return noop
    raise AttributeError(name)

  def visit_table(self, node):
    drawer = TableDrawer(self.props, self.document, **self.options)
    node.walkabout(drawer)
    self.lines = drawer.lines

  def visit_row(self, node):
    self.col = 0
    self.cursor = 0

  def depart_row(self, node):
    self.line += self.props.heights[self.row] + 1
    self.row += 1
    self.local_row += 1

  def visit_thead(self, node):
    self.nb_rows = len(node.children)
    self.local_row = 0

  visit_tbody = visit_thead

  def visit_entry(self, node):
    cols = node.attributes.get('morecols', 0) + 1
    rows = node.attributes.get('morerows', 0) + 1

    width = sum(self.props.widths[self.col:self.col + cols]) + (cols - 1)
    height = sum(self.props.heights[self.row:self.row + rows]) + (rows - 1)

    from .ansi import ANSITranslator

    if node.children:
      v = ANSITranslator(self.document, termsize=(width - 2, height), **self.options)
      node.children[0].walkabout(v)
      v.strip_empty_lines()
      i = 1
      for l in v.lines:
        for sl in l.split('\n'):
          line = self.lines[self.line + i]
          line = line[:self.cursor + 2] + sl + line[self.cursor + 2 + len(sl):]
          self.lines[self.line + i] = line
          i += 1

    self.col += cols
    self.cursor += width + 1

    # Do not recurse
    raise nodes.SkipChildren
