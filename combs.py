"""Parser combinators."""

OK = True

class ParseError(Exception): pass

class Parser(object):

    _result = None

    def result(self): return self._result

    def success(self): return self._result[0]
    def data(self): return self._result[1]
    def the_rest(self): return self._result[2]

    def parse(self): raise Exception("_parse() not implemented")

    def __rshift__(self, other):
        return DropFirstParser(self, other)

    def __lshift__(self, other):
        return DropSecondParser(self, other)

    def __ge__(self, other):
        return SeqParser(self, other)

    def __or__(self, other):
        return TryParser(self, other)

    def __add__(self, other):
        return SumParser(self, other)

    def __mul__(self, other):
        return CollectParser(self, other)

class DropFirstParser(Parser):

    pred = None
    succ = None

    def __init__(self, pred=None, succ=None):
        self.pred = pred
        self.succ = succ

    def parse(self, stream):
        self.pred.parse(stream)
        (success, data, the_rest) = self.pred.result()
        if success:
            self._result = self.succ.parse(the_rest).result()
            return self
        else:
            self._result = self.pred.result()
            return self

class DropSecondParser(Parser):

    pred = None
    succ = None

    def __init__(self, pred=None, succ=None):
        self.pred = pred
        self.succ = succ

    def parse(self, stream):
        self.pred.parse(stream)
        if self.pred.success():
            self.succ.parse(self.pred.the_rest())
            if self.succ.success():
                self._result = (
                    OK, self.pred.data(), self.succ.the_rest())
                return self
            else:
                self._result = self.succ.result()
                return self
        else:
            self._result = self.pred.result()
            return self

class SeqParser(Parser):

    pred = None
    succ = None

    def __init__(self, pred=None, succ=None):
        self.pred = pred
        self.succ = succ

    def parse(self, stream):
        self.pred.parse(stream)
        (success1, data1, the_rest1) = self.pred.result()
        if success1:
            self.succ.parse(the_rest1)
            (success2, data2, the_rest2) = self.succ.result()
            if success2:
                self._result = (success2, data1 + data2, the_rest2)
                return self
            else:
                self._result = self.succ.result()
                return self
        else:
            self._result = self.pred.result()
            return self

class TryParser(Parser):

    pred = None
    succ = None

    def __init__(self, pred=None, succ=None):
        self.pred = pred
        self.succ = succ

    def parse(self, stream):
        self.pred.parse(stream)
        if self.pred.success():
            self._result = self.pred.result()
            return self
        else:
            self.succ.parse(stream)
            self._result = self.succ.result()
            return self

class SumParser(Parser):

    pred = None
    succ = None

    def __init__(self, pred=None, succ=None):
        self.pred = pred
        self.succ = succ

    def parse(self, stream):
        self.pred.parse(stream)
        self.succ.parse(stream)
        status = (self.pred.success(), self.succ.success())
        data = (self.pred.data(), self.succ.data())
        the_rest = (self.pred.the_rest(), self.succ.the_rest())
        self._result = (status, data, the_rest)
        return self

class CollectParser(Parser):

    pred = None
    succ = None

    def __init__(self, pred=None, succ=None):
        self.pred = pred
        self.succ = succ

    def parse(self, stream):
        self.pred.parse(stream)
        (success1, data1, the_rest1) = self.pred.result()
        if success1:
            self.succ.parse(the_rest1)
            (success2, data2, the_rest2) = self.succ.result()
            if success2:
                try:
                    data = list(data1)
                except TypeError:
                    data = [data1]
                self._result = (success2, data + [data2], the_rest2)
                return self
            else:
                self._result = (success2, data2, the_rest2)
                return self
        else:
            self._result = (success1, data1, the_rest1)
            return self

class Any(Parser):

    def parse(self, stream):
        if len(stream) == 0:
            msg = "unexpected eof"
            self._result = (not OK, msg, stream)
        else:
            self._result = (OK, stream[0], stream[1:])
        return self

class Eof(Parser):

    def parse(self, stream):
        if len(stream) == 0:
            self._result = (OK, "", stream)
        else:
            msg = "expected eof, but got: {}".format(stream[0])
            self._result = (not OK, msg, stream)
        return self

class Const(Parser):

    value = None

    def __init__(self, value=None):
        self.value = value

    def parse(self, stream):
        self._result = (OK, self.value, stream)
        return self

class Bind(Parser):

    parser = None
    fn = None

    def __init__(self, parser=None, fn=None):
        self.parser = parser
        self.fn = fn

    def parse(self, stream):
        self.parser.parse(stream)
        if self.parser.success():
            status = self.parser.success()
            data = self.fn(self.parser.data())
            the_rest = self.parser.the_rest()
            self._result = (status, data, the_rest)
            return self
        else:
            self._result = self.parser.result()
            return self

class Is(Parser):

    fn = None

    def __init__(self, fn=None):
        self.fn = fn

    def parse(self, stream):
        parser = Any()
        (success, data, the_rest) = parser.parse(stream).result()
        if success:
            if self.fn(data):
                self._result = (success, data, the_rest)
                return self
            else:
                msg = "{} not matched".format(data)
                self._result = (not OK, msg, the_rest)
                return self
        else:
            self._result = (success, data, the_rest)
            return self

class Char(Parser):

    char = None

    def __init__(self, char=None):
        self.char = char

    def parse(self, stream):
        parser = Is(lambda x: x == self.char)
        parser.parse(stream)
        self._result = parser.result()
        return self

class Space(Parser):

    def parse(self, stream):
        parser = Is(lambda x: x.isspace())
        parser.parse(stream)
        self._result = parser.result()
        return self

class Digit(Parser):

    def parse(self, stream):
        parser = Is(lambda x: x.isdigit())
        parser.parse(stream)
        self._result = parser.result()
        return self

class Alpha(Parser):

    def parse(self, stream):
        parser = Is(lambda x: x.isalpha())
        parser.parse(stream)
        self._result = parser.result()
        return self

class ZeroOrMore(Parser):

    parser = None

    def __init__(self, parser=None):
        self.parser = parser

    def parse(self, stream):
        self._result = (OK, "", stream)
        do_again = True
        remainder = stream
        while do_again:
            self.parser.parse(remainder)
            (success, data, the_rest) = self.parser.result()
            if success:
                if self._result is None:
                    prev_data = ""
                else:
                    prev_data = self.data()
                self._result = (success, prev_data + data, the_rest)
                self.parser._result = None
                if len(the_rest) > 0:
                    remainder = the_rest
                else:
                    do_again = False
            else:
                do_again = False
        return self

class OneOrMore(Parser):

    parser = None

    def __init__(self, parser=None):
        self.parser = parser

    def parse(self, stream):
        self._result = (not OK, "no matches found", stream)
        do_again = True
        remainder = stream
        while do_again:
            self.parser.parse(remainder)
            (success, data, the_rest) = self.parser.result()
            if success:
                if self.success() is not OK:
                    prev_data = ""
                else:
                    prev_data = self.data()
                self._result = (success, prev_data + data, the_rest)
                self.parser._result = None
                if len(the_rest) > 0:
                    remainder = the_rest
                else:
                    do_again = False
            else:
                do_again = False
        return self
