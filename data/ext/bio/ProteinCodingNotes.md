# Proposal of Protein Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of a protein.

## Background

The `Protein` type has been discussed in the Bioschemas community in:

**ToDo:** Add links to most pertinant issues and email threads

- Issue
- Bioschemas community mailing list thread
  - [

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

**ToDo:** Complete rationale for properties 

#### hasSequence

*New property*

**ToDo:** *How is this different from `hasRepresentation` proposed on BioChemEntity?*

