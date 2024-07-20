import dataclasses
import itertools
from typing import ClassVar, Generator

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
class FunctionBody:
    node: Node
    MODIFIER_FIELD_TYPE: ClassVar[list[str]] = ["expression_statement"]

    @property
    def maybe_modified_identifiers(self) -> list[Identifier]:
        maybe_modified_nodes = itertools.chain(
            get_all_descendant_with_node_type(self.node, "assignment_expression"),
            get_all_descendant_with_node_type(self.node, "declaration_expression"),
        )
        identifiers: list[Identifier] = []
        for node in maybe_modified_nodes:
            left = node.child_by_field_name('left')
            if left is None:
                raise ValueError(f"Left hand side doesn't found for {left}")
            identifiers.append(Identifier.from_node(left))
        return identifiers


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

    @property
    def function_body(self) -> FunctionBody:
        body = self.node.child_by_field_name("body")
        if body is None:
            raise ValueError(f"Function body does not exist {self}")
        return FunctionBody(node=body)

    def find_all_ref(self):
        modified_identifiers = self.function_body.maybe_modified_identifiers
        modified_names = set(ident.name for ident in modified_identifiers)
        print(modified_names)
        for param in self.parameter_identifiers:
            if param.name in modified_names:
                print(param)
        return None

    @classmethod
    def functions_from_node(cls, node: Node) -> list["Function"]:
        function_nodes = get_all_descendant_with_node_type(node, "method_declaration")
        functions = [Function(node=n) for n in function_nodes]
        return functions


def get_root_node_from_source(source: str) -> Node:
    tree = parser.parse(bytes(source, "utf-8"))
    return tree.root_node


def get_all_descendant_with_node_type(
    node: Node, node_type: str
) -> Generator[Node, None, None]:
    if node.type == node_type:
        yield node
    for child in node.children:
        yield from get_all_descendant_with_node_type(child, node_type)


if __name__ == "__main__":
    node = get_root_node_from_source(source_code)
    functions = Function.functions_from_node(node)
    for function in functions:
        function.find_all_ref()
