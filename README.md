
Welcome to Schema.org
=====================

This is the Schema.org project repository. It contains all the schemas, examples and software used to publish schema.org. For the site itself, please see [Schema.org](https://schema.org/) instead.

Note: Much of the supporting software is imported from a sub module: 'sdopythonapp'

Issues and proposals are managed here by collaborators around the project, especially participants of the [W3C Schema.org Community Group](https://www.w3.org/community/schemaorg/). If you are interested to participate please
join the group at the [W3C](https://www.w3.org/community/schemaorg/), introduce yourself and find or file issues here that engage your interest. If you are new to Git and GitHub, there's a useful [introduction to GitHub](https://www.w3.org/2006/tools/wiki/Github) in the W3C Wiki.

There are also continuous integration tests to check incoming pull requests.

[Issue #1](https://github.com/schemaorg/schemaorg/issues/1) in GitHub is an entry point for release planning. It
should provide an overview of upcoming work, in terms of broad themes, specific issues and release milestones.

[Issue #1](https://github.com/schemaorg/schemaorg/issues/1) will link to per-release entry points, or else navigate issues via label or milestone within GitHub.
Every change to the site comes via discussions here. Substantive changes are recorded in our [release notes](https://schema.org/docs/releases.html).
A preview of the [draft new release notes](https://staging.schema.org/docs/releases.html) can be found as part of the test site for our next release.
Every month or so, after final review by the Schema.org Steering Group and wider community, we make a formal release.

Regarding CC and opensource licenses for documents and software, see our [FAQ entry](https://schema.org/docs/faq.html#18).

Improving schemas
=================

We are always interested in practical suggestions for improvements to schema.org, and our collection of schemas has been [growing gradually](http://schema.org/docs/releases.html) since our launch in 2011.

We try to [prioritize](https://lists.w3.org/Archives/Public/public-schemaorg/2015Dec/0016.html) simple fixes and improvements to our existing schemas, examples and documentation over the addition of new vocabulary, and we are most likely to add new schemas when there is evidence that some (preferably large-scale) consuming application will make use of the data. Consuming applications need not be search engines; software tools e.g. opensource, markup-enriched approaches to Web analytics, browser add-ons or cloud tools are all rich areas for exploration and collaboration. The important thing is that there should be some reasonable expectation of data consumers making good use of the changes. It is not sufficient to justify additions on the basis that search engines generally try to use Schema.org-based structured data. Smaller changes, and backwards-compatible changes, are easier to incorporate.

Note that Schema.org does *not* attempt to capture the full detail of Web content; it is necessarily a simplification of a more complex reality. This means that there will be many cases where adding more detail to Schema.org will look possible. However, in the interests of keeping Schema.org simple and usable for publishers and webmasters, we will often choose not to add such detail. Schema.org uses Web standards such as JSON-LD, Microdata and RDFa to
allow for [independent extension](http://schema.org/docs/extension.html) (for example, see [GS1's vocabulary](https://ref.gs1.org/voc/)).

We are also highly unlikely to take on large scale reorganizations of Schema.org's terminology, if they are motivated solely  by considerations of elegance, "proper modeling", ontological purity or conceptual unification. Although the project founders and team are familiar with - and respectful of - the traditions behind such concerns, the scale, scope and nature of Schema.org has required us to trade elegance and global consistency for a somewhat scruffier notion of incremental evolution and a pragmatic tolerance for a style that would be out of place in a formal ontology. Proposals for unifying, cross-domain logic-based knowledge structures may be better received e.g. in the [Ontolog](https://groups.google.com/g/ontolog-forum) community.

We sometimes introduce types without dedicated property associations, simply for markup usability reasons. In a formal ontology, this is often considered poor modeling. However, logically equivalent structures can result in many more errors from publishers/webmasters unfamiliar with the underlying formal concepts behind JSON-LD or RDF/S. Schema.org is not a closed system, and other initiatives e.g. Wikidata or [GS1](https://ref.gs1.org/voc/) have defined many other terms that can be mixed in alongside those we define at schema.org. We also make efforts to align our designs to relevant external standards and initiatives, even when it reduces the global elegance of Schema.org considered alone. For example in a bibliographic or cultural heritage context we may be influenced by initiatives like MARC, BibFrame, and FRBR, while for e-commerce we collaborated with [Good Relations](https://blog-schema.org/2012/11/08/good-relations-and-schema-org/) and GS1. Schema.org's [news](https://schema.org/docs/news.html)-related terms were heavily influenced by incorporating [IPTC's rNews](https://iptc.org/standards/rnews/) design, alongside collaborations with [fact checkers](https://www.poynter.org/product-category/fact-checking/), the [Trust Project](https://thetrustproject.org/), and others. Our TV and Music related vocabularies are heavily influenced by working with the [BBC and the European Broadcasting Union](https://www.bbc.co.uk/ontologies), alongside [the Music ontology](http://musicontology.com/docs/getting-started.html) and [MusicBrainz](https://musicbrainz.org/doc/LinkedBrainz/RDF); our schemas reflect these prior designs. We prefer to collaborate in this way, improving Schema.org incrementally and working to polish, integrate and blend such designs rather than produce our own pure model in isolation. The result may lack global elegance but brings our work into alignment with related efforts worldwide.

We always welcome issues that track usability and readability issues, but encourage a focus on concrete situations (e.g. how to describe repeating events) rather than global philosophical concerns (e.g. whether a Reservation or Action is "really" an Event). We prioritize local coherence (having sensible ways to describe many common situations) over global elegance (having a global theory in which everything has a sensible place). This doesn't mean we never have cleanups, but they are balanced against (and often outweighed by) other considerations.

When we add terms, often into the "Pending" area, we strongly encourage feedback that takes a global perspective: how does a new term relate to others, how could it be used alongside pre-existing patterns, etc. The changes we make during this integration phase reflect such considerations, but are usually expressed through modest rewording, examples, or adjustment to the documentation of type/property links, rather than through major restructuring.

 * Suggestions for improvements are always welcome here - please search for older discussions (including closed issues) before opening a new issue.
 * We particularly value improvements to existing definitions, examples and text, to clarify how schema.org vocabulary is used in practice.
 * Please don't be surprised or offended if you raise an issue proposing new schemas and it is marked by the project team as "[noted](https://github.com/schemaorg/schemaorg/issues?q=is%3Aissue+label%3A%22Closed+and+Noted+%28and+possibly+Queued%29%22+is%3Aclosed)" then closed. We have 100s of issues discussing possible improvements, and to keep things manageable we adopt the convention of noting then closing issues that are not likely to be immediately explored.
 * While many Schema.org improvements have been proposed via GitHub's "[Pull request](https://help.github.com/articles/about-pull-requests/)" mechanism (see also our list of [PRs](https://github.com/schemaorg/schemaorg/pulls)), please do not undertake any substantial development work without agreeing it with the project team here first.
 * All Pull Requests should reference specific issues that they're fixes or solutions for. This lets the schema.org community discuss problems and topics without it being tied too closely to a specific (and easily outdated) proposed fix.
 * Please note that some changes are much easier to make than others: the wording/phrasing in definitions is relatively easy to amend, whereas the exact spelling of a type or property ('Person', 'startDate' etc.) is much more disruptive to change.
 * There are many other projects developing schemas and ontologies for the Web, e.g. [Wikidata](http://wikidata.org/) or the vocabulary projects in the [Linked Data](https://lov.linkeddata.es/dataset/lov/) community. Many of these projects go into more expressive detail than is possible for a project like Schema.org. To keep Schema.org manageable, we have a strong bias towards designs that are grounded in large scale usage on the Web, in particular [usage](https://github.com/schemaorg/schemaorg/issues/652) by data-consuming applications since these in turn motivate data publishers. Other schema initiatives have different priorities and make different tradeoffs.

See more on ["How we work"](https://schema.org/docs/howwework.html)


Software
========

For most collaborators, all you need to know about the software is how to run it. 

The objective of the software is to create a static copy of the Schema.org site, including potential local changes, to inspect and run behind a simple web server on a local system for testing.  In the same way that a production release is deployed to a cloud server, your local version could then be deployed to a virtual machine using gcloud to enable collaboration with others.

Full instructions are available in [SOFTWARE_README.md](software/SOFTWARE_README.md) explaining how to create the initial local copy to work with, then evolve to test out any changes.

Essentially you will need to have a Linux-like (inc  Mac) environment loaded with Python version 3.6 or above. You can then make test builds of schema.org running on your own machine accessible as http://localhost:8080/ or else post them on appspot.com for collaboration. See the [Appengine documentation](https://cloud.google.com/appengine/docs) for details of the relevant gcloud commands.

More detailed information about the software and is use is available in [SOFTWARE_README.md](software/SOFTWARE_README.md).

See also notes in the wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

Formats and standards
=====================

All schemas and examples are in data/ in utf-8 encoded files.

The main schemas file is data/schema.ttl (utf-8)

While developing schemas, using data/sdo-somethinghere-schema.ttl can be useful.

The format is based on W3C RDFS in RDF/Turtle format.

The examples are stored in data/examples.txt (utf-8) and other *.txt files.

As with schemas, data/*examples.txt will also be read. It can be useful to develop
using separate files. When vocabulary is finally integrated into the main repository, schema
data will be merged into schema.org. However examples will stay in separate files, as this
works better with git's file comparison machinery.

The data/releases/ hierarchy is reserved for release snapshots (see https://schema.org/version/).

The ext/*/ hierarchy is reserved for extensions (see https://schema.org/docs/extension.html).


We no longer use github branches for work-in-progress. The main/ branch is our latest candidate. It is not guaranteed to be in a conceptually consistent state, but should stabilize prior to circulation of a release candidate for review.

Notes
=====

This documentation concerns the software codebase rather than schema.org itself.

However do note that labels, comments, and documentation should use US English (in the code
and schemas), if a choice between English variants is needed. Please aim for international
English wherever possible.

See also: https://twitter.com/schemaorg_dev
