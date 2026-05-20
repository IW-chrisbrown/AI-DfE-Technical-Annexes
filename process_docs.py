import os
import re

INPUT_DIR = "."
OUTPUT_BASE = "processed_docs"

# Create output base directory
os.makedirs(OUTPUT_BASE, exist_ok=True)

def clean_filename(name):
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^\w\-_.]", "", name)
    return name[:80]

def split_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by H2 headings
    sections = re.split(r"\n##\s+", content)

    results = []

    for section in sections:
        if len(section.strip()) == 0:
            continue

        lines = section.split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:])

        filename = clean_filename(title)

        results.append({
            "title": title,
            "content": f"## {title}\n{body}"
        })

    return results


def extract_key_values(text):
    """Simple pattern extraction for engineering values"""
    patterns = [
        r"\d+\s*l/s/?person",
        r"\d+\s*ppm",
        r"\d+\s*°C",
        r"\d+\s*\%",
    ]

    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)

    return list(set(found))


def process_file(md_file):
    base_name = os.path.splitext(os.path.basename(md_file))[0]
    output_dir = os.path.join(OUTPUT_BASE, base_name)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Processing: {md_file}")

    sections = split_markdown(md_file)

    summary_lines = [f"# Summary: {base_name}\n"]

    for section in sections:
        safe_name = clean_filename(section["title"])
        output_path = os.path.join(output_dir, f"{safe_name}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(section["content"])

        # Extract key engineering values
        values = extract_key_values(section["content"])
        if values:
            summary_lines.append(f"## {section['title']}")
            for v in values:
                summary_lines.append(f"- {v}")
            summary_lines.append("")

    # Write summary
    summary_path = os.path.join(output_dir, "summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))


def main():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".md") and file != "index.md":
            process_file(os.path.join(INPUT_DIR, file))


if __name__ == "__main__":
    main()
