import dis
from textwrap import dedent

import pytest

from rigel.code import Code
from rigel.instruction import convert
from rigel.utils import code_diff


print_str = "print('string')"
two_print_str = """
    print(r'string 1')
    print(f'string 2')
"""
func_print_str = """
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

loop_str = """
a = 0
for _ in range(10):
    a += 1
"""


@pytest.mark.parametrize('test_input, expected', [
    (print_str, {}),
    (two_print_str, {}),
    (func_print_str, {}),
    (loop_str, {}),
])
def test_code(test_input, expected):
    native_code = compile(dedent(test_input), '<string>', 'exec')
    instructions = dis.get_instructions(native_code)

    generated_code = Code(instructions=list(convert(instructions))).code_object()

    assert code_diff(native_code, generated_code) == expected
