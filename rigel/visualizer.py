from graphviz import Digraph

from rigel.code import Code
from rigel.instruction import convert
from rigel.visitor import BlockVisitor


class Visualizer(BlockVisitor):
    node_styles = {
        'default': ('rectangle', '#000000'),
    }

    def __init__(self, name: str = 'CFG', format_: str = 'png'):
        self._graph = Digraph(
            name=name,
            format=format_,
            graph_attr={
                'label': '',
                'ranksep': '0.02',
                'fontname': 'DejaVu Sans Mono',
                'compound': 'True',
                'pack': 'False',
            },
            node_attr={'fontname': 'DejaVu Sans Mono'},
            edge_attr={'fontname': 'DejaVu Sans Mono'},
        )

    def visualize(self, cfg):
        self.visit(cfg.start_block)

        return self._graph.render('asd', view=True)

    def stylize_node(self, block) -> tuple:
        shape, color = self.node_styles['default']
        text = r'\l'.join(line for line in block.get_source().splitlines())
        return shape, color, text

    def visit_block(self, block):
        node_shape, node_color, node_label = self.stylize_node(block)

        self._graph.node(
            str(block.uuid),
            label=node_label,
            _attributes={
                'shape': node_shape,
                'color': node_color,
            },
        )

        self.generic_visit(block.next)

        for exit_ in block.next:
            self._graph.edge(
                str(block.uuid),
                str(exit_.uuid),
            )

    def visit_for(self, block):
        node_shape, node_color, node_label = self.stylize_node(block)

        self._graph.node(
            str(block.uuid),
            label=node_label,
            _attributes={
                'shape': node_shape,
                'color': node_color,
            },
        )

        self._graph.edge(
            str(block.uuid),
            str(block.uuid),
        )

        self.generic_visit(block.next)

        for exit_ in block.next:
            self._graph.edge(
                str(block.uuid),
                str(exit_.uuid),
            )


def visualize(cfg):
    Visualizer().visualize(cfg)


if __name__ == '__main__':
    import dis
    from pprint import pprint
    from textwrap import dedent

    IF_STM = """
        a = 123
        b = 2
        if a == 0:
            print(b)
        else:
            print(a)
        b = 5
        """

    native_code = compile(dedent(IF_STM), '<string>', 'exec')
    instructions = list(dis.get_instructions(native_code))

    pprint(instructions)

    generated_code = Code(instructions=list(convert(instructions)))

    visualize(generated_code._cfg)  # pylint: disable=protected-access
