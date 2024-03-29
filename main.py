import sys
from pathlib import Path
import shutil
import re
from threading import Thread, RLock

CATEGORIES = {"Audio": [".mp3", ".wav", ".flac", ".wma"],
              "Docs": [".docx", ".txt", ".pdf"],
              "Images": ['.jpeg', '.png', '.jpg', '.svg'],
              "Archives": ['.zip', '.gz', '.tzr'],
              "Video": ['.avi', '.mp4', '.mov', '.mkv'],
              "Unknown": []
              }

known_list = set()
unknown_list = set()

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def normalize(file_name):
    file_name_root = file_name.stem
    suffix = file_name.suffix
    changed_file_name = file_name_root
    changed_file_name = re.sub(r"\W", "_", file_name_root)
    transliterated_name = ''.join(
        [TRANS.get(ord(c), c) for c in changed_file_name])
    return transliterated_name+suffix


def check_parent_empty(parent: Path):
    # Check if the parent directory exists
    if parent.exists():
        if not any(parent.iterdir()):
            parent.rmdir()
            # Ensure it doesn't go beyond the root directory
            if parent != Path(sys.argv[1]):
                check_parent_empty(parent.parent)
    else:
        return         # If the parent directory doesn't exist, no need to continue


def get_categories(file: Path) -> str:
    ext = file.suffix.lower()

    category_found = None
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            known_list.add(ext)
            category_found = cat
            break
    if not category_found:
        unknown_list.add(ext)

    return category_found or "Unknown"


def create_file_category(file: Path, category: str, dir: Path) -> None:
    target_dir = dir.joinpath(category)
    # Create dir if doesn't exist
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)


def rename_and_move_file(file: Path, category: str, dir: Path) -> None:
    target_dir = dir.joinpath(category)
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    if file.exists():
        if category == "Unknown":
            new_path = target_dir / file.name
        else:
            normalized_name = normalize(file)
            new_path = target_dir / normalized_name
        counter = 1
        extension = file.suffix
        while new_path.exists():
            base_name = file.stem
            new_name = f"{base_name}_{counter}{extension}"
            new_path = target_dir / new_name
            counter += 1
        # Rename (or move) the file to the target directory
        file.rename(new_path)
    else:
        print(f"File not found: {file}")


def archive_unpack(file: Path, dir: Path):
    try:
        shutil.unpack_archive(str(file), dir.joinpath(file.stem))
    except shutil.ReadError:
        print(f"Unable to unpack {file}. It may not be a valid archive.")


# Reentrant lock for synchronization
lock = RLock()
threads = []


def sort_folder(path: Path) -> None:
    known_extensions = set()
    unknown_extensions = set()

    # Move&rename files to appropriate categories
    for element in path.rglob("*"):
        if element.is_file():
            category = get_categories(element)
            create_file_category(element, category, path)
            if category == "Archives":
                archive_unpack(element, path.joinpath("Archives"))
            rename_and_move_file(element, category, path)

            # Update known_extensions and unknown_extensions
            if category != "Unknown":
                with lock:
                    known_extensions.add(element.suffix.lower())
            else:
                with lock:
                    unknown_extensions.add(element.suffix.lower())
        elif element.is_dir():
            thread_dir = Thread(target=sort_folder, args=(element,))
            threads.append(thread_dir)

    # Recursively sort subdirectories
    for sub_dir in path.iterdir():
        if sub_dir.is_dir():
            sort_folder(sub_dir)

    # Update global known_list and unknown_list after processing
    with lock:
        known_list.update(known_extensions)
        unknown_list.update(unknown_extensions)

    # Remove empty directories
    for element in path.iterdir():
        if element.is_dir() and not any(element.iterdir()):
            element.rmdir()
            check_parent_empty(element.parent)


def main() -> str:
    try:
        path = Path(sys.argv[1])
    except IndexError:
        return "No path to folder"

    if not path.exists():
        return "Folder does not exist"

    thread = Thread(target=sort_folder, args=(path,))
    thread.start()
    for t in threads:
        t.join()
    thread.join()

    print(f"Known extensions: {known_list}")
    print(f"Unknown extensions: {unknown_list}")

    return "All Ok"


if __name__ == '__main__':
    main()
