import funcparserlib.parser as p
from functools import reduce

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.lexers import PythonLexer
from pygments.formatters import LatexFormatter

# blocks
class Paragraph:
    def __init__(self, text):
        self.text = text

class Header:

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
        return Header.LATEX[self.level] % text + "\n"

    def __repr__(self):
        return "Header: \"%s\" (%s)" % (self.text, self.level)

class Blockquote:
    def __init__(self, text):
        self.text = text

class CodeBlock:

    def __init__(self, code):
        self.code = code

    def latex(self):
        formatter = LatexFormatter()
        print(formatter.get_style_defs())
        return highlight(self.code, get_lexer_by_name('python'), formatter=formatter)

    def __repr__(self):
        cut = min(len(self.code)-1, 7)
        return "CodeBlock: \"%s..\"" % self.code[:cut]

class Reference:
    def __init__(self, ident, url, title=""):
        self.ident = ident
        self.url = url
        self.title = title

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

def format_atxheader(s, level):
    return Header(s[1], level)

# format idented codeblock
def format_codeline(s):
    return ''.join(s)

def format_code(s):
    return CodeBlock('\n'.join(s))

def format_inlinecode(s):
    return Code(''.join(s))

def format_reference(s):
    ident, _, url, title = s
    if not title:
        title = ""
    return Reference(ident, url, title)

def format_str(s):
    return String(''.join(s))


# helper parsers
char = lambda c: p.skip(p.a(c))
literal = lambda s: reduce(lambda x,y: x+y, map(char, s))


isNormalText = lambda c: (c not in ['*', '_', '`', '\n'])

text = p.oneplus(p.some(isNormalText)) >> format_str

inlineCodeChar = p.many(p.some(lambda c: c not in ('`')))

code = char('`') + inlineCodeChar + char('`') >> format_inlinecode

inline = code | text

newline = p.oneplus(p.a('\n')) >> (lambda s: ''.join(s))

endline = char('\n')

line = p.oneplus(inline) + endline

spaces = p.many(char(' '))

# atx header parsing
# atxheader = (p.oneplus(p.a('#')) >> (lambda s:''.join(s))) + \
#             line >> format_atxheader

atxheader = literal('#####') + spaces + line >> \
            (lambda s: format_atxheader(s, 5)) \
          | literal('####') + spaces + line >> \
            (lambda s: format_atxheader(s, 4)) \
          | literal('###') + spaces + line >> \
            (lambda s: format_atxheader(s, 3)) \
          | literal('##') + spaces + line >> \
            (lambda s: format_atxheader(s, 2)) \
          | literal('#') + spaces + line >> \
            (lambda s: format_atxheader(s, 1)) \

# paragraph = p.oneplus(line) + newline

# codeblock parsing
# any non-newline char can be in a codeblock
codeChar = p.many(p.some(lambda c: c != '\n'))
# code line
codeLine = literal('    ') + codeChar + endline >> format_codeline
# codeblock
codeBlock = p.oneplus(codeLine) >> format_code

plain = p.many(p.some(lambda c: c.isdigit() or c.isalpha() or c == '_'))
ident = p.many(p.some(lambda c: c.isdigit() or c.isalpha() or c in (':', '_'))) \
        >> (lambda s: ''.join(s))

# not working yet!
# references
titleWrapStart = p.some(lambda c: c in ('\"', '\'', '('))
titleWrapEnd = p.some(lambda c: c in ('\"', '\'', ')'))

optionalTitle = spaces + p.maybe(titleWrapStart + plain + titleWrapEnd)

url = p.a('1')

# TODO handle maybe endline better
reference = char('[') + ident + literal(']:') + spaces + url + \
            optionalTitle + p.maybe(endline) \
            >> format_reference

block = atxheader | codeBlock | reference | newline#| text#| codeBlock | paragraph

document = p.many(block) + p.skip(p.finished)

# print(document.parse("##### heade`sad`r\n## header2\n\n    def parse():\n\n        return None\n\n"))
doc = document.parse("    def parse():\n        return None\n\n")
# doc = document.parse("# Header med `kode` og tekst\n")

for d in doc:
    print(d.latex())


