import collections
import pprint

class Serializable(object):
    __slots__ = ()
    def __serialize__(self):
        raise NotImplementedError("to be implemented by subclass")
    
    def __repr__(self):
        return repr(self.__serialize__())

def _pprint_operation(self, obj, *args):
    obj = obj.__serialize__()
    pprint.PrettyPrinter._dispatch[obj.__class__.__repr__](self, obj, *args)

pprint.PrettyPrinter._dispatch[Serializable.__repr__] = _pprint_operation

basic_literals = (str, bytes, int, float, complex, bool, type(None), )
def serialize(obj, additional_literals=()):
    if isinstance(obj, Serializable):
        obj = obj.__serialize__()
    if isinstance(obj, basic_literals):
        return obj
    if isinstance(obj, additional_literals):
        return obj
    if isinstance(obj, collections.abc.Mapping):
        return {serialize(key,additional_literals): serialize(value,additional_literals) for key, value in obj.items()}
    if isinstance(obj, set):
        return set(serialize(element,additional_literals) for element in obj)
    if isinstance(obj, tuple):
        return tuple(serialize(element,additional_literals) for element in obj)
    if isinstance(obj, collections.abc.Iterable):
        return [serialize(element,additional_literals) for element in obj]
    raise ValueError(obj,type(obj))

from ast import *
def extended_literal_eval(node_or_string, additional_literals={}):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, and None.
    
    I added additional_literals keyword to add things like Vector, Box, Sphere, ...
    """
    if isinstance(node_or_string, str):
        node_or_string = parse(node_or_string, mode='eval')
    if isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body
    def _convert_num(node):
        if isinstance(node, Constant):
            if type(node.value) in (int, float, complex):
                return node.value
        if isinstance(node, Num):
            return node.n
        if isinstance(node, Str):
            return node.s
        if isinstance(node, NameConstant):
            return node.value
        print(type(node), dir(node))
        raise ValueError('malformed node or string: ' + repr(node))
    def _convert_signed_num(node):
        if isinstance(node, UnaryOp) and isinstance(node.op, (UAdd, USub)):
            operand = _convert_num(node.operand)
            if isinstance(node.op, UAdd):
                return + operand
            else:
                return - operand
        return _convert_num(node)
    def _convert(node):
        if isinstance(node, Constant):
            return node.value
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            return list(map(_convert, node.elts))
        elif isinstance(node, Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, Call) and isinstance(node.func, Name):
            if node.func.id == 'set' and node.args == node.keywords == []:
                return set()
            constructor = additional_literals[node.func.id]
            args = map(_convert, node.args)
            kwargs = {keyword.arg:_convert(keyword.value) for keyword in node.keywords}
            return constructor(*args,**kwargs)
        elif isinstance(node, Dict):
            return dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        elif isinstance(node, BinOp) and isinstance(node.op, (Add, Sub)):
            left = _convert_signed_num(node.left)
            right = _convert_num(node.right)
            if isinstance(left, (int, float)) and isinstance(right, complex):
                if isinstance(node.op, Add):
                    return left + right
                else:
                    return left - right
        return _convert_signed_num(node)
    return _convert(node_or_string)

if __name__ == "__main__":
#    class Test(Serializable):
#        def __serialize__(self):
#            return ([1]*10,[2]*10,[3]*8,4)
#
#    t = Test()
#    pprint.pprint(t)
    
    def test(a,b,c,f=10):
        return [a,b,c,f]
    d = extended_literal_eval("test('tag',2,3,f=2)",{"test":test})
    print(d)
