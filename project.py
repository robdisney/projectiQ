import asyncio
import subprocess
from openai import AsyncOpenAI
from openaicreds import key, model
from pathlib import Path

# Import the exclude patterns
from exclude import exclude_patterns

client = AsyncOpenAI(api_key=key)

async def generate_response(prompt):
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=4000,
        temperature=0.5,
        stream=True
    )

    async for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end='', flush=True)

def should_exclude(path, exclude_patterns):
    # Check if the path matches any of the exclude patterns
    for pattern in exclude_patterns:
        if str(path).startswith(pattern):
            return True
    return False

def get_tree_and_files_contents(target_dir):
    # Get the tree structure of the target directory
    tree_output = subprocess.run(['tree', target_dir], capture_output=True, text=True).stdout
    tree = f"tree {target_dir}: " + tree_output

    # Read all files in the directory tree
    files_contents = []
    for path in Path(target_dir).rglob('*'):
        if path.is_file() and not should_exclude(path, exclude_patterns):
            try:
                file_content = path.read_text(encoding='utf-8')  # Specify encoding here
            except UnicodeDecodeError:
                # Handle the error, e.g., log the issue and skip the file
                print(f"Skipping file due to encoding error: {path}")
                continue
            files_contents.append(f"{path}: {file_content}")

    return tree, files_contents

async def main():
    # Read the initial prompt from doc.txt
    doc = Path('project.txt').read_text(errors="ignore")

    # Specify the target directory
    target_dir = 'project' # change this to your desired target project directory

    # Get the tree and files contents
    tree, files_contents = get_tree_and_files_contents(target_dir)

    # Debug -- uncomment if needed
    print(doc)
    print(tree)
    print(files_contents)
    
    # Combine all parts of the question
    question = doc + "\n" + tree + "\n" + "\n".join(files_contents)

    print("\n")
    await generate_response(question)

if __name__ == "__main__":
    asyncio.run(main())
    print("\n")
