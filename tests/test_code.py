import dis
from textwrap import dedent

import pytest

from rigel.code import Code
from rigel.instruction import convert
from rigel.utils import code_diff


CALL_BUILTIN_FN = """
    print(r'string 1')
    print(f'string 2')
"""
FUNC_PRINT_STATEMENT = """
def test_func3(param1):
    return param1

def test_func2(param1):
    return param1

def test_func(param1):
    return param1

print(test_func3(r'string 1'))
print(test_func(r'string 2'))
print(test_func2(r'string 3'))
"""

LOOP_FOR_STATEMENT = """
a = 0
for _ in range(10):
    a += 1
"""

IF_ELSE_STATEMENT = """
a = 123
b = 2
if a == 0:
    print(b)
else:
    print(a)
b = 5
"""


@pytest.mark.parametrize('test_input, expected', [
    (CALL_BUILTIN_FN, {}),
    (FUNC_PRINT_STATEMENT, {}),
    (LOOP_FOR_STATEMENT, {}),
    (IF_ELSE_STATEMENT, {}),
])
def test_code(test_input, expected):
    native_code = compile(dedent(test_input), '<string>', 'exec')
    instructions = dis.get_instructions(native_code)

    generated_code = Code(instructions=list(convert(instructions))).code_object()

    assert code_diff(native_code, generated_code) == expected
