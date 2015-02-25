Schema.org - Version reports
============================

... under construction....


PROPOSAL TEXT
=============

Proposal for enhance [schema.org/releases](http://schema.org/docs/releases.html) and/or internal documentation, with "counting reports" that summarize the profile of each release. As adicional information, also sumarizes "errors" when exists. 

The *report-tools* can be also assume the rule of *validators*, and vice-versa.

## Report tool ##

See https://github.com/ppKrauss/schemaorg/blob/sdo-gozer/proposals/testing/issue280/updtRDF-CSV.php
 (options -r and -c)


RELEASES AND DUMPS
==================
Main releases and the result reporting of each one. The dumps are for checking profile and to compare with near releases.

## 2015-02-25-master dump ##
...

## 2015-02-25-portal dump ##
At http://schema.org/docs/schema_org_rdfa.html in 2015-02-25.
Same as 2015-02-25-master, differing only by 

`<link property="supersededBy" href="http://schema.org/clinicalPharmacology" />` (portal).

## Release of 2015-02-07 (v1.94-gozer) ##
File of https://github.com/schemaorg/schemaorg/branches  renamed here to
`r2015-02-07-sdoGozer.schema.rdfa.htm`.

**GENERAL PROFILE (countings)**

 * number of div tags (nDivs): 1521
 * number of definitions by classes+properties (nDefs): 1478
 * number of rdfs-classes (nClass): 620
 * number of rdf-Properties (nProp): 858
 * number of schema-supersededBy (nSupBy): 33
 * number of duplicated rdfs-labels (nDup): 2
 * number of defs with link tag (nLinks): 105
 * total number of link tags over defs (nLinksTot): 112

**VALIDATION**

Some little problems:

 * Labels of classes with space: ' TaxiReservation', ' TrainReservation'.
 * Tag `div` with resource definition (?) but with no `rdfs:label`: comment, genre, duration, SportsTeam, DatedMoneySpecification, startDate, endDate, width, height, depth.
 * Duplicated labels:  'clinicalPharmacology' and 'departureAirport'.


## Release of 2015-02-04 (v1.93-stantz) ##
File of https://github.com/schemaorg/schemaorg/branches  renamed here to
`r2015-02-04-v1.93-sdoStantz.schema.rdfa.htm`.

**GENERAL PROFILE (countings)**

 * number of div tags (nDivs): 1521
 * number of definitions by classes+properties (nDefs): 1478
 * number of rdfs-classes (nClass): 620
 * number of rdf-Properties (nProp): 858
 * number of schema-supersededBy (nSupBy): 33
 * number of duplicated rdfs-labels (nDup): 2
 * number of defs with link tag (nLinks): 105
 * total number of link tags over defs (nLinksTot): 112

**VALIDATION**

Some little problems:

 * Labels of classes with space: ' TaxiReservation', ' TrainReservation'.
 * Tag `div` with resource definition (?) but with no `rdfs:label`: comment, genre, duration, SportsTeam, DatedMoneySpecification, startDate, endDate, width, height, depth.
 * Duplicated labels:  'clinicalPharmacology' and 'departureAirport'.

## Release of 2014-12-11 (v1.92-venkman) ##
File of https://github.com/schemaorg/schemaorg/branches  renamed here to
`r2014-12-11-v1.92-sdoVenkman.schema.rdfa.htm`.

**GENERAL PROFILE (countings)**

 * number of div tags (nDivs): 1503
 * number of definitions by classes+properties (nDefs): 1463
 * number of rdfs-classes (nClass): 618
 * number of rdf-Properties (nProp): 845
 * number of schema-supersededBy (nSupBy): 33
 * number of duplicated rdfs-labels (nDup): 1
 * number of defs with link tag (nLinks): 104
 * total number of link tags over defs (nLinksTot): 111

**VALIDATION**

Some little problems:

 * Labels of classes with space: ' TaxiReservation', ' TrainReservation'.
 * Tag `div` with resource definition (?) but with no `rdfs:label`: comment, genre, duration, SportsTeam, DatedMoneySpecification, startDate, endDate.
 * Duplicated labels: 'departureAirport'.



