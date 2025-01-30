import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os

project_directory = "<name_of_your_project_directory>" ### <--- change this to the name of your project folder to include

class FileTreeApp:
    def __init__(self, root, base_path):
        self.root = root
        self.base_path = Path(base_path)
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill='both')
        self.selected_items = set()
        self.item_sizes = {}

        # Load exclusions from exclude.py if available
        self.exclude_patterns = self.load_exclusions()

        # Calculate total size excluding pre-selected items
        self.total_size = self.calculate_total_size(self.base_path)
        self.selected_size = self.calculate_selected_size()
        self.remaining_size = self.total_size - self.selected_size

        self.populate_tree(self.base_path, "")

        self.tree.bind("<Button-1>", self.on_item_click)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', padx=5, pady=5)

        self.size_label = tk.Label(btn_frame, text=f"Total Size: {self.remaining_size} bytes")
        self.size_label.pack(side='left')

        save_btn = tk.Button(btn_frame, text="Save Exclusions", command=self.save_exclusions)
        save_btn.pack(side='right')

    def load_exclusions(self):
        # Check if exclude.py exists and load it
        if os.path.exists('exclude.py'):
            exclude_globals = {}
            with open('exclude.py', 'r') as f:
                exec(f.read(), exclude_globals)
            exclude_patterns = exclude_globals.get('exclude_patterns', [])
            self.selected_items.update(exclude_patterns)
            return exclude_patterns
        return []

    def should_exclude(self, path):
        # Check if the path matches any of the exclude patterns
        return any(str(path).startswith(pattern) for pattern in self.exclude_patterns)

    def populate_tree(self, path, parent):
        for p in path.iterdir():
            if "checkpoint" in p.name:
                self.selected_items.add(str(p))  # Automatically select checkpoint items
                continue  # Skip adding to the tree

            if p.is_file():
                size = p.stat().st_size
                size_text = f" ({size} bytes)"
            else:
                size = 0
                size_text = ""

            self.item_sizes[str(p)] = size
            node = self.tree.insert(parent, 'end', text=p.name + size_text, open=True)
            if str(p) in self.selected_items:
                self.tree.item(node, tags=('selected',))  # Highlight if in selected items

            if p.is_dir():
                self.populate_tree(p, node)

        self.tree.tag_configure('selected', background='lightblue')

    def calculate_total_size(self, path):
        # Calculate the total size, excluding already excluded items
        return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not self.should_exclude(p))

    def calculate_selected_size(self):
        # Calculate the size of the pre-selected items
        return sum(self.item_sizes[item] for item in self.selected_items if item in self.item_sizes)

    def on_item_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.toggle_selection(item_id)

    def toggle_selection(self, item):
        item_path = self.get_full_path(item)
        if item_path in self.selected_items:
            self.deselect_item(item)
        else:
            self.select_item(item)
        self.update_tree_selection()
        self.update_remaining_size()

    def select_item(self, item):
        item_path = self.get_full_path(item)
        if item_path not in self.selected_items:
            self.selected_items.add(item_path)
            self.selected_size += self.item_sizes.get(item_path, 0)
        for child in self.tree.get_children(item):
            self.select_item(child)

    def deselect_item(self, item):
        item_path = self.get_full_path(item)
        if item_path in self.selected_items:
            self.selected_items.remove(item_path)
            self.selected_size -= self.item_sizes.get(item_path, 0)
        for child in self.tree.get_children(item):
            self.deselect_item(child)

    def update_tree_selection(self):
        for item in self.tree.get_children(''):
            self.update_item_color(item)

    def update_item_color(self, item):
        item_path = self.get_full_path(item)
        if item_path in self.selected_items:
            self.tree.item(item, tags=('selected',))
        else:
            self.tree.item(item, tags=())

        for child in self.tree.get_children(item):
            self.update_item_color(child)

    def get_full_path(self, item):
        path_parts = []
        while item:
            path_parts.insert(0, self.tree.item(item, 'text').split(' (')[0])
            item = self.tree.parent(item)
        return str(self.base_path.joinpath(*path_parts))

    def update_remaining_size(self):
        self.remaining_size = self.total_size - self.selected_size
        self.size_label.config(text=f"Total Size: {self.remaining_size} bytes")

    def save_exclusions(self):
        with open('exclude.py', 'w') as f:
            f.write("# Excluded files and directories\n")
            f.write("exclude_patterns = [\n")
            for item in sorted(self.selected_items):
                f.write(f"    '{item}',\n")
            f.write("]\n")
        print("Exclusions saved to exclude.py")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Exclusion Tool")
    root.lift()
    root.attributes('-topmost', True)
    root.geometry("800x600")

    style = ttk.Style()
    style.configure('Treeview', rowheight=25)

    app = FileTreeApp(root, project_directory)  # Replace with your actual directory

    root.mainloop()
