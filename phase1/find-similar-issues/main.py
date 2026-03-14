import subprocess
import sys


def run_step(module_name: str):
    """Run a python module and stop if it fails."""
    print(f"\n=== Running: {module_name} ===")

    result = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd="src"
    )

    if result.returncode != 0:
        print(f"❌ Error while running {module_name}")
        sys.exit(result.returncode)

    print(f"✅ Finished: {module_name}")


def main():
    pipeline = [
        "convert.csv2json",
        "convert.json2jsonRAG",
        "embedding.embedding",
        "rag.rag_demo",
    ]

    for module in pipeline:
        run_step(module)

    print("\n🎉 Pipeline completed successfully")


if __name__ == "__main__":
    main()