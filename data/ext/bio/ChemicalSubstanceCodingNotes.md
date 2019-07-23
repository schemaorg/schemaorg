# Proposal of ChemicalSubstance Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of chemical substances which represents the composition of molecular entities. 

This type should be used in conjunction with the newly proposed `MolecularEntity` type.

## Background

The `ChemicalSubstance` type has been discussed in the Bioschemas community in:

**ToDo:** Add links to most pertinant issues and email threads

- Issue
- Bioschemas community mailing list thread
  - [

The proposal is based on the [ChEBI ontology](https://www.ebi.ac.uk/chebi/) and its definition of a chemical substance ([CHEBI:59999](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI%3A59999)).

**ToDo:** Discussion about relationship to `schema:Drug` and `schema:Substance`

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/ChemicalSubstance (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/ChemicalSubstance/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `ChemicalSubstance` type under a `BioChemEntity` type which inherits from `schema:Thing`. `BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org. 

### Properties

**ToDo:** Complete rationale for properties 

#### chemicalRole

*New property*



#### molecularFormula

*New property*



#### potentialUse

*New property*

