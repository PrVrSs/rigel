from contextlib import contextmanager
from typing import Iterable

from .exceptions import UnknownInstructionError


class InstructionVisitor:
    """"""
    def visit(self, instruction, block):
        return getattr(
            self,
            f'visit_{instruction.opname.lower()}',
            self._unknown_instruction,
        )(instruction, block)

    def _unknown_instruction(self, *args, **kwargs):
        raise UnknownInstructionError


class BlockVisitor:
    """"""
    def visit(self, block):
        return getattr(
            self,
            f'visit_{block.__class__.__name__.lower()}',
            self.generic_visit,
        )(block)

    def generic_visit(self, blocks):
        for block in blocks:
            self.visit(block)


class Listener:
    def walk(self, node) -> None:
        with self._listener(node):
            for child in node.children:
                self.walk(child)

    @contextmanager
    def _listener(self, node) -> Iterable[None]:
        self.enter_rule(node)
        yield
        self.exit_rule(node)

    def enter_rule(self, node) -> None:
        raise NotImplementedError

    def exit_rule(self, node) -> None:
        raise NotImplementedError
