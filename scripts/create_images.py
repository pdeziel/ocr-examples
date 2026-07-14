import argparse
import importlib

from ocrit.generator import DocumentGenerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create example images from a schema and PDF template"
    )
    parser.add_argument("schema", type=str, help="The name of the schema")
    parser.add_argument("template", type=str, help="The path to the PDF template file")
    parser.add_argument("output", type=str, help="The path to the output directory")
    parser.add_argument(
        "--json-dir", type=str, help="The path to the output JSON directory"
    )
    parser.add_argument(
        "--num-examples", type=int, default=10, help="The number of examples to create"
    )
    parser.add_argument(
        "--random-seed", type=int, default=None, help="The random seed to use"
    )
    args = parser.parse_args()

    module, schema_name = args.schema.rsplit(".", 1)
    schema_class = getattr(importlib.import_module(module), schema_name)
    generator = DocumentGenerator(args.template)
    generator.generate_images(
        schema_class,
        args.output,
        args.json_dir,
        args.num_examples,
        args.random_seed,
    )

    print(f"Created {args.num_examples} images in {args.output}")
    print(f"Created {args.num_examples} JSON files in {args.json_dir}")
