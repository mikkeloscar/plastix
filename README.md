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
```
