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

    def add_exit(self, block):
        """Adds an exit from this block to `block`."""
        self.next.add(block)
        block.prev.add(self)

    def get_source(self):
        return '\n'.join([str(inst) for inst in self._instructions])


class For(Block):
    pass


class Frame:
    pass


def add_instruction_to_block(_, instruction: BaseInstruction, block: Block) -> Block:
    block.add(instruction)
    return block


class ControlFlowGraph:
    def __init__(self, start_block):
        self.start_block = start_block

        self._blocks = []
        self._consts = []
        self._names = []

        self._blocks.append(start_block)

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


class CFGBuilder(InstructionVisitor):
    """A visitor for determining the control flow of a Python program from an instructions."""
    def __init__(self):
        self._frames = []

        self.current_block = Block(label='<start>')
        self._cfg = ControlFlowGraph(self.current_block)

    def build(self, instructions: list[BaseInstruction]) -> ControlFlowGraph:
        current_block = self._cfg.start_block

        for instruction in instructions:
            current_block = self.visit(instruction, current_block)

        return self._cfg

    visit_pop_top = add_instruction_to_block
    visit_inplace_add = add_instruction_to_block
    visit_return_value = add_instruction_to_block
    visit_call_function = add_instruction_to_block
    visit_get_iter = add_instruction_to_block
    visit_make_function = add_instruction_to_block

    def visit_load_name(self, instruction: BaseInstruction, block: Block) -> Block:
        self._cfg.add_name(instruction.argval)
        block.add(instruction)

        return block

    def visit_load_const(self, instruction: BaseInstruction, block: Block) -> Block:
        self._cfg.add_const(instruction.argval)
        block.add(instruction)

        return block

    def visit_store_name(self, instruction: BaseInstruction, block: Block) -> Block:
        self._cfg.add_name(instruction.argval)
        block.add(instruction)

        return block

    def visit_for_iter(self, instruction: BaseInstruction, block: Block) -> Block:
        new_block = For(label='<for>')
        new_block.add(instruction)
        block.add_exit(new_block)
        return new_block

    def visit_jump_absolute(self, instruction: BaseInstruction, block: Block) -> Block:
        block.add(instruction)

        new_block = Block()
        block.add_exit(new_block)
        return new_block


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
