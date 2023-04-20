import struct
from typing import Iterable

from more_itertools import first, last

from .instruction import BaseInstruction


def _assemble_emit_linetable_pair(bdelta: int, ldelta_: int | None) -> Iterable[bytes]:
    """Helper function for calculation lnotab for python3.10."""
    if ldelta_ is None:
        ldelta = -128
    else:
        ldelta = ldelta_

        while ldelta > 127:
            yield struct.pack('bb', 0, 127)
            ldelta -= 127

        while ldelta < -127:
            yield struct.pack('bb', 0, -127)
            ldelta += 127

    while bdelta > 254:
        yield struct.pack('Bb', 254, ldelta)

        if ldelta_ is None:
            ldelta = -128
        else:
            ldelta = 0

        bdelta -= 254

    yield struct.pack('Bb', bdelta, ldelta)


def assemble_lnotab(instructions: list[BaseInstruction], starts_line: int = 1) -> Iterable[bytes]:
    """
    Generate lnotab for python 3.10.

    See https://github.com/python/cpython/blob/3.10/Objects/lnotab_notes.txt
        for the description of the line number table.

    cpython:
        https://github.com/python/cpython/blob/3.10/Python/compile.c#L6681
    """
    instruction = first(instructions)

    old_offset = 0
    old_lineno = instruction.starts_line
    old_ldelta = instruction.starts_line - starts_line
    for instruction in instructions[1:]:
        ldelta = instruction.starts_line - old_lineno
        if ldelta == 0:
            continue

        yield from _assemble_emit_linetable_pair(
            bdelta=instruction.offset - old_offset,
            ldelta_=old_ldelta,
        )

        old_lineno = instruction.starts_line
        old_offset = instruction.offset
        old_ldelta = ldelta

    instruction = last(instructions)

    yield from _assemble_emit_linetable_pair(
        bdelta=instruction.offset + instruction.size - old_offset,
        ldelta_=old_ldelta,
    )
