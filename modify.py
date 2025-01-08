#!/usr/bin/env python3
import sys
from pathlib import Path
from src.modifier import modify_article

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python modify.py <article.md> "modification instructions"')
        sys.exit(1)

    article_path = Path(sys.argv[1])
    if not article_path.exists():
        print(f"Error: File {article_path} not found")
        sys.exit(1)

    instructions = sys.argv[2]

    try:
        # Create backup of original file
        backup_path = article_path.with_suffix(".md.backup")
        if not backup_path.exists():
            with open(backup_path, "w", encoding="utf-8") as f:
                with open(article_path, "r", encoding="utf-8") as orig:
                    f.write(orig.read())

        # Modify and save the article
        modified_content = modify_article(article_path, instructions)
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

        print(f"\nArticle modified successfully!")
        print(f"Original content backed up to: {backup_path}")
    except Exception as e:
        print(f"Error modifying article: {e}")
        sys.exit(1)
