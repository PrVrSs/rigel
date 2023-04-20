from enum import IntFlag
from inspect import isbuiltin
from textwrap import dedent
from types import CodeType
from typing import Any, Iterable


class CompilerFlags(IntFlag):
    """code.h"""
    CO_OPTIMIZED = 0x0001
    CO_NEWLOCALS = 0x0002
    CO_VARARGS = 0x0004
    CO_VARKEYWORDS = 0x0008
    CO_NESTED = 0x0010
    CO_GENERATOR = 0x0020

    CO_NOFREE = 0x0040

    CO_COROUTINE = 0x0080
    CO_ITERABLE_COROUTINE = 0x0100
    CO_ASYNC_GENERATOR = 0x0200

    CO_FUTURE_DIVISION = 0x20000
    CO_FUTURE_ABSOLUTE_IMPORT = 0x40000
    CO_FUTURE_WITH_STATEMENT = 0x80000
    CO_FUTURE_PRINT_FUNCTION = 0x100000
    CO_FUTURE_UNICODE_LITERALS = 0x200000

    CO_FUTURE_BARRY_AS_BDFL = 0x400000
    CO_FUTURE_GENERATOR_STOP = 0x800000
    CO_FUTURE_ANNOTATIONS = 0x1000000


def create_code_object(  # pylint: disable=too-many-arguments,too-many-locals
        co_argcount: int,
        co_posonlyargcount: int,
        co_kwonlyargcount: int,
        co_nlocals: int,
        co_stacksize: int,
        co_flags: int,
        co_code: bytes,
        co_consts: tuple[Any, ...],
        co_names: tuple[str, ...],
        co_varnames: tuple[str, ...],
        co_filename: str,
        co_name: str,
        co_firstlineno: int,
        co_lnotab: bytes,
        co_freevars: tuple[Any, ...],
        co_cellvars: tuple[Any, ...],
) -> CodeType:
    """
    :param co_argcount:
    :param co_posonlyargcount:
    :param co_kwonlyargcount:
    :param co_nlocals:
    :param co_stacksize:
    :param co_flags:
    :param co_code:
    :param co_consts:
    :param co_names:
    :param co_varnames:
    :param co_filename:
    :param co_name:
    :param co_firstlineno:
    :param co_lnotab:
    :param co_freevars:
    :param co_cellvars:
    :return:
    """
    return CodeType(
        co_argcount,
        co_posonlyargcount,
        co_kwonlyargcount,
        co_nlocals,
        co_stacksize,
        co_flags,
        co_code,
        co_consts,
        co_names,
        co_varnames,
        co_filename,
        co_name,
        co_firstlineno,
        co_lnotab,
        co_freevars,
        co_cellvars,
    )


def get_co_fields(code: CodeType) -> Iterable[tuple[str, Any]]:
    """
    :param code:
    :return:
    """
    for co_property in dir(code):
        if co_property.startswith('co_') is False:
            continue

        value = getattr(code, co_property)
        if isbuiltin(value):
            value = list(value())

        yield co_property, value


def code_diff(code_a: CodeType, code_b: CodeType) -> dict[str, tuple[Any, Any]]:
    """
    :param code_a:
    :param code_b:
    :return:
    """
    co_fields_a = dict(get_co_fields(code_a))
    co_fields_b = dict(get_co_fields(code_b))

    return {
        key: (value, co_fields_b[key])
        for key, value in co_fields_a.items()
        if co_fields_b[key] != value
    }


def main():
    raw_code_a = '''print('string 1')
print('string 2')
    '''

    raw_code_b = '''
    print('string 3')
    print('string 4')
    '''

    c_code_a = compile(dedent(raw_code_a), '<string>', 'exec')
    c_code_b = compile(dedent(raw_code_b), '<string>', 'exec')

    diff = code_diff(c_code_a, c_code_b)
    print(diff)


if __name__ == '__main__':
    main()
