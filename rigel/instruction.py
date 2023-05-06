import dis
from enum import IntFlag
from typing import Final, Iterable, NamedTuple

import opcode


UNCONDITIONAL_JUMP_INSTRUCTIONS: Final = frozenset({
    'JUMP_FORWARD',
    'JUMP_ABSOLUTE',
    'JUMP_BACKWARD',
    'JUMP_BACKWARD_NO_INTERRUPT',
})

FINAL_INSTRUCTIONS: Final = frozenset({
    'RETURN_VALUE',
    'RAISE_VARARGS',
    'RERAISE',
    'BREAK_LOOP',
    'CONTINUE_LOOP',
})


STATIC_STACK_EFFECTS = {

}

DYNAMIC_STACK_EFFECTS = {
    **{
        opname: lambda effect: (effect - 1, 1)
        for opname in (
            'MAKE_FUNCTION',
            'CALL_FUNCTION',
            'CALL_FUNCTION_EX',
            'CALL_FUNCTION_KW',
            'CALL_METHOD'
        )
    }

}


class IFlag(IntFlag):
    NONE = 0
    HAS_CONST = 1
    HAS_NAME = 2
    HAS_JREL = 4
    HAS_JABS = 8
    HAS_JUNKNOWN = 16
    HAS_LOCAL = 32
    HAS_FREE = 64
    HAS_NARGS = 128
    HAS_ARGUMENT = 256
    NO_NEXT = 512
    STORE_JUMP = 1024
    PUSHES_BLOCK = 2048
    POPS_BLOCK = 4096


class IProperties:
    has_const = property(lambda self: bool(self.FLAG & IFlag.HAS_CONST))
    has_name = property(lambda self: bool(self.FLAG & IFlag.HAS_NAME))
    has_jrel = property(lambda self: bool(self.FLAG & IFlag.HAS_JREL))
    has_jabs = property(lambda self: bool(self.FLAG & IFlag.HAS_JABS))
    has_junknown = property(lambda self: bool(self.FLAG & IFlag.HAS_JUNKNOWN))
    has_jump = property(lambda self: bool(
        self.FLAG & (IFlag.HAS_JREL | IFlag.HAS_JABS | IFlag.HAS_JUNKNOWN)))
    has_local = property(lambda self: bool(self.FLAG & IFlag.HAS_LOCAL))
    has_free = property(lambda self: bool(self.FLAG & IFlag.HAS_FREE))
    has_nargs = property(lambda self: bool(self.FLAG & IFlag.HAS_NARGS))
    has_argument = property(lambda self: bool(self.FLAG & IFlag.HAS_ARGUMENT))
    no_next = property(lambda self: bool(self.FLAG & IFlag.NO_NEXT))
    carry_on_to_next = property(lambda self: not self.FLAGS & IFlag.NO_NEXT)
    store_jump = property(lambda self: bool(self.FLAG & IFlag.STORE_JUMP))
    does_jump = property(lambda self: self.has_jump and not self.store_jump)
    pushes_block = property(lambda self: bool(self.FLAG & IFlag.PUSHES_BLOCK))
    pops_block = property(lambda self: bool(self.FLAG & IFlag.POPS_BLOCK))
    has_arg = property(lambda self: False)


class MetaInstruction(type):
    def __new__(cls, *args, **kwargs):
        name, base, variables = args

        return type.__new__(
            cls,
            name,
            base,
            {
                **variables,
                **{
                    key: value
                    for key, value in IProperties.__dict__.items()
                    if not key.startswith('__')
                },
            },
            **kwargs
        )


class BaseInstruction(metaclass=MetaInstruction):  # pylint: disable=too-many-instance-attributes
    FLAG = IFlag.NONE

    oparg = property(lambda self: self.arg if self.has_argument() else None)

    def __init__(self, opname, opcode_, arg, argval, argrepr, offset, starts_line, is_jump_target):
        self.opname = opname
        self.opcode = opcode_
        self.arg = arg
        self.argval = argval
        self.argrepr = argrepr
        self.offset = offset
        self.starts_line = starts_line
        self.is_jump_target = is_jump_target

    def __repr__(self):
        return f'{self.opname} arg {self.arg} | argrepr `{self.argrepr}` | offset  {self.offset}'

    def get_stack_effect(self):
        return dis.stack_effect(self.opcode, self.oparg)

    def _stack_effect(self, jump: bool | None = None) -> int:
        if self.opcode < opcode.HAVE_ARGUMENT:
            arg = None
        elif self.opname == 'LOAD_GLOBAL' and isinstance(self.arg, tuple):
            arg = self.arg[0]
        elif not isinstance(self.arg, int) or self.opcode in opcode.hasconst:
            arg = 0
        else:
            arg = self.arg

        return dis.stack_effect(self.opcode, arg, jump=jump)

    def stack_effect(self, jump: bool | None = None) -> tuple[int, int]:
        if self.opname in STATIC_STACK_EFFECTS:
            return STATIC_STACK_EFFECTS[self.opname]

        effect_ = self._stack_effect(jump=jump)
        if self.opname in DYNAMIC_STACK_EFFECTS:
            return DYNAMIC_STACK_EFFECTS[self.opname](effect_)

        return effect_, 0

    def is_final(self) -> bool:
        if self._is_final():
            return True

        if self._is_unconditional_jump():
            return True

        return False

    def _is_final(self) -> bool:
        return self.opname in FINAL_INSTRUCTIONS

    def _is_unconditional_jump(self) -> bool:
        return self.opname in UNCONDITIONAL_JUMP_INSTRUCTIONS

    def has_argument(self) -> bool:
        return self.opcode >= dis.HAVE_ARGUMENT

    def as_bytes(self) -> bytes:
        size = self.size
        arg = self.arg or 0
        ret = [self.opcode, arg & 0xff]

        for _ in range(size // 2 - 1):
            arg >>= 8
            ret = [
                *[dis.opmap['EXTENDED_ARG'], arg & 0xff],
                *ret
            ]

        return bytes(ret)

    @property
    def size(self):
        match self.arg:
            case None:
                return 2
            case value if value <= 0xff:
                return 2
            case value if value <= 0xffff:
                return 4
            case value if value <= 0xffffff:
                return 6
            case _:
                return 8


class WithArgument(BaseInstruction):
    pass


class LoadName(WithArgument):
    FLAG = IFlag.HAS_NAME | IFlag.HAS_ARGUMENT


class LoadConst(WithArgument):
    FLAG = IFlag.HAS_CONST | IFlag.HAS_ARGUMENT


class StoreName(WithArgument):
    FLAG = IFlag.HAS_NAME | IFlag.HAS_ARGUMENT


class MakeFunction(WithArgument):
    FLAG = IFlag.HAS_ARGUMENT


class PopTop(BaseInstruction):
    pass


class ReturnValue(BaseInstruction):
    FLAG = IFlag.HAS_JUNKNOWN | IFlag.NO_NEXT


class CallFunction(WithArgument):
    FLAG = IFlag.HAS_NARGS | IFlag.HAS_ARGUMENT | IFlag.HAS_JUNKNOWN


class GetIter(BaseInstruction):
    pass


class ForIter(WithArgument):
    FLAG = IFlag.HAS_JREL | IFlag.HAS_ARGUMENT


class JumpAbsolute(WithArgument):
    FLAG = IFlag.HAS_JABS | IFlag.HAS_ARGUMENT | IFlag.NO_NEXT


class InplaceAdd(BaseInstruction):
    pass


PYTHON_OPCODE_INSTRUCTION_MAP = {
    1: PopTop,
    55: InplaceAdd,
    68: GetIter,
    83: ReturnValue,
    90: StoreName,
    93: ForIter,
    100: LoadConst,
    101: LoadName,
    113: JumpAbsolute,
    131: CallFunction,
    132: MakeFunction,
}


class Positions(NamedTuple):
    lineno: int | None = ...
    end_lineno: int | None = ...
    col_offset: int | None = ...
    end_col_offset: int | None = ...


def convert(instructions: list[dis.Instruction]) -> Iterable[BaseInstruction]:
    line = 0
    for instruction in instructions:
        if instruction.starts_line is not None:
            line = instruction.starts_line

        yield PYTHON_OPCODE_INSTRUCTION_MAP[instruction.opcode](
            opname=instruction.opname,
            opcode_=instruction.opcode,
            arg=instruction.arg,
            argval=instruction.argval,
            argrepr=instruction.argrepr,
            offset=instruction.offset,
            starts_line=line,
            is_jump_target=instruction.is_jump_target,
        )
