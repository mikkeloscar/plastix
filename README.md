# Plastix

## Grammar

```
Document ::= Blocks
Blocks ::= Block
        | Block Blocks
Block ::= Section
       | List
       | FootnoteRef
       | Figure
       | Paragraph

Paragraph ::= Inlines
List ::= UnorderedList
      | OrderedList

UnorderedList ::= '* ' Block
Inline ::= Color
        | Bold
        | Italic
        | Underline
        | Text
Inlines ::= Inline
         | Inline Inlines
Line ::= Inlines Endline
Section ::= '=====' Line
         | '====' Line
         | '===' Line
         | '==' Line
         | '=' Line
ColorValue ::= see: http://www.w3schools.com/cssref/css_colornames.asp
ColorDef ::= '#' Int Int Int Int Int Int <- hex
          |  '(' rgb ')' <- RGB
          | ColorValue   <- predefined colors
Color ::= '<' Inlines ':' ColorDef '>'
Italic ::= '//' Inlines '//'
Bold ::= '*' Inlines '*'
Underline ::= '_' Inlines '_'
Footnote ::= '^#'
FootnoteRef ::= '#:' Inlines
Figure ::= '![' Img ']' Label ('\n') Caption
Caption ::= E
         | Inlines
Label ::= E
       | Ident
Ident ::= [a-z0-9_:-]+

```


## Cheatsheet
```
Unordered List:

* Shopping
  * Eggs
    * small
  * Milk
  * Bacon

Bold:

bla *bold* bla

Italic:

bla //bla// bla

Color:

bla <bla:red> bla

Underline:

_underline_


Sections

= Header h1

== Header h2

=== Header h3


References

The book^# is very good^#.

#: Harry Potter
#: Harry Potter

I cite [cite] something shown in Figure _[fig:2].

References:
[id]: Author

Figures

(label optional) - captional optional (check for blank line)

![image.jpg] label
Caption text

Tables

(måske uden plusser +++)
kunne være sejt med alignment også

+----------------------------+
| Year  | President          |
+----------------------------+
| 1789  | George Washington  |
+----------------------------+
| 1797  | John Adams         |
+----------------------------+
| 1801  | Thomas Jefferson   |
+----------------------------+

Math

TI-syntax:

Wrap in `$`

x=(2ab+a*2)/(a*2^2+sqrt(9^a))+a


```

## Grammar simplified

```
Document ::= Blocks
Blocks ::= E
        | Block
        | Block Blocks

Block ::= Section
       | List
       | FootnoteRef
       | Figure
       | Paragraph
       | MathBlock
       | Table
       | Newline

Paragraph ::= Lines + Newline
List ::= UnorderedList
      | OrderedList
UnorderedList ::= UnorderedListItem
               | UnorderedListItem UnorderedList
UnorderedListItem ::= E
                   | '* ' Block
                   | Spacing UnorderedListItem
Spacing ::= E
         | Space
         | Tab

OrderedList ::= OrderedListItem
             | OrderedListItem OrderedList
OrderedListItem ::= E
                 |'# ' Block
                 | Spacing OrderedListItem
Inline ::= Color
        | Bold
        | Italic
        | Underline
        | Symbol
        | InlineMath
        | Text (regex)
Inlines ::= Inline
         | Inline Inlines
Line ::= Inlines Newline
Lines ::= Line
       | Lines
Section ::= '=====' Line
         | '====' Line
         | '===' Line
         | '==' Line
         | '=' Line

ColorValue ::= 'red'
            | 'blue'
            | 'green'
            | 'yellow'
            | 'black'
            | 'white'
            | 'purple'
            | 'cyan'
            | 'magenta'
            | '...'
Color ::= '<' Inlines ':' ColorValue '>'
Italic ::= '//' Inlines '//'
Bold ::= '*' Inlines '*'
Underline ::= '_' Inlines '_'

Footnote ::= '^#'
FootnoteRef ::= '#:' Inlines

Figure ::= '![' Img ']' Label Newline Caption
Caption ::= E
         | Inlines Newline
Label ::= E
       | Ident

InlineMath ::= '$' Math '$'
MathBlock ::= InlineMath Newline

Table ::= TableHLine TableRows
TableRows ::= E
           | TableRow
           | TableRow TableRows
TableHLine ::= '-----' Newline
TableRow ::= '|' TableCells
TableCells ::= TableCell
            |  TableCell TableCells
TableCell ::= Inline '|' Newline

Ident ::= [a-z0-9_:-]+
Symbol ::= '#' SymbolName

```
