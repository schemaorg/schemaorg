#!/usr/bin/env python3

import os
import sys
import logging
from typing import Dict, Optional, Union
from collections import OrderedDict

DEBUG = False

# see readme.md

"""Convert MCF into Turtle for Schema.org. 

Example input:

Node: dcid:medicalSubjectHeadingSupplementaryRecordID
name: "medicalSubjectHeadingSupplementaryRecordID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHSupplementaryRecord, schema:Text
domainIncludes: dcs:ChemicalCompound, dcs:MeSHSupplementaryRecord
description: "A unique ID for a Medical Subject Heading supplementary record.

Example output:

:medicalSubjectHeadingSupplementaryRecordID
  a rdf:Property ;
  :isPartOf <https://pending.schema.org> ;
  :domainIncludes ChemicalCompound ;
  :domainIncludes dcs:MeSHSupplementaryRecord ;
  :rangeIncludes MeSHSupplementaryRecord ;
  :rangeIncludes schema:Text ;
  rdfs:label "medicalSubjectHeadingSupplementaryRecordID" ;
  rdfs:comment \"\"\\"A unique ID for a Medical Subject Heading supplementary record.\"\""  .
"""

TURTLE_PREFIXES = """
@prefix : <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dcs: <https://datacommons.org/schema/> .

"""

# originally from datacommons/data/util/
def my_mcf_to_dict_list(mcf_str: str) -> list:
    """Converts MCF file string to a list of OrderedDict objects.

    Args:
        mcf_str: String read from MCF file.
        
    Returns:
        List of OrderedDict objects where each object represents a node in the MCF file.
    """
    # TODO preserve empty lines if required
    # split by \n\n
    nodes_str_list = mcf_str.split('\n\n')
    # each node
    node_list = []

    for node in nodes_str_list:
        node = node.strip()
        # check for comments
        node_str_list = node.split('\n')
        cur_node = OrderedDict()
        comment_ctr = 0
        is_first_prop = True
        # add each pv to ordered dict
        for pv_str in node_str_list:
            # TODO handle multiple occurrences of same property within a node
            pv_str = pv_str.strip()
            if pv_str.startswith('#'):
                cur_node[f'__comment{comment_ctr}'] = pv_str
                comment_ctr += 1
            elif is_first_prop:
                is_first_prop = False
                if pv_str and not pv_str.startswith('Node: '):
                    raise ValueError(
                        f'Missing "Node: <name>" in MCF node {node}')
            if pv_str and not pv_str.startswith('#'):
                # find p, prefix, v
                pv = pv_str.split(':')
                if pv_str.count(':') == 1:
                    p = pv[0].strip()
                    prefix = ''
                    v = pv[1].strip()
                elif pv_str.count(':') == 2:
                    p = pv[0].strip()
                    prefix = pv[1].strip()
                    v = pv[2].strip()
                else:
                    p = pv[0].strip()
                    prefix = pv[1].strip()
                    v = ':'.join(pv[2:]).strip()
                    # TODO detect colon within a str(for e.g. descriptionURL)
                    #logging.warning(
                    #    "# substructure detected in property value(s) using ':' found in %s",
                    #    pv_str)

                cur_node[p] = {}
                cur_node[p]['value'] = v
                if v.startswith('[') and v.endswith(']'):
                    cur_node[p]['complexValue'] = re.sub(' +', ' ',
                                                         v)[1:-1].split(' ')
                if v.count(':') > 0 and ',' in v:
                    # TODO better handling of multiple values
                    cur_node[p]['multiple_values'] = []
                    vals = v.split(',')
                    for cur_v in vals:
                        temp_dict = {}
                        if ':' in cur_v:
                            temp_dict['namespace'] = cur_v[:cur_v.
                                                           index(':')].strip()
                            temp_dict['value'] = cur_v[cur_v.index(':') +
                                                       1:].strip()
                        else:
                            temp_dict['namespace'] = ''
                            temp_dict['value'] = cur_v
                cur_node[p]['namespace'] = prefix
        node_list.append(cur_node)
    return node_list

def get_pv(node, property_name):
    return node.get(property_name, {}).get("value", "").strip('"')

def debug_print(message):
    if DEBUG:
        print(f"# DEBUG: {message}")


def multiprop(node, property_name):
    """
    Handle multi-valued properties, e.g., subClassOf, domainIncludes, rangeIncludes.
    Returns a set of cleaned property values.
    """
    if property_name in node:
        pv_values = node[property_name]["value"].split(",")
        return {pv.strip() for pv in pv_values}
    return set()

def generate_class_turtle(node, terms):
    debug_print(f"# Generating Turtle for class node: {node['Node']['value']}")

    node_id = f':{node["Node"]["value"]}'
    terms['types'].add(node["Node"]["value"])

    lines = [
        f'{node_id}',
        '  a rdfs:Class ;',
        '  :isPartOf <https://pending.schema.org> ;'
    ]
    
    name_value = get_pv(node, "name")
    description_value = get_pv(node, "description")
    
    for sub_class in multiprop(node, "subClassOf"):
        terms['types'].add(sub_class)  # Add the supertype to the terms['types'] set
        lines.append(f'  rdfs:subClassOf :{sub_class} ;')

    if name_value:
        lines.append(f'  rdfs:label "{name_value}" ;')
    if description_value:
        lines.append(f'  rdfs:comment """{description_value}""" ;')
    
    lines[-1] = lines[-1][:-1] + ' .'
    
    return {
        'turtle': '\n'.join(lines),
        'terms': terms
    }

def generate_property_turtle(node, terms):
    node_id = f':{node["Node"]["value"]}'
    terms['properties'].add(node["Node"]["value"])

    lines = [
        f'{node_id}',
        '  a rdf:Property ;',
        '  :isPartOf <https://pending.schema.org> ;'
    ]
    
    name_value = get_pv(node, "name")
    description_value = get_pv(node, "description")
    
    for domain_value in multiprop(node, "domainIncludes"):
        terms['types'].add(domain_value)
        lines.append(f'  :domainIncludes :{domain_value} ;')
    
    for range_value in multiprop(node, "rangeIncludes"):
        terms['types'].add(range_value)
        lines.append(f'  :rangeIncludes :{range_value} ;')
    
    if name_value:
        lines.append(f'  rdfs:label "{name_value}" ;')
    if description_value:
        lines.append(f'  rdfs:comment """{description_value}""" ;')
    
    lines[-1] = lines[-1][:-1] + ' .'
    
    return {
        'turtle': '\n'.join(lines),
        'terms': terms
    }

    return sorted(list(types))

def main():
    if len(sys.argv) < 2:
        print("Please provide the path to the MCF file as a command-line argument.")
        sys.exit(1)

    mcf_file_path = sys.argv[1]

    if not os.path.isfile(mcf_file_path):
        print(f"MCF file '{mcf_file_path}' does not exist.")
        sys.exit(1)

    terms = {
        'types': set(),
        'properties': set(),
        'enumerations': set()
    }

    try:
        with open(mcf_file_path, 'r') as file:
            mcf_data_str = file.read()

        mcf_data = my_mcf_to_dict_list(mcf_data_str)
        debug_print(f"# Loaded MCF data: {len(mcf_data)} entries")

        turtle_data = [TURTLE_PREFIXES]

        for node in mcf_data:
            if node["typeOf"]["value"] == "Class":
                result = generate_class_turtle(node, terms)
                turtle_data.append(result['turtle'])
                terms = result['terms']
            elif node["typeOf"]["value"] == "Property":
                result = generate_property_turtle(node, terms)
                turtle_data.append(result['turtle'])
                terms = result['terms']


        final_turtle_output = '\n\n'.join(turtle_data)

        print(final_turtle_output)
        print("\n")
        for term in terms["types"]:
            if term not in ["Boolean", "Text", "Number", "schema:Text"]:
                if ':' in term:
                    ns_prefix, term_name = term.split(':', 1)
                    print(f'{ns_prefix}:{term_name.strip()} rdfs:subClassOf :BioChemEntity .')
                else:
                    print(f':{term.strip()} rdfs:subClassOf :BioChemEntity .')

    except Exception as e:
        print(f"Error converting MCF into Schema TTL: {str(e)}")
        if DEBUG:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
