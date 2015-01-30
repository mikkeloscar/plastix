from parser import document as parser

import sys

from elements import (
        FootnoteRef,
        Reference
)


class Plastix:

    def __init__(self, parse):
        self.parse = parse
        self.preamble = [
                "\\documentclass{article}\n",
                "\\usepackage[utf8]{inputenc}\n",
                "\\usepackage[T1]{fontenc}\n",
                "\\usepackage{lmodern}\n",
                "\\usepackage[english]{babel}\n"
                ]
        self.document = []
        self.references()
        self.interpret()

    def references(self):
        self.references = { "references": {}, "footnotes": [] }
        for p in self.parse:
            if isinstance(p, FootnoteRef):
                self.references["footnotes"].append(p.reference(self.references))
            elif isinstance(p, Reference):
                ident, val = p.reference(self.references)
                ref = { "type":  "cite", "value": val }
                self.references["references"][ident] = ref

    def interpret(self):
        print(self.parse)
        for p in self.parse:
            tex = p.latex(self.references)
            self.preamble += tex["preamble"]
            self.document += tex["document"]

    def latex(self):
        output = ""
        for p in self.preamble:
            output += p
        output += "\\begin{document}\n"
        for d in self.document:
            output += d
        output += "\\end{document}\n"
        return output

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
    return plastix

def main():
    if len(sys.argv) > 1:
        content = load(sys.argv[1])
        plastix = Plastix(parser.parse(content))
        sys.stdout.write(plastix.latex())
    else:
        print("Please provide a plastix file as first argument.")

if __name__ == "__main__":
    main()
