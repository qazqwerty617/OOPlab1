from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

VIEW_DIR = Path(__file__).resolve().parent / "views"

env = Environment(
    loader=FileSystemLoader(VIEW_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

def render(template: str, **context) -> bytes:
    return env.get_template(template).render(**context).encode("utf-8")
