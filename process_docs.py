import os
import re

INPUT_DIR = "."
OUTPUT_BASE = "processed_docs"

os.makedirs(OUTPUT_BASE, exist_ok=True)

def clean_filename(name):
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^\w\-_.]", "", name)[:80]

def split_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"\n##\s+", content)

    results = []
    for section in sections:
        if not section.strip():
            continue

        lines = section.split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:])

        results.append({
            "title": title,
            "content": f"## {title}\n{body}"
        })

    return results


def extract_engineering_values(text):
    patterns = {
        "airflow": r"\d+(\.\d+)?\s*l/s/?person",
        "co2": r"\d+\s*ppm",
        "temperature": r"\d+\s*°C",
    }

    extracted = {}

    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            extracted[key] = list(set(matches))

    return extracted


def process_file(md_file):
    base_name = os.path.splitext(os.path.basename(md_file))[0]
    output_dir = os.path.join(OUTPUT_BASE, base_name)

    os.makedirs(output_dir, exist_ok=True)

    sections = split_markdown(md_file)

    knowledge_summary = [f"# Extracted Engineering Data: {base_name}\n"]

    for section in sections:
        filename = clean_filename(section["title"])
        output_path = os.path.join(output_dir, f"{filename}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(section["content"])

        values = extract_engineering_values(section["content"])

        if values:
            knowledge_summary.append(f"## {section['title']}")
            for key, vals in values.items():
                for v in vals:
                    knowledge_summary.append(f"- {key}: {v}")
            knowledge_summary.append("")

    summary_path = os.path.join(output_dir, "engineering_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(knowledge_summary))


def main():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".md") and file not in ["index.md"]:
            process_file(os.path.join(INPUT_DIR, file))


if __name__ == "__main__":
    main()
