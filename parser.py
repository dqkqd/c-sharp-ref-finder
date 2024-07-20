import dataclasses
import itertools

import tree_sitter_c_sharp as cspython
from tree_sitter import Language, Node, Parser, Tree

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


def get_all_identifiers_from_parameters(parameters_node: Node) -> list[Identifier]:
    identifiers: list[Identifier] = []
    for parameter in parameters_node.children:
        name_nodes = parameter.children_by_field_name("name")
        identifiers.extend(map(Identifier.from_node, name_nodes))
    return identifiers


def get_all_parameter_identifiers_from_function(function: Node) -> list[Identifier]:
    all_param_names = map(
        get_all_identifiers_from_parameters,
        function.children_by_field_name("parameters"),
    )
    parameter_names = list(itertools.chain(*all_param_names))
    return parameter_names


def get_all_variables_from_function(function: Node) -> list[Identifier]:
    return []


def get_function_identifier(function: Node) -> Identifier:
    name_node = function.child_by_field_name("name")
    assert name_node is not None
    return Identifier.from_node(name_node)


def get_function_with_ref_from_node(node: Node):
    for child in node.children:
        if child.type == "method_declaration":
            print("--------------------")
            print(get_function_identifier(child))
            print(get_all_parameter_identifiers_from_function(child))
            print(get_all_variables_from_function(child))
        get_function_with_ref_from_node(child)


def get_function_with_ref(source: str) -> Tree:
    tree = parser.parse(bytes(source, "utf-8"))
    root_node = tree.root_node
    get_function_with_ref_from_node(root_node)
    return tree


get_function_with_ref(source_code)
