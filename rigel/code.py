import dis
from collections import deque
from types import CodeType
from typing import Iterable

from rigel.cfg import CFGBuilder, calculate_stack_size
from rigel.instruction import BaseInstruction, convert
from rigel.lnotab import assemble_lnotab
from rigel.utils import CompilerFlags, create_code_object


class Code:  # pylint: disable=too-many-instance-attributes
    def __init__(self, instructions: list[BaseInstruction]):
        self._instructions = instructions

        self._cfg = CFGBuilder().build(self._instructions)

        self._co_argcount = 0
        self._co_posonlyargcount = 0
        self._co_kwonlyargcount = 0
        self._co_nlocals = 0
        self._co_consts = tuple()
        self._co_names = tuple()
        self._co_varnames = tuple()
        self._co_freevars = tuple()
        self._co_cellvars = tuple()
        self._co_flags = CompilerFlags.CO_NOFREE
        self._co_firstlineno = 1
        self._co_name = '<module>'
        self._co_filename = '<string>'

    def _co_code(self) -> bytes:
        return b''.join([instruction.as_bytes() for instruction in self._instructions])

    def code_object(self) -> CodeType:
        return create_code_object(
            co_argcount=self._co_argcount,
            co_posonlyargcount=self._co_posonlyargcount,
            co_kwonlyargcount=self._co_kwonlyargcount,
            co_nlocals=self._co_nlocals,
            co_stacksize=calculate_stack_size(self._instructions),
            co_flags=self._co_flags,
            co_code=self._co_code(),
            co_consts=self._cfg.co_consts,
            co_names=self._cfg.co_names,
            co_varnames=self._co_varnames,
            co_filename=self._co_filename,
            co_name=self._co_name,
            co_firstlineno=self._co_firstlineno,
            co_lnotab=b''.join(assemble_lnotab(self._instructions)),
            co_freevars=self._co_freevars,
            co_cellvars=self._co_cellvars,
        )


def flat_instructions(code: CodeType) -> Iterable[dis.Instruction]:
    todo = deque(list(dis.get_instructions(code)))
    while todo:
        instruction = todo.popleft()
        if isinstance(instruction.argval, CodeType):
            todo.extend(list(dis.get_instructions(instruction.argval)))

        yield instruction


def make_code_object(instructions: list[dis.Instruction]) -> CodeType:
    return Code(instructions=list(convert(instructions))).code_object()
