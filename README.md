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



```
