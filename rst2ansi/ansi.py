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

from copy import deepcopy
from os import get_terminal_size

from docutils import nodes

from .functional import npartial
from .table import TableSizeCalculator, TableWriter
from .unicode import ref_to_unicode
from .wrap import wrap

COLORS = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
STYLES = (
    "bold",
    "dim",
    "italic",
    "underline",
    "blink",
    "blink-fast",
    "inverse",
    "conceal",
    "strikethrough",
)


class ANSICodes:
    """Work with ANSI codes."""

    @staticmethod
    def get_color_code(code, fg):
        """Return the ANSI code for a color.

        Parameters
        ----------
        code : str, int, tuple, or list
            The color code. If a string, it must be one of the following:
            ``black``, ``red``, ``green``, ``yellow``, ``blue``, ``magenta``,
            ``cyan``, ``white``. If an integer, it must be between 0 and 255.
            If a tuple or list, it must be a 3-tuple of integers between 0 and
            255.
        fg : bool
            Whether to return a foreground or background color code.
        """
        fgc_256 = 38
        bgc_256 = 48

        if code in COLORS:
            fgc = 30
            bgc = 40
            shift = fgc if fg else bgc
            return str(shift + COLORS.index(code))

        if isinstance(code, int) and 0 <= code <= 255:
            shift = fgc_256 if fg else bgc_256
            return f"{shift};5;{code}"

        if isinstance(code, (tuple, list)) and len(code) == 3:
            for c in code:
                if not 0 <= c <= 255:
                    raise ValueError(f'Invalid color "{code}"')

            r, g, b = code
            shift = fgc_256 if fg else bgc_256
            return f"{shift};2;{r};{g};{b}"

        raise ValueError(f'Invalid color "{code}"')

    @staticmethod
    def get_style_code(code):
        """Return the ANSI code for a style.

        Parameters
        ----------
        code : str
            The style code. It must be one of the following:
            ``bold``, ``dim``, ``italic``, ``underline``, ``blink``,
            ``blink-fast``, ``inverse``, ``conceal``, ``strikethrough``.
        """
        if code in STYLES:
            return str(1 + STYLES.index(code))
        raise ValueError(f'Invalid style "{code}"')

    @staticmethod
    def to_ansi(codes):
        """Return the ANSI escape sequence for a list of codes.

        Parameters
        ----------
        codes : list
            A list of ANSI codes.
        """
        codes = ";".join(codes)
        return f"\x1b[{codes}m"

    NONE = "0"
    RESET = to_ansi.__func__(NONE)


class ANSITranslator(nodes.NodeVisitor):
    class Context:
        def __init__(self):
            self.output = ""
            self.indent_level = 0
            self.in_list = False
            self.has_title = False
            self.list_counter = 0
            self.node_type = ""

    class StyleContext:
        def __init__(self):
            self.styles = set()
            self.fg = ANSICodes.NONE
            self.bg = ANSICodes.NONE

    def __init__(self, document, termsize=None, **options):
        nodes.NodeVisitor.__init__(self, document)
        self.document = document
        self.output = ""
        self.lines = [""]
        self.line = 0
        self.indent_width = 2
        try:
            self.termsize = termsize or get_terminal_size()
        except OSError:
            self.termsize = (80, 24)
        self.options = options
        self.references = []
        self.refcount = 0

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

    def push_style(self, fg=None, bg=None, styles=None):
        if styles is None:
            styles = []
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
        reset = (
            self.style.fg == ANSICodes.NONE
            and self.style.bg == ANSICodes.NONE
            and not self.style.styles
        )
        self._restyle(reset)

    def append(self, *args, **kwargs):
        try:
            strict = kwargs["strict"]
        except KeyError:
            strict = False
        if len(self.lines[self.line]) == 0 and not strict:
            self.lines[self.line] += " " * self.ctx.indent_level * self.indent_width

        for a in args:
            self.lines[self.line] += a

    def newline(self, n=1):
        self.lines.extend([""] * n)
        self.line += n

    def prevline(self, n=1):
        self.line -= n

    def nextline(self, n=1):
        self.line += n

    def popline(self):
        line = self.lines.pop(self.line)
        self.line -= 1
        return line

    def replaceline(self, newline, strict=True):
        if strict:
            self.lines[self.line] = newline
        else:
            self.lines[self.line] = ""
            self.append(newline)

    def addlines(self, lines, strict=False):
        if strict:
            self.lines.extend(lines)
            self.line += len(lines)
            self.newline()
        else:
            for line in lines:
                self.append(line)
                self.newline()

    def _restyle(self, reset=False):
        if reset:
            self.append(ANSICodes.RESET)

        styles = list(self.style.styles)
        if self.style.fg != ANSICodes.NONE:
            styles.append(self.style.fg)
        if self.style.bg != ANSICodes.NONE:
            styles.append(self.style.bg)

        if styles:
            self.append(ANSICodes.to_ansi(styles))

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

    def _print_references(self):
        if not self.references:
            return

        self.push_style(styles=["bold"])
        self.append("References:")
        self.pop_style()
        self.newline(2)

        self.push_ctx(indent_level=self.ctx.indent_level + 1)
        for ref in self.references:
            self._print_references_inner(ref)
        self.references = []
        self.pop_ctx()

    def _print_references_inner(self, ref):
        self.append(f"[{ref[0]}]: <")
        self.push_style(fg="cyan", styles=["underline"])
        self.append(ref[1])
        self.pop_style()
        self.append(">")
        self.newline()

    def depart_document(self, node):
        self._print_references()
        self.depart_section(node)

        self.pop_ctx()
        self.strip_empty_lines()

        self.output = "\n".join(self.lines)

    def wrap_current_line(self):
        indent = self.ctx.indent_level * self.indent_width
        sublines = wrap(
            self.curline,
            width=self.termsize[0] - indent,
            subsequent_indent=" " * indent,
        )
        self.popline()
        self.addlines(sublines, strict=True)

    def depart_paragraph(self, node):
        if self.options.get("wrap_paragraphs", True):
            self.wrap_current_line()
        if not self.ctx.in_list:
            self.newline()

    def visit_title(self, node):
        self.push_style(styles=["bold"])

    def depart_title(self, node):
        self.pop_style()
        self.push_ctx(has_title=True, indent_level=self.ctx.indent_level + 1)
        self.newline(2)

    def visit_subtitle(self, node):
        self.prevline(2)
        self.append(" - ")

    def depart_subtitle(self, node):
        self.nextline(2)

    def visit_Text(self, node):
        self.append(node.astext())

    def depart_section(self, node):
        if self.ctx.has_title:
            self.pop_ctx()

    def depart_transition(self, node):
        indent = (self.ctx.indent_level + 2) * self.indent_width
        char = "╌" if self.options["unicode"] else "-"
        self.append(
            " " * indent + char * (self.termsize[0] - 2 * indent) + " " * indent,
            strict=True,
        )
        self.newline(2)

    def _get_uri(self, node):
        return node.attributes.get("refuri", "") or node.attributes.get("uri", "")

    def visit_reference(self, node):
        if self._get_uri(node) == node.astext().strip():
            self.append("<")
        self.push_style(fg="cyan", styles=["underline"])

    def depart_reference(self, node):
        self.pop_style()
        if self._get_uri(node) == node.astext().strip():
            self.append(">")
        else:
            self.references.append((self.refcount, self._get_uri(node)))
            if self.options["unicode"] and self.options.get(
                "unicode_superscript", False
            ):
                self.append(ref_to_unicode(self.refcount))
            else:
                self.append(f" [{self.refcount}]")
            self.refcount += 1

    # Style nodes

    visit_strong = npartial(push_style, styles=["bold"])
    depart_strong = npartial(pop_style)

    visit_emphasis = npartial(push_style, styles=["italic"])
    depart_emphasis = npartial(pop_style)

    def visit_TextElement(self, node):
        ansi_props = [
            x[5:] for x in node.attributes["classes"] if x.startswith("ansi-")
        ]
        style = {
            "fg": next(
                (x[3:] for x in ansi_props if x.startswith("fg-") and x[3:] in COLORS),
                None,
            ),
            "bg": next(
                (x[3:] for x in ansi_props if x.startswith("bg-") and x[3:] in COLORS),
                None,
            ),
            "styles": (x for x in ansi_props if x in STYLES),
        }
        self.push_style(**style)

    def depart_TextElement(self, node):
        self.pop_style()

    visit_inline = visit_TextElement
    depart_inline = depart_TextElement

    # Lists

    def visit_enumerated_list(self, node):
        strt = node.attributes.get("start", 1)
        self.push_ctx(in_list=True, list_counter=strt)

    def depart_enumerated_list(self, node):
        self.pop_ctx()
        if not self.ctx.in_list:
            self.newline()

    def visit_bullet_list(self, node):
        self.push_ctx(in_list=True, list_counter=0)

    def depart_bullet_list(self, node):
        self.pop_ctx()
        if not self.ctx.in_list:
            self.newline()

    def visit_list_item(self, node):
        if self.ctx.list_counter:
            self.append(f"{str(self.ctx.list_counter)}. ")
            self.ctx.list_counter += 1
        else:
            self.append("• " if self.options["unicode"] else "* ")
        self.push_ctx(indent_level=self.ctx.indent_level + 1)

    def depart_list_item(self, node):
        self.pop_ctx()

    visit_definition_list = npartial(push_ctx, in_list=True, list_counter=0)
    depart_definition_list = npartial(pop_ctx)

    def visit_definition(self, node):
        self.newline()
        self.push_ctx(indent_level=self.ctx.indent_level + 1)

    def depart_definition(self, node):
        self.newline()
        self.pop_ctx()

    visit_option_list = npartial(push_ctx, in_list=True, list_counter=0)
    depart_option_list = npartial(pop_ctx)

    def depart_option(self, node):
        self.append(" | ")

    def depart_option_group(self, node):
        self.replaceline(self.lines[self.line][:-3], strict=True)
        self.push_ctx(indent_level=self.ctx.indent_level + 2)
        self.newline()

    def visit_option_argument(self, node):
        self.append(" ")

    def depart_option_list_item(self, node):
        self.pop_ctx()

    # Tables

    def visit_table(self, node):
        props = TableSizeCalculator(self.document)
        node.walkabout(props)

        writer = TableWriter(props, self.document, **self.options)
        node.walkabout(writer)
        self.addlines(writer.lines)

        # Do not recurse
        raise nodes.SkipChildren

    def depart_table(self, node):
        self.newline()

    # Misc

    def depart_image(self, node):
        if type(node.parent) == nodes.figure:
            self.visit_reference(node)
            self.append(f"[{node.attributes.get('alt', 'Image')}]")
            self.depart_reference(node)
            self.newline()
        else:
            self.append(f"[{node.attributes.get('alt', 'Image')}]")

    def depart_caption(self, node):
        self.newline(2)

    def visit_substitution_definition(self, node):
        raise nodes.SkipChildren

    def visit_comment(self, node):
        raise nodes.SkipChildren

    def depart_admonition(self, node):
        if self.ctx.has_title:
            self.pop_ctx()

    def visit_block_quote(self, node):
        self.push_ctx(indent_level=self.ctx.indent_level + 1)

    def depart_block_quote(self, node):
        self.pop_ctx()

    def depart_literal_block(self, node):
        sublines = self.curline.split("\n")
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
        indent = self.ctx.indent_level + (
            1 if self.ctx.node_type == "line_block" else 0
        )
        self.push_ctx(indent_level=indent, node_type="line_block")

    def depart_line_block(self, node):
        self.pop_ctx()
        if self.ctx.node_type != "line_block":
            self.newline()

    def __getattr__(self, name):
        if name.startswith("visit_") or name.startswith("depart_"):

            def noop(*args, **kwargs):
                pass

            return noop
        if name == "curline":
            return self.lines[self.line]
        raise AttributeError(name)
