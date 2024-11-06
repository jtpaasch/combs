# Combs

A toy parser combinator library (in Python). For pedagogical purposes.

To use it, import the contents of the `combs.py` module:

``` python
from combs import *
```

The tools in this package produce _parsers_, which can be combined
to build more complex parsers.

An example:

```python
spaces = ZeroOrMore(Space()) # Match zero or more spaces
word = Alpha() >= OneOrMore(Alpha() | Digit()) # Match a letter, then one or more letters or digits
parser = word << spaces # Match a word, then discard any spaces
parser.parse("foo34  ")
parser.data() # "foo34"
```

A slightly more complex example:

```python
spaces = ZeroOrMore(Space()) # Match zero or more spaces
num = OneOrMore(Digit()) << spaces # Match one or more digits then discard spaces
plus = Char("+") << spaces # Match "+" then discard spaces
parser = num * plus * num # Combine a number, plus, and a number
parser.parse("234 + 5")
parser.data() # ["234", "+", "5"]
```

## Interacting with a parser

Suppose you have built a parser called `parser`.

To have `parser` parse a stream of text, e.g., `"some text"`:

``` python
parser.parse("some text")
```

When that command executes, the parser will consume/parse as many
characters from the front of the input stream `some text` as it can,
and then it will stop.

To see if the parse succeeded:

``` python
parser.success() # True or False
```

To see the consumed/parsed data (or error message if `success()`
is `False`):

``` python
parser.data()
```

To see the rest of the input stream that was not consumed by the parse:

``` python
parser.the_rest()
```

To see all three pieces of information as a triple
`(success(), data(), the_rest())`:

``` python
parser.result()
```


## Simple parsers

`Any()` returns a parser that will consume any character.
E.g., to consume the first character of a stream:

``` python
parser = Any()

parser.parse("a")
parser.data() # "a"

parser.parse("")
parser.success() # False, there is no char to consume
```

`Eof()` produces a parser that will check that the stream is empty/done.

``` python
parser = Eof()

parser.parse("")
parser.success() # True

parser.parse("a")
parser.success() # False, since the stream is not empty/done
```

`Char(c)` produces a parser that consumes the character `c`, e.g.:

``` python
parser = Char("x")

parser.parse("x")
parser.data() # "x"

parser.parse("a")
parser.success() # False, since the first char is not "x"
```

`Is(fn)` produces a parser that applies `fn : Char -> Bool` to the
consumed character.

``` python
parser = Is(lambda x: x == "3")

parser.parse("3")
parser.success() # True

parser.parse("x")
parser.success() # False
```

`Digit()`, `Alpha()`, and `Space()` work as you'd expect:

``` python
Digit().parse("1").success() # True
Digit().parse("x").success() # False

Alpha().parse("x").success() # True
Alpha().parse("1").success() # False

Space().parse(" ").success() # True
Space().parse("abc").success() # False
```

`Const(value)` consumes nothing and produces the provided `value`.

``` python
Const("abc").parse("x").data() # "abc"
```


## Parsers that extend parsers

`ZeroOrMore(parser)` produces a parser that consumes zero or more
sequential characters that match the given `parser`.

``` python
parser = ZeroOrMore(Char("x"))

parser.parse("xxxbc")
parser.success() # True
parser.data() # "xxx"
parser.the_rest() # "bc"

parser.parse("abcd")
parser.success() # True
parser.data() # "" since zero "x"s were matched
parser.the_rest() # "abcd"
```

`OneOrMore(parser)` produces a parser that consumes one or more
sequential characters that match the given `parser`.

``` python
parser = OneOrMore(Char("x"))

parser.parse("xxxbc")
parser.success() # True
parser.data() # "xxx"
parser.the_rest() # "bc"

parser.parse("abcd")
parser.success() # False since at least one "x" is required
```

`Bind(parser, fn)` applies the given `parser` to the stream and then
feeds the output to the given `fn`.

``` python
numeral = OneOrMore(Digit())
parser = Bind(numeral, int)

numeral.parse("123").data() # "123", i.e., a string
parser.parse("123").data() # 123, i.e., an integer
```


## Combinators

`parser1 >= parser2` produces a parser that takes the parsed output
of `parser1` and then prepends it to the parsed output of `parser2`
(if successful, otherwise it returns the error).

``` python
parser = Char("a") >= Char("b")
parser.parse("ab").data() # "ab"
```

`parser1 >> parser2` produces a parser that is like one produced by
`parser1 >= parser2`, except it discards the output of `parser1`.

``` python
parser = Char("a") >> Char("b")
parser.parse("ab").data() # "b" since "a" was discarded
```

`parser1 << parser2` is like `parser1 >> parser2` except the results of
`parser2` are discarded and only the results of `parser1` are kept.

``` python
parser = Char("a") << Char("b")
parser.parse("ab").data() # "a" since "b" was discarded
```

`parser1 * parser2` runs `parser1` then `parser2`, and appends each result to a list.

``` python
parser = Char("a") * Char("b")
parser.parse("ab").data() # ["a", "b"] since first "a" is matched, then "b" is matched
```

`parser1 | parser2` tries `parser1` first, and if that fails, it
then tries `parser2`.

``` python
parser = Char("a") | Char("b")
parser.parse("a").success() # True, because `Char("a")` succeeded
parser.parse("b").success() # True, because `Char("b")` succeeded
parser.parse("c").success() # False, because neither succeeded
```
