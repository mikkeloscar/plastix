# Plastix

## Grammar

```
Document ::= Blocks
Blocks ::= Block
        | Block Blocks
Block ::= List

List ::= UnorderedList
      | OrderedList

UnorderedList ::= '* ' Block
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

bla <bla red> bla


Sections

= Header h1

== Header h2

=== Header h3


References

The book^# is very good.

#: Harry Potter

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




```
