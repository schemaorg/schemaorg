#!/usr/bin/env python3

# bmdc2sdo.py
# find ../schema/biomedical_schema/ -name \*.mcf -exec ./bmdc2sdo.py {} \;

# TODO:
# - fix issue with multiple types in a rangeIncludes/subClassOf/domainIncludes.
# - add enumerations exporter (and statvars?)

# Usage: 
# python mcf2turtle.py ~/working/datcom/schema/biomedical_schema/biological_taxonomy.mcf 
# or several files
# find ~/working/datcom/schema/biomedical_schema/ -name \*.mcf -exec ./mcf2turtle.py {} \;
# to concatenate, or 
# find ~/working/datcom/schema/biomedical_schema/ -name \*.mcf -exec ./mcf2turtle.py {} > ./{}.ttl \;
# to echo filenames.

# Schema.org Utility to import definitions from a Data Commons collection of MCF files.
# Pass it a .mcf file, it should emit Schema.org configuration Turtle to STDOUT.

# This allows us to spin up an instance of the Schema.org site codebase on AppSpot or elsewhere,
# allowing draft proposals to be explored in their entirity.
# 
# Target TTL format is https://github.com/schemaorg/schemaorg/blob/main/data/ext/pending/issue-2862.ttl
#

# OK:
#  via python mcf2turtle.py ~/working/datcom/schema/biomedical_schema/biological_taxonomy.mcf  > tmp/biological_taxonomy.ttl
#
# biological_taxonomy.mcf     

# TODO:
# GeneticVariant_alt_id_database_properties.mcf  
# pharmGKB_id_properties.mcf
# biomedical_stat_vars.mcf
# GeneticVariant_GenVarSource_enums.mcf          
# chemical_compound_enum.mcf
# genome_annotation_enum.mcf
# virus_taxonomic_ranking_enum.mcf
# chemical_compound.mcf
# genome_annotation.mcf
# virus_taxonomy_enum.mcf
# disease_enum.mcf
# human_cell_type_enum.mcf
# virus_taxonomy.mcf
# disease.mcf
# human_tissue_enum.mcf
# encode.mcf
# interaction_type_enum.mcf



import os
import sys

# We assume https://github.com/datacommonsorg/data/ and https://github.com/datacommonsorg/tools/
# are checked out nearby:


# _MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
#sys.path.insert(1, os.path.join(_MODULE_DIR, '../data/'))

# Ensure data/ repo is nearby (for a basic MCF parser), for example:
sys.path.insert(1, '/home/danbri/working/datcom/data/')

#DEBUG = os.getenv("DEBUG", "0") == "1"
DEBUG = 0

from util.mcf_dict_util import mcf_file_to_dict_list

TURTLE_PREFIXES = """
@prefix : <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

"""

def debug_print(message):
    """
    Print a debug message if debug mode is enabled.
    """
    if DEBUG:
        print(f"DEBUG: {message}")



def split_and_format_values(value_string):
    """
    Splits a string by commas and formats it, preserving namespaces.
    Handles multiple namespaces (e.g., 'dcs:Gene,schema:Text').
    Returns a list of formatted strings.
    """
    formatted_values = []
    for value in value_string.split(','):
        value = value.strip()
        if ':' in value:  # Check if the value contains a namespace
            namespace, local_part = value.split(':', 1)
            formatted_value = f'{namespace}:{local_part}'
        else:
            formatted_value = f':{value}'  # Default to schema: if no namespace is present
        formatted_values.append(formatted_value)
        debug_print(f"Formatted value: {formatted_value}")
    return formatted_values

# Inline test cases
def test_split_and_format_values():
    print("Testing split_and_format_values function...")
    test_cases = [
        ("dcs:Disease,dcs:ICD10Code", ["dcs:Disease", "dcs:ICD10Code"]),
        ("dcs:MeSHDescriptor, schema:Text", ["dcs:MeSHDescriptor", "schema:Text"]),
        ("schema:Number,dcs:Text", ["schema:Number", "dcs:Text"]),
    ]
    for input_value, expected_output in test_cases:
        assert split_and_format_values(input_value) == expected_output, f"Test failed for input: {input_value}"
    print("All tests passed!")




def generate_class_turtle(node):
    """Generate Turtle syntax for a class node."""

    debug_print(f"Generating Turtle for class node: {node['Node']['value']}")

    node_id = f':{node["Node"]["value"]}'
    lines = [
        f'{node_id}',
        '  a rdfs:Class ;',
        '  :isPartOf <https://pending.schema.org> ;'
    ]
    
    # Prepare the label and comment values beforehand
    name_value = node.get("name", {}).get("value", "").strip('"')
    description_value = node.get("description", {}).get("value", "").strip('"')
    
    # Handle subClassOf with potential multiple values
    if 'subClassOf' in node:
        sub_class_values = split_and_format_values(node["subClassOf"]["value"])
        for sub_class_value in sub_class_values:
            lines.append(f'  rdfs:subClassOf {sub_class_value} ;')
    
    # Handle name and description
    if name_value:
        lines.append(f'  rdfs:label "{name_value}" ;')
    if description_value:
        lines.append(f'  rdfs:comment "{description_value}" ;')
    
    # End the statement properly
    lines[-1] = lines[-1][:-1] + ' .'
    
    return '\n'.join(lines)
def generate_property_turtle(node):
    """Generate Turtle syntax for a property node."""
    node_id = f':{node["Node"]["value"]}'
    lines = [
        f'{node_id}',
        '  a rdf:Property ;',
        '  :isPartOf <https://pending.schema.org> ;'
    ]
    
    # Prepare the label and comment values beforehand
    name_value = node.get("name", {}).get("value", "").strip('"')
    description_value = node.get("description", {}).get("value", "").strip('"')
    
    # Handle domainIncludes and rangeIncludes with potential multiple values
    if 'domainIncludes' in node:
        domain_values = split_and_format_values(node["domainIncludes"]["value"])
        for domain_value in domain_values:
            lines.append(f'  :domainIncludes {domain_value} ;')
    
    if 'rangeIncludes' in node:
        range_values = split_and_format_values(node["rangeIncludes"]["value"])
        for range_value in range_values:
            lines.append(f'  :rangeIncludes {range_value} ;')
    
    # Handle name and description
    if name_value:
        lines.append(f'  rdfs:label "{name_value}" ;')
    if description_value:
        lines.append(f'  rdfs:comment "{description_value}" ;')
    
    # End the statement properly
    lines[-1] = lines[-1][:-1] + ' .'
    
    return '\n'.join(lines)


def main():


    # Running test cases to ensure everything works as expected
    test_split_and_format_values()
    print("All tests passed!")

    # Check if the MCF file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Please provide the path to the MCF file as a command-line argument.")
        sys.exit(1)

    mcf_file_path = sys.argv[1]

    # Check if the MCF file exists
    if not os.path.isfile(mcf_file_path):
        print(f"MCF file '{mcf_file_path}' does not exist.")
        sys.exit(1)

    # Read and parse the MCF file
    try:
        mcf_data = mcf_file_to_dict_list(mcf_file_path)
        debug_print(f"Loaded MCF data: {len(mcf_data)} entries")

        # Assuming mcf_data is correctly parsed

        turtle_data = [TURTLE_PREFIXES]  # Start with the prefixes

        # Iterate over each node in mcf_data and process accordingly
        for node in mcf_data:
            if node["typeOf"]["value"] == "Class":
                turtle_data.append(generate_class_turtle(node))
            elif node["typeOf"]["value"] == "Property":
                turtle_data.append(generate_property_turtle(node))

        # Combine all turtle data into a single string
        final_turtle_output = '\n\n'.join(turtle_data)

        # Print or save the Turtle data
        print(final_turtle_output)

    except Exception as e:
        print(f"Error parsing MCF file: {str(e)}")
        if DEBUG:
            # In debug mode, you might want to re-raise the exception to get a stack trace.
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
