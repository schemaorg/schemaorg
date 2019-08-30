# Bioschemas Proposed Extension

This directory contains a proposal for extending schema.org to include types and properties for describing life sciences resources such as genes and proteins. The proposal has been developed by the [Bioschemas community]([https://bioschemas.org](https://bioschemas.org/)).

The proposal consists of the following types and where they sit in the schema.org hierarchy. For each type, we provide details of the major design decisions and domain vocabularies considered. The link takes you to the corresponding document for that type.

- Thing
  - [BioChemEntity](BioChemEntityCodingNotes.md)
    - [BioSample](BioSampleCodingNotes.md)
    - [ChemicalSubstance](ChemicalSubstanceCodingNotes.md)
    - [Gene](GeneCodingNotes.md)
    - [MolecularEntity](MolecularEntityCodingNotes.md)
    - [Protein](ProteinCodingNotes.md)
  - [Taxon](TaxonCodingNotes.md)

A test deployment of the schema.org pages with the Bioschemas extension can be found [here](http://sdo-bioschemas-227516.appspot.com/). Note that this instance has a very limited quota on the number of page requests it can serve. We have also made the types available through the Bioschemas website ([types](https://bioschemas.org/types/)).

Details of known deployments of these types can be found on the Bioschemas website ([deployments](https://bioschemas.org/liveDeploys/)).