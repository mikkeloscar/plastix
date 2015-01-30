import funcparserlib.parser as p
from functools import reduce

import sys

from elements import (
        Paragraph,
        Section,
        FootnoteRef,
        Reference,
        String,
        Bold,
        Italic,
        Underline,
        Escaped,
        Footnote,
        Color,
        Figure,
        List,
        ListItem,
        Table,
        TableCell,
        TableRow,
        Newline,
        InlineRef
)

# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.lexers import PythonLexer
# from pygments.formatters import LatexFormatter


# formatting functions

def format_section(s, level):
    return Section(s[1], level)

# format idented codeblock
def format_codeline(s):
    return ''.join(s)

def format_code(s):
    return CodeBlock('\n'.join(s))

def format_inlinecode(s):
    return Code(''.join(s))

def format_reference(s):
    ident, _, ref = s
    if not ref:
        ref = ""
    return Reference(ident, ref)

def format_str(s):
    return String(''.join(s))

def format_footnote(s):
    return Footnote()

def format_footref(s):
    _, inline = s
    return FootnoteRef(inline)

def format_bold(s):
    return Bold(s)

def format_escape(c):
    return Escaped(c)

def format_italic(s):
    return Italic(s)

def format_underline(s):
    return Underline(s)

def format_rgb(s):
    print(s)

def format_color(s):
    text, color = s
    return Color(text, color)

def format_figure(s):
    path, (_, label), caption = s
    if label == "":
        label = None
    return Figure(path, label, caption)

# ordered list
def format_sublistitem(s):
    indent, listType, item = s
    return ListItem(listType, item, len(indent))

def format_listitem(s):
    listTupe, item = s
    return ListItem(listTupe, item)

def format_list(l):
    first, rest = l
    fullList = [first] + rest
    return List(first.listType, fullList)

def format_table(s):
    _, rows = s
    return Table(rows)

def format_cell(s):
    if isinstance(s, tuple):
        content, _ = s
    else:
        content = s
    return TableCell(content)

def format_row(r):
    row, _ = r
    return TableRow(row)

def format_newline(s):
    print(s)
    return Newline(''.join(s))

def format_paragraph(s):
    paragraph, newline = s
    return Paragraph(paragraph, newline)

def format_inlinereference(s):
    return InlineRef(s)


# helper parsers
char = lambda c: p.skip(p.a(c))
literal = lambda s: reduce(lambda x,y: x+y, map(char, s))
var = lambda s: reduce(lambda x,y: x+y, map(lambda c: p.a(c), s))

# simple char-list -> string shortcut
join = (lambda s: ''.join(s))

# discard spaces
spaces = p.many(char(' '))

# check if char matches a valid ident char [a-z0-9_:-]
def isident(c):
    return c.isdigit() or ('a' <= c and c <= 'z') or c in (':', '_', '-')

def isnormaltext(c):
    return c not in ( '*'
                    , '/'
                    , '<'
                    , '>'
                    , ':'
                    , '^'
                    , '#'
                    , '|'
                    , '-'
                    , '_'
                    , '\\'
                    , '['
                    , ']'
                    )

def ishex(c):
    return c.isdigit() or ('a' <= c and c <= 'f')

def ispathchar(c):
    return c.isalpha() or c.isdigit() or isident(c) or c in ('/', '.')

def validescapechar(c):
    if not state:
        return False
    if state == "bold":
        return c in ('/', '<', '>', ':', '^', '\n')
    if state == "italic":
        return c in ('*', '<', '>', ':', '^', '\n')
    if state == "color":
        return c in ('*', '<', '^', '\n')

def notSpace(c):
    return c not in [' ', '\t']

ident = p.many(p.some(isident)) >> join

text = p.oneplus(p.some(lambda c: isnormaltext(c) and c != '\n')) >> format_str

# inlineCodeChar = p.many(p.some(lambda c: c not in ('`')))

# code = char('`') + inlineCodeChar + char('`') >> format_inlinecode

inline = p.forward_decl()

# bold
bold = char('*') + p.many(inline) + char('*') >> format_bold

# italic
italic = literal('//') + p.many(inline) + literal('//') >> format_italic

underline = char('_') + p.many(inline) + char('_') >> format_underline

# inline math
# TODO inline math
# inlineMath = char('$') + p.many(inline) + char('$')

# color
hexVal = p.some(ishex)
hexColor = p.a('#') + hexVal + hexVal + hexVal + hexVal + hexVal + hexVal >> join
# TODO better way to do this.
strColor = var('red') >> join \
         | var('blue') >> join
# TODO doesn't handle ints that well
byteInt = p.oneplus(p.some(lambda c: c.isdigit()))
rgbColor = char('(') + byteInt + char(',') + \
           byteInt + char(',') + byteInt + char(')') >> format_rgb
colorDef = hexColor | strColor | rgbColor
color = char('<') + p.many(inline) + char(':') + colorDef + char('>') \
        >> format_color

# reference
inlinereference = char('[') + ident + literal(']') >> format_inlinereference

# footnote
footnote = literal('^#') >> format_footnote

# rest = bold | color | italic | (p.some(lambda c: not isnormaltext(c)) >> (lambda s: print("rest:", s)))

escapechar = char('\\') \
           + p.some(lambda c: not isnormaltext(c)) \
           >> format_escape

inline.define(
        escapechar
      | footnote
      | color
      | bold
      | italic
      | inlinereference
      | underline
      | text)

# print(inline.parse("*bold*")) # "<color*a*:red>"))

newline = p.oneplus(p.a('\n')) >> format_newline

endline = char('\n') | p.finished

line = p.oneplus(inline) + endline

section = literal('=====') + spaces + line >> \
            (lambda s: format_section(s, 5)) \
          | literal('====') + spaces + line >> \
            (lambda s: format_section(s, 4)) \
          | literal('===') + spaces + line >> \
            (lambda s: format_section(s, 3)) \
          | literal('==') + spaces + line >> \
            (lambda s: format_section(s, 2)) \
          | literal('=') + spaces + line >> \
            (lambda s: format_section(s, 1)) \

# footnote reference
footnoteRef = literal('#:') + spaces + p.oneplus(inline) + endline >> format_footref

# figure
path = p.oneplus(p.some(ispathchar)) >> join # TODO handle paths
optLabel = p.maybe(spaces + ident)
optCaption = p.maybe(p.oneplus(line))
# figure = literal('![') + path + char(']') + optLabel + endline + optCaption
figure = char('!') + path + optLabel + endline + optCaption >> format_figure

paragraph = p.oneplus(line) + p.maybe(newline) >> format_paragraph

# # codeblock parsing
# # any non-newline char can be in a codeblock
# codeChar = p.many(p.some(lambda c: c != '\n'))
# # code line
# codeLine = literal('    ') + codeChar + endline >> format_codeline
# # codeblock
# codeBlock = p.oneplus(codeLine) >> format_code


# general sublists
listStart = p.some(lambda c: c in ['#', '*']) + char(' ')
listSubItem = p.oneplus(p.some(lambda c: c == " ")) + \
              listStart + p.oneplus(line) >> format_sublistitem

# ordered lists
orderedListItem = p.a('#') + char(' ') + p.oneplus(line) >> format_listitem
orderedInlistItem =  orderedListItem | listSubItem

orderedList = orderedListItem + p.many(orderedInlistItem) >> format_list

# unordered lists
unorderedListItem = p.a('*') + char(' ') + p.oneplus(line) >> format_listitem
unorderedInlistItem =  unorderedListItem | listSubItem

unorderedList = unorderedListItem + p.many(unorderedInlistItem) >> format_list

lists = orderedList | unorderedList


# tables
tableCell = p.oneplus(inline) + char('|') + p.maybe(endline) >> format_cell
tableHLine = p.oneplus(p.a('-')) + endline
tableRow = char('|') + p.oneplus(tableCell) + tableHLine >> format_row

table = tableHLine + p.oneplus(tableRow) >> format_table


reference = char('[') + ident + literal(']:') + spaces + p.oneplus(line) \
            >> format_reference

block = section \
      | footnoteRef \
      | reference \
      | figure \
      | lists \
      | table \
      | paragraph \
      | newline #| text#| codeBlock | paragraph

document = p.many(block) + p.skip(p.finished)

def load(path):
    plastix = ""
    with open(path, "r") as f:
        # hacky way to handle comments
        lines = f.readlines()
        outlines = []
        for line in lines:
            if line[0] != "%":
                outlines.append(line)
        plastix = ''.join(outlines)
    print(document.parse(plastix))

if __name__ == "__main__":
    load(sys.argv[1])
