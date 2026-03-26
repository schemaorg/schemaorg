#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom import minidom
from xml.etree import ElementTree

KEY_ORDER = ["@context", "@id", "@type"]


def sort_xml(xml_input):
    """Sorts children of an XML element for deterministic output.

    If the input is a string, it will be parsed as an XML Element.
    The function returns a formatted XML string.
    """
    if isinstance(xml_input, str):
        root = ElementTree.fromstring(xml_input)
    elif isinstance(xml_input, ElementTree.Element):
        root = xml_input
    else:
        raise TypeError(f"Expected str or ElementTree.Element, got {type(xml_input)}")

    def get_key(elem):
        # We look for rdf:about or about attribute
        about = elem.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about") or elem.get("about")
        if about:
            return (about, "", "")
        # Fallback to tag name (primary) and resource or string representation (secondary)
        tag = elem.tag
        resource = elem.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource") or elem.get("resource")
        if resource:
            return (tag, resource, "")
        return (tag, "", ElementTree.tostring(elem, encoding="unicode"))

    def recursive_sort(element):
        children = list(element)
        if not children:
            return
        children.sort(key=get_key)
        for child in list(element):
            element.remove(child)
        for child in children:
            element.append(child)
            recursive_sort(child)

    recursive_sort(root)

    pretty_xml = (
        minidom.parseString(ElementTree.tostring(root))
        .toprettyxml(encoding="UTF-8")
        .decode()
    )

    # Filter out empty lines and strip trailing whitespace from each line
    lines = [line.rstrip() for line in pretty_xml.splitlines() if line.strip()]

    return "\n".join(lines) + "\n"


def universal_sort_key(item):

    """Sort key for dictionary items (k, v).

    Returns a priority rank and the key name itself.
    """
    k, v = item
    if k in KEY_ORDER:
        return (KEY_ORDER.index(k), k)
    if k.startswith("@"):
        return (len(KEY_ORDER), k)
    if isinstance(v, (str, bytes, bool, int, float)) or v is None:
        return (len(KEY_ORDER) + 1, k)
    return (len(KEY_ORDER) + 2, k)


def list_sort_key(item):
    """Sort key for list items."""
    if isinstance(item, dict):
        # Prefer sorting by @id, then @type, then string representation
        return str(item.get("@id", item.get("@type", str(item))))
    return str(item)


def sort_dict(data):
    """Recursively sort dictionary keys and list elements for predictability.

    Uses universal_sort_key for dictionaries. 
    Sorts all lists for determinism, using list_sort_key for elements.
    """
    if isinstance(data, dict):
        try:
            # Sort keys based on universal priorities
            sorted_items = sorted(data.items(), key=universal_sort_key)
            return {k: sort_dict(v) for k, v in sorted_items}
        except Exception:
            # Fallback to original order if sorting fails
            return {k: sort_dict(v) for k, v in data.items()}

    elif isinstance(data, list):
        try:
            # Process items in the list and sort them
            # Sorting all lists ensures 100% determinism.
            sorted_list = sorted(data, key=list_sort_key)
            return [sort_dict(i) for i in sorted_list]
        except Exception:
            # Fallback: process items without sorting if not comparable
            return [sort_dict(i) for i in data]

    return data
