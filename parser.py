import funcparserlib.parser as p
from functools import reduce

import sys

# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.lexers import PythonLexer
# from pygments.formatters import LatexFormatter

# blocks
class Paragraph:
    def __init__(self, text):
        self.text = text

class Section:

    LATEX = { 1: "\\section{%s}"
            , 2: "\\subsection{%s}"
            , 3: "\\subsubsection{%s}"
            , 4: "\\paragraph{%s}"
            , 5: "\\subparagraph{%s}"
            }

    def __init__(self, text, level=1):
        self.level = level
        self.text = text

    def latex(self):
        text = [x.latex() for x in self.text]
        text = ''.join(text)
        return Section.LATEX[self.level] % text + "\n"

    def __repr__(self):
        return "Section: \"%s\" (%s)" % (self.text, self.level)

class FootnoteRef:

    def __init__(self, inline):
        self.inline = inline

    def __repr__(self):
        text = [x.latex() for x in self.inline]
        text = ''.join(text)
        return "Footnote: %s" %  text

# class Blockquote:
#     def __init__(self, text):
#         self.text = text

# class CodeBlock:

#     def __init__(self, code):
#         self.code = code

#     def latex(self):
#         formatter = LatexFormatter()
#         print(formatter.get_style_defs())
#         return highlight(self.code, get_lexer_by_name('python'), formatter=formatter)

#     def __repr__(self):
#         cut = min(len(self.code)-1, 7)
#         return "CodeBlock: \"%s..\"" % self.code[:cut]

class Reference:
    def __init__(self, ident, reference=""):
        self.ident = ident
        self.reference = reference

    def __repr__(self):
        return "Reference %s" % self.ident

# inlines
class Code:

    LATEX = "\\texttt{%s}"

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        cut = min(len(self.code)-1, 7)
        return "Code: \"%s..\"" % self.code[:cut]

    def latex(self):
        escapes = ["_", "#"]
        # TODO optional pygments
        code = self.escape(self.code, escapes)
        return (Code.LATEX % code)

    def escape(self, s, escapes):
        for e in escapes:
            s = s.replace(e, "\\" + e)
        return s

class String:
    def __init__(self, string):
        self.string = string

    def latex(self):
        # TODO escape stuff
        return self.string

    def __repr__(self):
        return self.string

class Bold:

    LATEX = "\\textbf{%s}"

    def __init__(self, text):
        self.text = text

    def latex(self):
        text = [x.latex() for x in self.text]
        text = ''.join(text)
        return Bold.LATEX % text

    def __repr__(self):
        text = [x.__repr__() for x in self.text]
        text = ''.join(text)
        return "b:%s:b" % text

class Italic:

    LATEX = "\\textit{%s}"

    def __init__(self, text):
        self.text = text

    def latex(self):
        text = [x.latex() for x in self.text]
        text = ''.join(text)
        return Italic.LATEX % text

    def __repr__(self):
        text = [x.__repr__() for x in self.text]
        text = ''.join(text)
        return "i:%s:i" % text

class Footnote:

    def __repr__(self):
        return "^#"

class Color:

    def __init__(self, text, color):
        self.text = text
        self.color = color

    def __repr__(self):
        return "%s:%s" % (self.text, self.color)

class Figure:
    def __init__(self, path, label=None, caption=None):
        self.path = path
        self.label = label
        self.caption = caption

    def __repr__(self):
        return "img[%s]" % self.path

class List:
    def __init__(self, listType, items):
        self.listType = listType
        self.items = items

class ListItem:
    def __init__(self, listType, item, indentation=0):
        self.listType = listType
        self.item = item
        self.indentation = indentation

    def __repr__(self):
        return "%s - %s:%d" % (self.listType, self.item, self.indentation)





# format atxheader string
# def format_atxheader(s):
#     title = ""
#     levels, chars = s
#     level = len(levels)
#     if level > 5:
#         level = 5
#         title = levels[5:] + ''.join(chars)
#     else:
#         pos = 0
#         while chars[pos] == ' ':
#             pos += 1
#         print(chars)
#         title = ''.join(chars[pos:])
#     return Header(title, level)

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
    print(s)
    ident, _, ref = s
    if not ref:
        ref = ""
    return Reference(ident, ref)

def format_str(s):
    print("str text", s)
    return String(''.join(s))

def format_footnote(s):
    return Footnote()

def format_footref(s):
    _, inline = s
    return FootnoteRef(inline)

def format_bold(s):
    print("bold!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    return Bold(s)

def format_italic(s):
    print("italic")
    return Italic(s)

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
    print(s)
    indent, listType, item = s
    return ListItem(listType, item, len(indent))

def format_listitem(s):
    listTupe, item = s
    return ListItem(listTupe, item)

def format_list(l):
    first, rest = l
    fullList = [first] + rest
    return List(first.listType, fullList)


# global document state
state = None


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
    return c not in ('*', '/', '<', '>', ':', '^', '#', '\n')

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

text = p.oneplus(p.some(isnormaltext)) >> format_str

# inlineCodeChar = p.many(p.some(lambda c: c not in ('`')))

# code = char('`') + inlineCodeChar + char('`') >> format_inlinecode

inline = p.forward_decl()

# bold
bold = char('*') + p.many(inline) + char('*') >> format_bold

# italic
italic = literal('//') + p.many(inline) + literal('//') >> format_italic

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
color = char('<') + p.many(inline) + char(':') + colorDef + char('>') >> format_color

# footnote
footnote = literal('^#') >> format_footnote

# rest = bold | color | italic | (p.some(lambda c: not isnormaltext(c)) >> (lambda s: print("rest:", s)))

# escapechar = char('\\') + p.some(not isnormaltext)

inline.define(
        footnote
      | color
      | bold
      | italic
      | text)

# print(inline.parse("*bold*")) # "<color*a*:red>"))

newline = p.oneplus(p.a('\n')) >> join

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

paragraph = p.oneplus(line) + p.maybe(newline | p.finished)

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


reference = char('[') + ident + literal(']:') + spaces + p.oneplus(line) \
            >> format_reference

block = section \
      | footnoteRef \
      | reference \
      | figure \
      | lists \
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
