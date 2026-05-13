import os
import posixpath
from bs4 import BeautifulSoup

NOTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes")


def get_note_title(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        tag = soup.find("title")
        if tag:
            return tag.get_text().strip()
    except OSError:
        pass
    return os.path.splitext(os.path.basename(file_path))[0]


def _find_dir_index(dir_path: str, dir_name: str) -> str | None:
    for candidate in [f"{dir_name}.html", "index.html"]:
        if os.path.exists(os.path.join(dir_path, candidate)):
            return candidate
    return None


def _scan_dir(dir_path: str, rel_prefix: str, dir_index_name: str | None) -> list:
    nodes = []
    try:
        entries = sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name.lower()))
    except OSError:
        return []

    for entry in entries:
        if entry.name.startswith("_"):
            continue

        if entry.is_dir(follow_symlinks=False):
            child_rel = f"{rel_prefix}/{entry.name}".lstrip("/")
            child_index = _find_dir_index(entry.path, entry.name)
            note_path = f"{child_rel}/{child_index}".replace("\\", "/") if child_index else None
            title = get_note_title(os.path.join(entry.path, child_index)) if child_index else entry.name
            children = _scan_dir(entry.path, child_rel, child_index)
            nodes.append({
                "title": title,
                "path": note_path,
                "dir_path": child_rel.replace("\\", "/"),
                "type": "dir",
                "children": children,
            })

        elif entry.is_file() and entry.name.endswith(".html") and entry.name != dir_index_name:
            file_rel = f"{rel_prefix}/{entry.name}".lstrip("/").replace("\\", "/")
            title = get_note_title(entry.path)
            nodes.append({
                "title": title,
                "path": file_rel,
                "type": "file",
                "children": [],
            })

    return nodes


def scan_notes_tree() -> list:
    if not os.path.exists(NOTES_DIR):
        return []
    return _scan_dir(NOTES_DIR, "", None)


def _flatten(tree: list) -> list:
    result = []
    for node in tree:
        if node["path"]:
            result.append({"title": node["title"], "path": node["path"]})
        result.extend(_flatten(node["children"]))
    return result


def get_folder_children(folder_rel_path: str) -> tuple[str, str | None, list]:
    """Returns (title, note_path_or_None, children) for a folder inside NOTES_DIR."""
    folder_abs = os.path.join(NOTES_DIR, folder_rel_path)
    folder_name = os.path.basename(folder_abs.rstrip("/\\"))
    index_file = _find_dir_index(folder_abs, folder_name)
    rel = folder_rel_path.replace("\\", "/")
    note_path = f"{rel}/{index_file}" if index_file else None
    title = get_note_title(os.path.join(folder_abs, index_file)) if index_file else folder_name
    children = _scan_dir(folder_abs, rel, index_file)
    return title, note_path, children


def search_notes(query: str) -> list:
    q = query.lower()
    return [n for n in _flatten(scan_notes_tree()) if q in n["title"].lower()]


def _resolve_url(relative: str, note_dir: str) -> str:
    if not relative or relative.startswith(("http://", "https://", "/", "#", "data:")):
        return relative
    if note_dir:
        return posixpath.normpath(f"{note_dir}/{relative}")
    return posixpath.normpath(relative)


def get_note_content(file_path: str, note_rel_path: str) -> tuple[str, str]:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except FileNotFoundError:
        return "Not Found", "<p>Note not found.</p>"
    except OSError as e:
        return "Error", f"<p>Could not read note: {e}</p>"

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else os.path.splitext(os.path.basename(file_path))[0]

    styles = "".join(str(s) for s in soup.find_all("style"))

    body = soup.find("body")
    body_html = body.decode_contents() if body else str(soup)

    note_dir_rel = posixpath.dirname(note_rel_path.replace("\\", "/"))

    body_soup = BeautifulSoup(body_html, "html.parser")

    for tag in body_soup.find_all(src=True):
        src = tag["src"]
        if not src.startswith(("http://", "https://", "/", "data:")):
            tag["src"] = "/notes-files/" + _resolve_url(src, note_dir_rel)

    for a in body_soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith(("http://", "https://", "/", "#")):
            resolved = _resolve_url(href, note_dir_rel)
            a["href"] = "/notes/" + resolved if href.endswith(".html") else "/notes-files/" + resolved

    return title, styles + str(body_soup)
