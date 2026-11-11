#!/usr/bin/env python3
"""Convert Data Commons MCF definitions into Schema.org Turtle.

Example input:

Node: dcid:medicalSubjectHeadingSupplementaryRecordID
name: "medicalSubjectHeadingSupplementaryRecordID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHSupplementaryRecord, schema:Text
domainIncludes: dcs:ChemicalCompound, dcs:MeSHSupplementaryRecord
description: "A unique ID for a Medical Subject Heading supplementary record."
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import re
import sys

from schemaorg import constants
from schemaorg.sdo_uri import SdoUri

DEBUG: bool = False

PENDING_URI: str = str(SdoUri.for_layer("pending"))

TURTLE_PREFIXES: str = f"""@prefix : <{constants.SCHEMA_URI}> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dcs: <https://datacommons.org/schema/> ."""

_CORE_SCALARS: frozenset[str] = frozenset({":Boolean", ":Text", ":Number"})
_BLANK_BLOCK_RE = re.compile(r"\n\s*\n")

McfNode = dict[str, dict[str, str]]


def mcf_to_dict_list(mcf_str: str) -> list[McfNode]:
    """Parse MCF text into a list of node property dictionaries."""
    node_list: list[McfNode] = []

    for block in _BLANK_BLOCK_RE.split(mcf_str):
        block = block.strip()
        if not block:
            continue

        cur_node: McfNode = {}
        is_first_prop = True
        for raw_line in block.splitlines():
            pv_str = raw_line.strip()
            if not pv_str or pv_str.startswith("#"):
                continue
            if is_first_prop:
                is_first_prop = False
                if not pv_str.startswith("Node:"):
                    raise ValueError(f'Missing "Node: <name>" in MCF node {block}')
            if ":" not in pv_str:
                raise ValueError(f"Malformed MCF line (missing ':'): {pv_str}")

            prop, raw_val = (part.strip() for part in pv_str.split(":", 1))
            if (
                not raw_val.startswith('"')
                and "," not in raw_val
                and ":" in raw_val
            ):
                ns_prefix, local_val = (
                    part.strip() for part in raw_val.split(":", 1)
                )
            else:
                ns_prefix, local_val = "", raw_val

            cur_node[prop] = {
                "namespace": ns_prefix,
                "value": local_val,
                "raw": raw_val,
            }

        if cur_node:
            node_list.append(cur_node)

    return node_list


my_mcf_to_dict_list = mcf_to_dict_list


def get_pv(node: McfNode, property_name: str) -> str:
    return node.get(property_name, {}).get("value", "").strip('"')


def debug_print(message: str) -> None:
    if DEBUG:
        print(f"# DEBUG: {message}")


def multiprop(node: McfNode, property_name: str) -> list[str]:
    """Return sorted multi-valued property tokens (e.g. domainIncludes)."""
    entry = node.get(property_name)
    if not entry:
        return []
    raw = entry.get("raw") or entry.get("value", "")
    return sorted({pv.strip() for pv in raw.split(",") if pv.strip()})


def format_turtle_term(raw_term: str) -> str:
    """Format an MCF term reference as a valid Turtle prefixed name."""
    term = raw_term.strip()
    if ":" in term:
        ns_prefix, local_name = (part.strip() for part in term.split(":", 1))
        if ns_prefix in ("", "schema", "dcid"):
            return f":{local_name}"
        return f"{ns_prefix}:{local_name}"
    return f":{term}"


def generate_class_turtle(
    node: McfNode, terms: dict[str, set[str]]
) -> str:
    local_id = node["Node"]["value"]
    debug_print(f"Generating Turtle for class node: {local_id}")
    node_id = format_turtle_term(local_id)
    terms["types"].add(node_id)

    lines = [
        node_id,
        "  a rdfs:Class ;",
        f"  :isPartOf <{PENDING_URI}> ;",
    ]

    for super_class in multiprop(node, "subClassOf"):
        formatted = format_turtle_term(super_class)
        terms["types"].add(formatted)
        lines.append(f"  rdfs:subClassOf {formatted} ;")

    if name_value := get_pv(node, "name"):
        lines.append(f'  rdfs:label "{name_value}" ;')
    if description_value := get_pv(node, "description"):
        lines.append(f'  rdfs:comment """{description_value}""" ;')

    lines[-1] = f"{lines[-1][:-1]}."
    return "\n".join(lines)


def generate_property_turtle(
    node: McfNode, terms: dict[str, set[str]]
) -> str:
    local_id = node["Node"]["value"]
    node_id = format_turtle_term(local_id)
    terms["properties"].add(node_id)

    lines = [
        node_id,
        "  a rdf:Property ;",
        f"  :isPartOf <{PENDING_URI}> ;",
    ]

    for domain_value in multiprop(node, "domainIncludes"):
        formatted = format_turtle_term(domain_value)
        terms["types"].add(formatted)
        lines.append(f"  :domainIncludes {formatted} ;")

    for range_value in multiprop(node, "rangeIncludes"):
        formatted = format_turtle_term(range_value)
        terms["types"].add(formatted)
        lines.append(f"  :rangeIncludes {formatted} ;")

    if name_value := get_pv(node, "name"):
        lines.append(f'  rdfs:label "{name_value}" ;')
    if description_value := get_pv(node, "description"):
        lines.append(f'  rdfs:comment """{description_value}""" ;')

    lines[-1] = f"{lines[-1][:-1]}."
    return "\n".join(lines)


def convert_mcf_to_turtle(mcf_data_str: str) -> str:
    """Convert MCF content string to a complete Schema.org Turtle document."""
    terms: dict[str, set[str]] = {
        "types": set(),
        "properties": set(),
        "enumerations": set(),
    }
    mcf_data = mcf_to_dict_list(mcf_data_str)
    debug_print(f"Loaded MCF data: {len(mcf_data)} entries")

    turtle_blocks = [TURTLE_PREFIXES]
    for node in mcf_data:
        node_type = node.get("typeOf", {}).get("value")
        if node_type == "Class":
            turtle_blocks.append(generate_class_turtle(node, terms))
        elif node_type == "Property":
            turtle_blocks.append(generate_property_turtle(node, terms))

    subclass_lines = [
        f"{term} rdfs:subClassOf :BioChemEntity ."
        for term in sorted(terms["types"])
        if term not in _CORE_SCALARS
    ]
    if subclass_lines:
        turtle_blocks.append("\n".join(subclass_lines))

    return "\n\n".join(turtle_blocks) + "\n"


def main(argv: Sequence[str] | None = None) -> None:
    global DEBUG
    parser = argparse.ArgumentParser(
        description="Convert a Data Commons MCF file into Schema.org Turtle."
    )
    parser.add_argument("mcf_file", type=Path, help="Path to the input MCF file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args(argv)
    DEBUG = args.debug

    if not args.mcf_file.is_file():
        print(f"MCF file '{args.mcf_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        mcf_data_str = args.mcf_file.read_text(encoding="utf-8")
        sys.stdout.write(convert_mcf_to_turtle(mcf_data_str))
    except Exception as exc:
        print(f"Error converting MCF into Schema TTL: {exc}", file=sys.stderr)
        if DEBUG:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
