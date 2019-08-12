# Proposal of ChemicalSubstance Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of chemical substances which represents the composition of molecular entities. 

This type should be used in conjunction with the newly proposed `MolecularEntity` type.

## Background

The `ChemicalSubstance` type has been discussed in the Bioschemas community in:

**ToDo:** Add links to most pertinant issues and email threads

- Issues
  - [Clarifying ChemicalSubstance vs MolecularEntity](https://github.com/BioSchemas/specifications/issues/327)
  - All issues labelled [ChemicalSubstance](https://github.com/BioSchemas/specifications/issues?utf8=%E2%9C%93&q=label%3A%22type%3A+ChemicalSubstance%22)
- Bioschemas community mailing list thread
  - [Difference between ChemicalSubstance and MolecularEntity](https://lists.w3.org/Archives/Public/public-bioschemas/2019Jun/0008.html)
  - All emails containing the term [BioChemEntity](https://www.w3.org/Search/Mail/Public/advanced_search?keywords=&hdr-1-name=subject&hdr-1-query=chemicalsubstance&hdr-2-name=from&hdr-2-query=&hdr-3-name=message-id&hdr-3-query=&period_month=&period_year=&index-grp=Public__FULL&index-type=t&type-index=public-bioschemas&resultsperpage=20&sortby=date-asc)

The proposal is based on the [ChEBI ontology](https://www.ebi.ac.uk/chebi/) and its definition of a chemical substance ([CHEBI:59999](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI%3A59999)).

The following ontologies were also considered when developing this proposal:

- Chemical Entities of Biological Interest ([ChEBI](https://www.ebi.ac.uk/chebi/))
- Chemical Information Ontology ([CHEMINF](http://semanticchemistry.github.io/semanticchemistry/)) 
- SemanticScience Integrated Ontology ([SIO](http://sio.semanticscience.org/))

**ToDo:** Discussion about relationship to `schema:Drug` and `schema:Substance`

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/ChemicalSubstance (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/ChemicalSubstance/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `ChemicalSubstance` type under a `BioChemEntity` type which inherits from `schema:Thing`. `BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org. 

### Properties

**ToDo:** Complete rationale for properties 

#### chemicalComposition

*New property*



#### chemicalRole

*New property*



#### potentialUse

*New property*
