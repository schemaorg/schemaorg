# Proposal of Taxon Type

The [Bioschemas](https://bioschemas.org) community would like to propose a new type for marking up details of a taxon. 

## Background

The `Taxon` type has been discussed in the Bioschemas community in:

- Issues
  - [Taxon vs TaxonName](https://github.com/BioSchemas/specifications/issues/309)
  - [Taxon Hierarchy](https://github.com/BioSchemas/specifications/issues/324)
  - [Related ontologies](https://github.com/BioSchemas/specifications/issues/348)
  - All issues labelled [Taxon](https://github.com/BioSchemas/specifications/issues?utf8=✓&q=label:"type:+Taxon")
- Bioschemas community mailing list thread
  - All emails containing the term [Taxon](https://www.w3.org/Search/Mail/Public/advanced_search?keywords=&hdr-1-name=subject&hdr-1-query=taxon&hdr-2-name=from&hdr-2-query=&hdr-3-name=message-id&hdr-3-query=&period_month=&period_year=&index-grp=Public__FULL&index-type=t&type-index=public-bioschemas&resultsperpage=20&sortby=date-asc)

The proposal is based on the [Darwin Core standard for Taxons](https://dwc.tdwg.org/terms/#taxon) that is widely used to model taxons. Other ontologies considered during the design were:

- Biodiversity Information Standards (TDWG) [Ontology](https://github.com/tdwg/ontology)
- NCBI [Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)
- Wikidata

## Proposal

The proposed type is available at http://sdo-bioschemas-227516.appspot.com/Taxon (a cached copy is also available on the Bioschemas [website](https://bioschemas.org/types/Taxon/)).

We summarise here the design decisions taken to reach this proposal.

### Type Hierarchy

We are proposing to add the `Taxon` type under a `BioChemEntity` type which inherits from `schema:Thing`.

`BioChemEntity` is being proposed as an umbrella type that the various types coming from Bioschemas will be placed under. This is to prevent bloat at the top level of Schema.org.

### Properties

- childTaxon: *New property*
- hasDefinedTerm: *Property reuse*
Extends the range of the property to include Taxon.
- parentTaxon: *New property*  
Based on [`dwc:parentNameUsageID`](https://dwc.tdwg.org/terms/#dwc:parentNameUsageID)
- taxonRank: *New property*  
Equivalent to [`dwc:taxonRank`](https://dwc.tdwg.org/terms/#dwc:taxonRank)
