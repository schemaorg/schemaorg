Welcome to SchemaExamples
=======================
   
   A module in the schemaorg repository for the accessing and processing of Example entries designed for use with User Interfaces displaying descriptions of terms in the [Schema.org](https://schema.org) vocabulary.
   
   An 'Example' entry is of the following text format:

 TYPES: #eg-0000 Type/property, Type/property, etc.

 PRE-MARKUP:

 MICRODATA:

 RDFA:

 JSON:


```#eg-0000``` - a unique example id 
```Type/Property```  - The label of terms associated with the example
Text contained following PRE-MARKUP,  MICRODATA, RDFA, & JSON headings is to be reproduced in as example contents in the UI.

One or more Examples are useually stored in a single file, by convention, with the '-examples.txt' suffix.

The ```schemaexamples.py``` module contains two significant classes: 
 
 * ```Example``` - Class for representing, modifying and serialising an example entry
 * ```SchemaExamples``` - Container loaded from example file(s) (via ```SchemaExamples.from_files``` or ```SchemaExamples.from_default```) providing mappings between Schema.org terms and associated examples.



