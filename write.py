#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()
import sys
from pathlib import Path
from src.writer import create_article


def read_guidelines_from_stdin():
    """Read content guidelines from stdin until EOF (Ctrl+D)"""
    print("Enter content guidelines (one per line, Ctrl+D when done):")
    guidelines = []
    try:
        while True:
            line = input().strip()
            if line:  # Only add non-empty lines
                guidelines.append(line)
    except EOFError:
        pass
    return guidelines if guidelines else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python write.py <topic> [output.md]")
        sys.exit(1)

    try:
        topic = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "output.md"

        # Read guidelines from stdin if available
        content_guidelines = read_guidelines_from_stdin()

        article_content = create_article(topic, content_guidelines)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(article_content)

        print(f"\nArticle written successfully to: {output_file}")

    except Exception as e:
        import traceback

        print(f"Error creating article: {str(e)}")
        print("\nStack trace:")
        print(traceback.format_exc())
        sys.exit(1)
