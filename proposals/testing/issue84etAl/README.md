Schema.org -  Issue #84 et al. consolidation
============================================

The following issues are consolidated and/or updated here:

 * (main) https://github.com/schemaorg/schemaorg/issues/84
 * (complementing main) https://github.com/schemaorg/schemaorg/issues/348
 * (another matter) https://github.com/schemaorg/schemaorg/issues/350

#PROPOSAL TEXT#

## 1. Enhance source citations by mapping sources to LOV
Proposal for enhance [schema.org/schema.rdfa](http://schema.org) source citations (`dc:source`), linking (`href`) the sources to [LOV - Linked Open Vocabularies](http://lov.okfn.org).


**NEW RULE**: do not use something like `href="http://www.w3.org/wiki/WebSchemas/SchemaDotOrgSources#source_GoodRelationsProperties"`, should prefer to use always a http://lov.okfn.org/dataset/lov/vocabs link, as `href="http://lov.okfn.org/dataset/lov/vocabs/gr"`.

**RATIONALE**: ... under construction...

**ACTION**: apply the *new rule* to start to use it.


## 2. Generalize name prefix and suffix properties

**ACTION**: to rename the *honorificSuffix* property to `nameSuffix` and *honorificPrefix* property to `namePrefix`,  and generalize them for use in *Person* and *Organization* names.

-----

#CONCRETE MODIFICATIONS#

 1. (to do) enhance or create a "schema.org `rdfs:Class` and `rdfs:Property` templates" documentation 
 2. schema.rdfa modified (here) with the *section 1* proposal above.
 3. schema.rdfa modified (here) with the *section 2* proposal above.


