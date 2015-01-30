
def combine_inlines(inline, references):
    preamble = []
    document = []
    for x in inline:
        l = x.latex(references)
        preamble += l["preamble"]
        document += l["document"]
    document = ''.join(document)
    return (preamble, document)


# blocks
class Paragraph:
    def __init__(self, text, newlines):
        self.text = text
        self.newlines = newlines

    def latex(self, references):
        preamble = []
        doc = ""
        for text in self.text:
            p, d = combine_inlines(text, references)
            preamble += p
            if len(doc) > 0:
                doc += " "
            doc += d

        if self.newlines:
            self.newlines = self.newlines.latex(references)
            preamble += self.newlines["preamble"]
            doc += self.newlines["document"][0]

        return { "preamble": preamble, "document": [doc + "\n"] }


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

    def latex(self, references):
        preamble, doc = combine_inlines(self.text, references)
        out = {
                "preamble": preamble,
                "document": [Section.LATEX[self.level] % doc + "\n"]
                }
        return out

    def __repr__(self):
        return "Section: \"%s\" (%s)" % (self.text, self.level)

class FootnoteRef:

    def __init__(self, inline):
        self.inline = inline

    def reference(self, references):
        _, doc = combine_inlines(self.inline, references)
        return doc

    def latex(self, references):
        return { "preamble": [], "document": [] }


    def __repr__(self):
        # text = [x.latex() for x in self.inline]
        # text = ''.join(text)
        return "Footnote:"

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
        self.ref = reference

    def reference(self, references):
        preamble = []
        doc = ""
        for text in self.ref:
            p, d = combine_inlines(text, references)
            preamble += p
            if len(doc) > 0:
                doc += " "
            doc += d
        return (self.ident, doc)

    def latex(self, references):
        return { "preamble": [], "document": [] }

    def __repr__(self):
        return "Reference %s" % self.ident

# inlines
# class Code:

#     LATEX = "\\texttt{%s}"

#     def __init__(self, code):
#         self.code = code

#     def __repr__(self):
#         cut = min(len(self.code)-1, 7)
#         return "Code: \"%s..\"" % self.code[:cut]

#     def latex(self):
#         escapes = ["_", "#"]
#         # TODO optional pygments
#         code = self.escape(self.code, escapes)
#         return (Code.LATEX % code)

#     def escape(self, s, escapes):
#         for e in escapes:
#             s = s.replace(e, "\\" + e)
#         return s

class String:
    def __init__(self, string):
        self.string = string

    def latex(self, references):
        # TODO escape stuff
        out = {
                "preamble": [],
                "document": [self.string]
                }
        return out

    def __repr__(self):
        return self.string

class Newline:
    def __init__(self, lines):
        self.lines = lines

    def latex(self, references):
        return { "preamble": [], "document": [self.lines] }

    def __repr__(self):
        return self.lines

class Bold:

    LATEX = "\\textbf{%s}"

    def __init__(self, text):
        self.text = text

    def latex(self, references):
        preamble, doc = combine_inlines(self.text, references)
        return { "preamble": preamble, "document": [Bold.LATEX % doc] }

    def __repr__(self):
        text = [x.__repr__() for x in self.text]
        text = ''.join(text)
        return "b:%s:b" % text

class Italic:

    LATEX = "\\textit{%s}"

    def __init__(self, text):
        self.text = text

    def latex(self, references):
        preamble, doc = combine_inlines(self.text, references)
        return { "preamble": preamble, "document": [Italic.LATEX % doc] }

    def __repr__(self):
        text = [x.__repr__() for x in self.text]
        text = ''.join(text)
        return "i:%s:i" % text

class Underline:

    LATEX = "\\underline{%s}"

    def __init__(self, text):
        self.text = text

    def latex(self, references):
        preamble, doc = combine_inlines(self.text, references)
        return { "preamble": preamble, "document": [Underline.LATEX % doc] }

    def __repr__(self):
        text = [x.__repr__() for x in self.text]
        text = ''.join(text)
        return "u:%s:u" % text

class Escaped:

    SYMBOLS = { "#": "\\#" }

    def __init__(self, char):
        self.char = char

    def latex(self, references):
        return { "preamble": [], "document": Escaped.SYMBOLS[self.char] }

    def __repr__(self):
        return self.char

class Footnote:

    NOTE = "\\footnote{%s}"

    def latex(self, references):
        footnotes = references["footnotes"]
        footnote = ""
        if len(footnotes) > 0:
            footnote = Footnote.NOTE % footnotes.pop(0)
        else:
            print("ERROR!! too many footnotes")

        return {"preamble": [], "document": [footnote] }

    def __repr__(self):
        return "^#"

class InlineRef:
    REF = { "ref": "\\ref{%s}",
            "cite": "\\cite{%s}" }

    def __init__(self, label):
        self.label = label

    def latex(self, references):
        doc = ""
        if self.label in references["references"]:
            ref = references["references"][self.label]
            doc = InlineRef.REF[ref["type"]] % self.label
        else:
            print("Reference '%s' not defined in document" % self.label)
        return { "preamble": [], "document": [doc] }


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


class Table:
    def __init__(self, rows):
        self.rows = rows

class TableCell:
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        text = [x.__repr__() for x in self.content]
        text = ''.join(text)
        return text

class TableRow:
    def __init__(self, cells):
        self.cells = cells

    def __repr__(self):
        cell = [x.__repr__() for x in self.cells]
        cell = ''.join(cell)
        return cell
