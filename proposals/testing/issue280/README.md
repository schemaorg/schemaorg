Schema.org -  Issue #280 consolidation
======================================

The following issue is consolidated and/or updated here:
https://github.com/schemaorg/schemaorg/issues/280

PROPOSAL TEXT
=============

Proposal for enhance [schema.rdfa](http://schema.org/docs/schema_org_rdfa.html) definition descriptors (`rdfs:comment`) and semantics, mapping each vocabulary item to a Wikidata item. 

A sibling project at Wikidata will be the *Wikidata.org-to-Schema.org* mapping.

##PART 1 - SchemaOrg  mapping to Wikidata ##

*Actions*: add `<link property="{$OWL}" href="{$WikiDataURL}"/>` with the correct *$WikiDataURL*.   

   * At  each `rdfs:Class ` add the `<link>` tag with   `$OWL="owl:equivalentClass"` or, when not possible, use`$OWL="rdfs:subClassOf"`.

   * At  each `rdf:Property ` add the `<link>` tag with   `$OWL="owl:equivalentProperty"` or, when not possible, use`$OWL="rdfs:subPropertyOf"`.

*Actions on testing phase*:  do some with no automation. Example: start with classes Person and Organization, and its properties.

*Examples*

* http://schema.org/Organization  is `owl:equivalentClass`  to *[Q43229](https://www.wikidata.org/wiki/Q43229)*.

* http://schema.org/City is `owl:equivalentClass`  to  *[Q515](https://www.wikidata.org/wiki/Q515)*.

* http://schema.org/Person is `owl:equivalentClass`  to *[Q215627](https://www.wikidata.org/wiki/Q215627)*.

* http://schema.org/PostalAddress is `owl:equivalentClass`  to  *[Q319608](https://www.wikidata.org/wiki/Q319608)*.

-------------

##PART 2 -  Wikidata mapping to SchemaOrg ##

... under construction... see similar mappings at  [schema.rdfs.org/mappings.html](http://schema.rdfs.org/mappings.html)...  Wikidata also have a lot of iniciatives maping Wikidata to external vocabularies (ex. there are a map from Wikidata to BNCF Thesaurus)...

#CONCRETE MODIFICATIONS#

Step-by-step:

 1. create tools: `generateCSV.php` and `updateWithWikidata.php`. 
 2. Use `generateCSV` tool to generates a CSV file (ex. `generated2015-02-23.csv`)
 3. Edit it as spreadsheet on GoogleDocs (@danbri suggestion). All colaborators edit at GoogleDocs.
 4. Export back to CSV (ex. `generated2015-02-23-back.csv`).
 3. Modify `schema.rdfa` with the `updateWithWikidata` tool. Check and send to fork at Github.

#WORKING IN PROGRESS

See the shared [generated2015-02-23 spreadsheet](https://docs.google.com/spreadsheets/d/1KeTSrVjSHRfVRwSgg6-LN0pu6nVre7cspUrkf_gfMm8/).

