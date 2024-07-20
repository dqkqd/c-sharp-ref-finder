import dataclasses
import itertools
from typing import Generator

import tree_sitter_c_sharp as cspython
from tree_sitter import Language, Node, Parser

CS_LANGUAGE = Language(cspython.language())
parser = Parser(CS_LANGUAGE)

source_code = """using System;

namespace HelloWorld
{
  class Program
  {
    static void ModifyVariable(int x, int y) { x += 1; y += 2}
    static void ModifyVariableNested(int x) { int y = 2; ModifyVariable(x, y); }
    static void Main(string[] args)
    {
      Console.WriteLine("Hello World!");    
   }
  }
}
"""


def get_node_text_name(node: Node) -> str | None:
    if node.text is None:
        return None
    return node.text.decode("utf-8")


@dataclasses.dataclass
class Identifier:
    name: str | None
    row: int
    column: int

    @classmethod
    def from_node(cls, node: Node) -> "Identifier":
        return cls(
            name=get_node_text_name(node),
            row=node.end_point.row,
            column=node.end_point.column,
        )


@dataclasses.dataclass
class Function:
    node: Node

    @property
    def identifier(self) -> Identifier:
        name_node = self.node.child_by_field_name("name")
        if name_node is None:
            raise ValueError(f"Invalid function: {self}")
        return Identifier.from_node(name_node)

    @property
    def parameter_identifiers(self) -> list[Identifier]:
        def identifier_from_parameters(parameters_node: Node) -> list[Identifier]:
            identifiers: list[Identifier] = []
            for parameter in parameters_node.children:
                identifiers.extend(
                    map(Identifier.from_node, parameter.children_by_field_name("name"))
                )
            return identifiers

        all_param_names = map(
            identifier_from_parameters,
            self.node.children_by_field_name("parameters"),
        )
        parameter_names = list(itertools.chain(*all_param_names))
        return parameter_names

    @classmethod
    def functions_from_node(cls, node: Node) -> list["Function"]:
        function_nodes = get_all_descendant_with_node_type(node, 'method_declaration')
        functions = [Function(node=n) for n in function_nodes]
        return functions


def get_root_node_from_source(source: str) -> Node:
    tree = parser.parse(bytes(source, "utf-8"))
    return tree.root_node


def get_all_descendant_with_node_type(node: Node, node_type: str) -> Generator[Node, None, None]:
    if node.type == node_type:
        yield node
    for child in node.children:
        yield from get_all_descendant_with_node_type(child, node_type)


if __name__ == "__main__":
    node = get_root_node_from_source(source_code)
    functions = Function.functions_from_node(node)
