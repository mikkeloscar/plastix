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
Line ::= Inline Endline
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
