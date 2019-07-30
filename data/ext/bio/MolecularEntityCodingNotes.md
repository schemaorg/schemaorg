# Proposal of MolecularEntity Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of a molecular entity. 

## Background

The `MolecularEntity` type has been discussed in the Bioschemas community in:

**ToDo:** Add links to most pertinant issues and email threads

- Issue
- Bioschemas community mailing list thread
  - [

The proposal is based on the [ChEBI ontology](https://www.ebi.ac.uk/chebi/) and its definition of a molecular entity ([CHEBI:23367](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI%3A23367)).

The following ontologies were also considered when developing this proposal:

- Chemical Entities of Biological Interest ([ChEBI](https://www.ebi.ac.uk/chebi/))
- Chemical Information Ontology ([CHEMINF](http://semanticchemistry.github.io/semanticchemistry/)) 
- SemanticScience Integrated Ontology ([SIO](http://sio.semanticscience.org/))

**ToDo:** Discussion about relationship to `schema:Drug` and `schema:Substance`

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/MolecularEntity (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/MolecularEntity/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `MolecularEntity` type under a `BioChemEntity` type which inherits from `schema:Thing`. `BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org.

### Properties

**ToDo:** Complete rationale for properties 

#### chemicalRole

*New property*



#### inChI

*New property*



#### inChIKey

*New property*



#### iupacName

*New property*



#### molecularFormula

*New property*



#### molecularWeight

*New property*



#### monoisotopicMolecularWeight

*New property*



#### potentialUse

*New property*



#### smiles

*New property*

