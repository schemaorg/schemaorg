Schema.org -  Issue #280 consolidation
======================================

The following issue is consolidated and/or updated here:
https://github.com/schemaorg/schemaorg/issues/280

PROPOSAL TEXT
=============

Proposal for enhance [schema.rdfa](http://schema.org/docs/schema_org_rdfa.html) definition descriptors (`rdfs:comment`) and semantics, mapping each vocabulary item to a Wikidata item. 

A sibling project at Wikidata will be the *Wikidata.org-to-Schema.org* mapping.

##PART 1 - SchemaOrg  mapping to Wikidata ##

*Actions*: add `<link property="{$OWL}" href="{$WikidataURL}"/>` with the correct *$WikidataURL*.   

   * At  each `rdfs:Class ` add the `<link>` tag with  `$OWL="owl:equivalentClass"` or, when not possible, `$OWL="rdfs:subClassOf"`.

   * At  each `rdf:Property ` add the `<link>` tag with  `$OWL="owl:equivalentProperty"` or, when not possible, `$OWL="rdfs:subPropertyOf"`.

*Actions on testing phase*:  do some with no automation. Example: start with classes Person and Organization, and its properties.

*Examples*

* http://schema.org/Organization  is `owl:equivalentClass`  to *[Q43229](https://www.wikidata.org/wiki/Q43229)*.

* http://schema.org/City is `owl:equivalentClass`  to  *[Q515](https://www.wikidata.org/wiki/Q515)*.

* http://schema.org/Person is `owl:equivalentClass`  to *[Q215627](https://www.wikidata.org/wiki/Q215627)*.

* http://schema.org/PostalAddress is `owl:equivalentClass`  to  *[Q319608](https://www.wikidata.org/wiki/Q319608)*.

-------------

##PART 2 -  Wikidata mapping to SchemaOrg ##

... under construction... see similar mappings at  [schema.rdfs.org/mappings.html](http://schema.rdfs.org/mappings.html)...  Wikidata also have a lot of iniciatives maping Wikidata to external vocabularies (ex. there are a map from Wikidata to BNCF Thesaurus)...

... some comments about (automation):
* "(...) we can automate importing most of that mapping into Wikidata so no one needs to click and copy&paste..."
* "I could not figure out a good programmatic way to access Wikidata's schema information in all its richness. Maybe there is a way to take the JSON dumps, load them into some fast-access NoSQL-ish database, so that things can be searched/matched/retrieved easily?"
* ...

#CONCRETE MODIFICATIONS#

Step-by-step:

 1. use tool `updtRDF-CSV.php` (check/edit the main configs before to use).

    1.1. Generating the first version (original) from ex. [sdo-gozer/data/schema.rdfa](https://github.com/schemaorg/schemaorg/blob/sdo-gozer/data/schema.rdfa). <br/>Terminal command: `php updtRDF-CSV.php > original.csv`

    1.2. Read `original.csv` with LibreOffice or Excel, to render columns, add bolds, etc.  And upload it in  GoogleDocs. Example: [generated2015-02-23 spreadsheet](https://docs.google.com/spreadsheets/d/1KeTSrVjSHRfVRwSgg6-LN0pu6nVre7cspUrkf_gfMm8/).

    1.3. Download the edited spreadsheet (ex. updated2015-02-24) and transform it in a new `schema.rdfa`.  <br/>Terminal command: `php updtRDF-CSV.php -u > schema.rdfa.htm`

 2. ... Check all, replace `data/schema.rdfa`, send a fork to Github... Example: 

#WORKING IN PROGRESS

See the shared [generated2015-02-23 spreadsheet](https://docs.google.com/spreadsheets/d/1KeTSrVjSHRfVRwSgg6-LN0pu6nVre7cspUrkf_gfMm8/).

## APPENDIX - USING TERMINAL TOOL 

```shell
git clone ....
cd schemaorg/proposals/testing/issue280/
php updtRDF-CSV.php > spreadsheets/original.csv

# ... some days later, after online collaboration, exporting ex. spreadsheets/updated2015-02-23b.csv ...
% php updtRDF-CSV.php -u > schema.rdfa.htm
# this last command results in:
```
```txt
	 --line 89.	 Organization = Q43229
	 --line 91.	  brand = Q431289
	 --line 96.	  email = Q9158
	 --line 803.	 Person = Q215627
	 --line 804.	  additionalName < Q1071027
	 --line 806.	  alumniOf = Q447877
	 --line 807.	  birthDate = Q47223
	 --line 808.	  children < Q171318
	 --line 809.	  colleague = Q1751358
	 --line 810.	  colleagues = Q1751358
	 --line 811.	  deathDate < Q1202197
	 --line 812.	  familyName = Q101352
	 --line 814.	  gender = Q48264
	 --line 815.	  givenName = Q202444
```

```shell
# Now you can count items of this new `schema.rdfa.htm`:
php updtRDF-CSV.php -c
```
```txt
 ---- COUNTING (../../../data/schema.rdfa)... ----
	 --ERROR-3 on label of class  TaxiReservation.
	 --ERROR-3 on label of class  TrainReservation.
	 --ERROR-2 (no label) on http://schema.org/comment .
	 --ERROR-2 (no label) on http://schema.org/genre .
	 --ERROR-2 (no label) on http://schema.org/duration .
	 --ERROR-2 (no label) on http://schema.org/SportsTeam .
	 --ERROR-2 (no label) on http://schema.org/DatedMoneySpecification .
	 --ERROR-2 (no label) on http://schema.org/startDate .
	 --ERROR-2 (no label) on http://schema.org/endDate .
	 --ERROR-2 (no label) on http://schema.org/width .
	 --ERROR-2 (no label) on http://schema.org/height .
	 --ERROR-2 (no label) on http://schema.org/depth .
	 --ERROR-5 clinicalPharmacology duplicated.
	 --ERROR-5 departureAirport duplicated.
 #Divs=1521 (sum=1478  #Class=620; #nProp=858); #supersededBy=33; dups=2
```



