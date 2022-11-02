
# Schema.org Markup Validator

This is a placeholder documentation page for the validator.

This service will validate Schema.org-based structured data embedded in web pages.

## Features

 * Extracts JSON-LD 1.0, RDFa 1.1, Microdata markup.
 * Displays a summary of the extracted structured data graph.
 * Identifies syntax mistakes in the markup.
 
It is based on the tool previously known as the Google Structured Data Testing Tool (SDTT), and is provided 
by Google as a service for the Schema.org community. 

# Notes

It can...

 * Fetch pages from URL, or validate markup provided directly.
 * Extract structured data injected by Javascript, e.g. by widgets.
 * Combine JSON-LD from script elements, alongside data the HTML attributes defined by RDFa and Microdata.
 * Apply some heuristics for cases where markup provides text values when an entity is expected.

# Limitations

 * The tool is focused on Schema.org. In the case of JSON-LD, this means that it will not fetch or interpret  other @context URLs.


