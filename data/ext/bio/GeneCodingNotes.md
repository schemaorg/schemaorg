# Proposal of Gene Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of a gene.

## Background

The `Gene` type has been discussed in the Bioschemas community in:

**ToDo:** Add links to most pertinant issues and email threads

- Issues
   - [Definition](https://github.com/BioSchemas/specifications/issues/272)
   - All issues labelled [Gene](https://github.com/BioSchemas/specifications/issues?utf8=%E2%9C%93&q=label%3A%22type%3A+Gene%22)
- Bioschemas community mailing list thread
  - [MyGene.info use case](https://lists.w3.org/Archives/Public/public-bioschemas/2019May/0003.html)
  - All emails containing the term [Gene](https://www.w3.org/Search/Mail/Public/advanced_search?keywords=&hdr-1-name=subject&hdr-1-query=gene&hdr-2-name=from&hdr-2-query=&hdr-3-name=message-id&hdr-3-query=&period_month=&period_year=&index-grp=Public__FULL&index-type=t&type-index=public-bioschemas&resultsperpage=20&sortby=date-asc)

The following ontologies were considered when developing this proposal:

- Feature Annotation Location Description Ontology ([FALDO](https://github.com/OBF/FALDO))
- Gene Ontology ([GO](http://geneontology.org/))
- Protein Ontology ([PRO](https://proconsortium.org/))
- SemanticScience Integrated Ontology ([SIO](http://sio.semanticscience.org/))
- UniProt RDF Schema Ontology ([UniProt](https://www.uniprot.org/core/))

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/Gene (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/Gene/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `Gene` type under a `BioChemEntity` type which inherits from `schema:Thing`. `BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org. 

### Properties

**ToDo:** Complete rationale for properties 

#### alternativeOf

*New property*

This property allows the linking of the many variants of a gene.

#### encodesBioChemEntity

*New property*



#### expressedIn

*New property*



#### hasSequence

*New property*

**ToDo:** *How is this different from `hasRepresentation` proposed on BioChemEntity?*

#### hasStatus

*New property*

