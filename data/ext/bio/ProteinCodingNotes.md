# Proposal of Protein Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of a protein.

## Background

The `Protein` type has been discussed in the Bioschemas community in:

- Issues
  - [Relationship between Protein and Organism/Taxon](https://github.com/BioSchemas/specifications/issues/222)
  - [Protein Properties](https://github.com/BioSchemas/specifications/issues/262)
  - All issues labelled [Protein](https://github.com/BioSchemas/specifications/issues?utf8=✓&q=label:"type:+Protein")
- Bioschemas community mailing list thread
  - Evolution of Protein w.r.t. BioChemEntity [thread one](https://lists.w3.org/Archives/Public/public-bioschemas/2017Nov/0001.html)[thread two](https://lists.w3.org/Archives/Public/public-bioschemas/2017Nov/0026.html)
  - All emails containing the term [Protein](https://www.w3.org/Search/Mail/Public/advanced_search?keywords=&hdr-1-name=subject&hdr-1-query=Protein&hdr-2-name=from&hdr-2-query=&hdr-3-name=message-id&hdr-3-query=&period_month=&period_year=&index-grp=Public__FULL&index-type=t&type-index=public-bioschemas&resultsperpage=20&sortby=date-asc)

The following ontologies were considered when developing this proposal:

- Feature Annotation Location Description Ontology ([FALDO](https://github.com/OBF/FALDO))
- Gene Ontology ([GO](http://geneontology.org/))
- Protein Ontology ([PRO](https://proconsortium.org/))
- SemanticScience Integrated Ontology ([SIO](http://sio.semanticscience.org/))
- UniProt RDF Schema Ontology ([UniProt](https://www.uniprot.org/core/))

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/Protein (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/Protein/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `Protein` type under a `BioChemEntity` type which inherits from `schema:Thing`. `BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org. 

### Properties

- hasSequence: *New property* 

  **ToDo:** *How is this different from `hasRepresentation` proposed on BioChemEntity?*

