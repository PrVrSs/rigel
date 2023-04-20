import uuid

from more_itertools import unique_everseen

from rigel.instruction import BaseInstruction
from rigel.visitor import InstructionVisitor


def calculate_stack_size(instructions):
    size = 0
    minsize = 0
    maxsize = 0

    for instruction in instructions:
        pre_, post_ = instruction.stack_effect(jump=False)
        size += pre_ + post_
        maxsize = max(maxsize, size)
        minsize = min(minsize, size)

    return maxsize


class Block:
    def __init__(self, instruction=None, label=None):
        self.graph = None
        self.next = set()
        self.prev = set()
        self._instructions = []
        self.label = label
        self.labels = {}
        self.uuid = uuid.uuid4()

        if instruction:
            self._instructions.append(instruction)

    def add(self, instruction: BaseInstruction):
        self._instructions.append(instruction)


class Frame:
    pass


class ControlFlowGraph:
    def __init__(self):
        self._blocks = []

        self.start_block = self.new_block()
        self.start_block.label = '<start>'

        self._consts = []
        self._names = []

    @property
    def co_consts(self):
        return tuple(unique_everseen(self._consts))

    @property
    def co_names(self):
        return tuple(unique_everseen(self._names))

    def add_const(self, const):
        self._consts.append(const)

    def add_name(self, name):
        self._names.append(name)

    def new_block(self, label=None):
        block = Block(label=label)
        block.graph = self
        self._blocks.append(block)
        return block


class CFGBuilder(InstructionVisitor):
    """A visitor for determining the control flow of a Python program from an instructions."""
    def __init__(self):
        self._cfg = ControlFlowGraph()
        self._frames = []

    def build(self, instructions: list[BaseInstruction]) -> ControlFlowGraph:
        current_block = self._cfg.start_block

        for instruction in instructions:
            current_block = self.visit(instruction, current_block)

        return self._cfg

    def visit_load_name(self, instruction: BaseInstruction, block: Block) -> Block:
        self._cfg.add_name(instruction.argval)
        block.add(instruction)

        return block

    def visit_load_const(self, instruction: BaseInstruction, block: Block) -> Block:
        self._cfg.add_const(instruction.argval)
        block.add(instruction)

        return block

    def visit_call_function(self, instruction: BaseInstruction, block: Block) -> Block:
        block.add(instruction)

        return block

    def visit_pop_top(self, instruction: BaseInstruction, block: Block) -> Block:
        block.add(instruction)

        return block

    def visit_return_value(self, instruction: BaseInstruction, block: Block) -> Block:
        block.add(instruction)

        return block

    def visit_make_function(self, instruction: BaseInstruction, block: Block) -> Block:
        block.add(instruction)

        return block

    def visit_store_name(self, instruction: BaseInstruction, block: Block) -> Block:
        self._cfg.add_name(instruction.argval)
        block.add(instruction)

        return block


def build_cfg(instructions: list[BaseInstruction]):
    blocks = []
    code = []
    for instruction in instructions:
        code.append(instruction)
        if instruction.no_next or instruction.does_jump or instruction.pops_block:
            blocks.append(Block(code))
            code = []

    if code:
        blocks.append(Block(code))

    return blocks
