# Proposal of Taxon Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of a taxon. 

## Background

The `Taxon` type has been discussed in the Bioschemas community in:

**ToDo:** Add links to most pertinant issues and email threads

- Issue
- Bioschemas community mailing list thread
  - [

The proposal is based on the [Darwin Core standard for Taxons](https://dwc.tdwg.org/terms/#taxon) that is widely used to model taxons.

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/Taxon (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/Taxon/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `Taxon` type under a `BioChemEntity` type which inherits from `schema:Thing`.

`BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org.

### Properties

**ToDo:** Complete rationale for properties 

#### childTaxon

*New property*



#### hasDefinedTerm

*Property reuse*

Extends the range of the property to include Taxon.

#### parentTaxon

*New property*

**ToDo:** *Is this related to [`dwc:parentNameUsageID`](https://dwc.tdwg.org/terms/#dwc:parentNameUsageID)?*

#### taxonRank

*New property*

**ToDo:** *Is this equivalent to [`dwc:taxonRank`](https://dwc.tdwg.org/terms/#dwc:taxonRank)?*

