import argparse
from pathlib import Path
from dotenv import load_dotenv

from ocrit.document import Document
from ocrit.pipeline import Pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a pipeline on a document or set of documents"
    )
    parser.add_argument("config", type=str, help="The path to the pipeline config file")
    parser.add_argument(
        "--id", type=str, help="The ID of the document to run the pipeline on"
    )
    parser.add_argument(
        "--documents",
        type=str,
        help="The path to the directory containing the JSON documents",
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    pipeline = Pipeline(args.config)

    if args.id:
        document = Document(
            img_path=f"data/images/{args.id}.png", json_path=f"data/json/{args.id}.json"
        )
        pipeline.run(document)
    elif args.documents:
        documents = []
        for json_path in Path(args.documents).glob("*.json"):
            id = json_path.stem
            documents.append(
                Document(img_path=f"data/images/{id}.png", json_path=str(json_path))
            )
        pipeline.run_many(documents)
    print(f"Pipeline completed successfully")
