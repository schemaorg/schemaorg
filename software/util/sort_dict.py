from __future__ import annotations

from typing import Any
from xml.dom import minidom
from xml.etree import ElementTree

KEY_ORDER: tuple[str, ...] = ("@context", "@id", "@type")
_KEY_RANK: dict[str, int] = {k: i for i, k in enumerate(KEY_ORDER)}
_RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
_RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"


def sort_xml(xml_input: str | ElementTree.Element) -> str:
    """Sort children of an XML element for deterministic output.

    If the input is a string, it will be parsed as an XML Element.
    Returns a formatted XML string.
    """
    if isinstance(xml_input, str):
        root = ElementTree.fromstring(xml_input)
    elif isinstance(xml_input, ElementTree.Element):
        root = xml_input
    else:
        raise TypeError(f"Expected str or ElementTree.Element, got {type(xml_input)}")

    def get_key(elem: ElementTree.Element) -> tuple[str, str, str]:
        if about := (elem.get(_RDF_ABOUT) or elem.get("about")):
            return (about, "", "")
        tag = elem.tag
        if resource := (elem.get(_RDF_RESOURCE) or elem.get("resource")):
            return (tag, resource, "")
        return (tag, "", ElementTree.tostring(elem, encoding="unicode"))

    def recursive_sort(element: ElementTree.Element) -> None:
        if not len(element):
            return
        element[:] = sorted(element, key=get_key)
        for child in element:
            recursive_sort(child)

    recursive_sort(root)
    pretty_xml = (
        minidom.parseString(ElementTree.tostring(root))
        .toprettyxml(encoding="UTF-8")
        .decode()
    )
    lines = [line.rstrip() for line in pretty_xml.splitlines() if line.strip()]
    return '\n'.join(lines) + '\n'


def universal_sort_key(item: tuple[str, Any]) -> tuple[int, str]:
    """Sort key for dictionary items (k, v)."""
    k, v = item
    if (rank := _KEY_RANK.get(k)) is not None:
        return (rank, k)
    if k.startswith("@"):
        return (len(KEY_ORDER), k)
    if isinstance(v, (str, bytes, bool, int, float)) or v is None:
        return (len(KEY_ORDER) + 1, k)
    return (len(KEY_ORDER) + 2, k)


def list_sort_key(item: Any) -> str:
    """Sort key for list items."""
    if isinstance(item, dict):
        return str(item.get("@id", item.get("@type", str(item))))
    return str(item)


def sort_dict(data: Any) -> Any:
    """Recursively sort dictionary keys and list elements for predictability."""
    if isinstance(data, dict):
        try:
            sorted_items = sorted(data.items(), key=universal_sort_key)
            return {k: sort_dict(v) for k, v in sorted_items}
        except Exception:
            return {k: sort_dict(v) for k, v in data.items()}

    if isinstance(data, list):
        try:
            sorted_list = sorted(data, key=list_sort_key)
            return [sort_dict(i) for i in sorted_list]
        except Exception:
            return [sort_dict(i) for i in data]

    return data
