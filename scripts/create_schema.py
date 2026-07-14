import ast
import argparse

from ocrit.schema import SchemaGenerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a schema from a PDF")
    parser.add_argument("pdf", type=str, help="The path to the PDF file")
    parser.add_argument("--output", type=str, help="The path to the output file")
    parser.add_argument("--schema-name", type=str, help="The name of the schema")
    args = parser.parse_args()

    generator = SchemaGenerator()
    module = generator.create_ast(args.pdf, schema_name=args.schema_name)
    with open(args.output, "w") as f:
        f.write(ast.unparse(module))
