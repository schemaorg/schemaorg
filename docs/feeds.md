
# Schema.org Feeds Specification

* Authors: Dan Brickley <danbri@google.com>, Ramanathan V. Guha<guha@google.com>
* Discussion: Welcomed on [Github](https://github.com/schemaorg/schemaorg/issues/2891) or on [public-schemaorg@w3.org](https://lists.w3.org/Archives/Public/public-schemaorg/).
* Status of this document: Discussion proposal only. Experimental implementation welcomed, please do not assume stability.


todo
 * add "pages mentioned in" / "main page for me (on this site)"

## Abstract

This is a draft of a simple "Schema.org Feeds" specification, introducing conventions for site-level rather than inline page-level publication of machine-readable structured data. Future revisions may explore other publication mechanisms, such as per-page files referenced via links.

## Overview

This specification introduces the idea of Schema.org feeds, and introduces some conventions for their discovery. The purpose is to make Schema.org structured data easier to publish, and easier to work with for data-consuming applications.



## Purpose of this Specification

Schema.org has been very successful for publishing per-page structured data. Originally targeting the HTML5 Microdata format, it is now also widely published in JSON-LD 1.0, as well as RDFa 1.1 formats. This success was largely based on the practice of publishing data within ordinary web pages, and on the practice of building richer user-facing applications using this structured data. The purpose of this specification is to define shared conventions for site-level publication and discovery of schema.org-based data, beyond the "page by page" model, in the expectation that doing so will help publishers and consumers of structured data communicate using Schema.org more effectively.


## Background

Schema.org itself is essentially a machine-readable dictionary, and as such, does not tell its users what they should say, or where they should say it. In practice, it has built on a tradition of embedded page-by-page content publishing, providing a machine-readable "site summary" within human-oriented pages across millions of sites. Such pages often repeat information redundantly. The same real-world entity may be mentioned thousands or millions of times on one site, often with the same factual information repeated in each page.

Schema.org schemas are concerned more with summarizing the real-world things and relationships that pages describe, than with describing the hypertext structure of web sites themselves. This has resulted in publishers asking reasonable questions such as:

 * "Should the contact information go in every page, or just our ContactPage? Our opening hours? logo?"
 * "On an e-commerce site, can information that applies to many product offers (e.g. shipping and returns policy details) all reference a common page?"
 * "Should we add markup to every page where something is mentioned, or just its main page?"

The motivation behind this specification is to explore an alternative model of structured data publication that is not tied so strongly to the "page by page" publication model.



# Schema.org Feeds - "Feeds that use Schema.org"

"Feed" in the sense used here, is a general term applicable to data published in the web, generally oriented towards machine-processing rather than humans, and with some suggestion of regular updates. Feeds can provide an alternative way for sites to re-distribute some or all of the data that they can also include via per-page embedding. Feeds also allow sites to add detail to machine readable structured data without adding to the page weight performance challenges of human-facing pages.

Schema.org can both be used to discover Web feeds, and to provide meaningful structure in such feeds. This specification is concerned primarily with feeds of Schema.org data, e.g. that carry roughly the same content that a site might be embedding in its HTML pages, rather than formats such as RSS/Atom, Sitemaps XML etc., which are complementary technologies. In the sense used here, a "Schema.org feed" is a document that uses schema.org vocabulary. This might be in JSON-LD, or other formats.

## Discovery

The main innovation in this document is to define two mechanisms for Schema.org Feed discovery. These are unlikely to be the only mechanisms through which schema.org feeds are found and shared, but provide a baseline for content intended for a general audience. The schema.org [DataFeed](https://schema.org/DataFeed) type provides an extensible foundation for using Schema.org to describe the location and format of data feeds, regardless of whether the actual feeds use Schema.org.

* Well Known URLs (using IETF [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615) URL conventions):
 * Two (as yet unregistered) Well Known URLs can be used for site-wide discovery of feed URLs, at the domain name level:
 * See also [Wikipedia](https://en.wikipedia.org/wiki/List_of_/.well-known/_services_offered_by_webservers). In brief:
   It is increasingly common for Web-based protocols to require the discovery of policy or other information about a host ("site-wide metadata") before making a request. RFC8615 defines a path prefix in HTTP(S) URIs for these "well-known locations", "/.well-known/".
 * /.well-known/feeddata-general
This gives a site's default representation in structured data formats, typically but not necessarily in JSON-LD format using Schema.org as the base vocabulary. It usually consists of all the structured data that is embedded in public pages on the site. For large data files, this URL could redirect to feeddata-toc, which would describe the set of component files making up the feed.
 * /.well-known/feeddata-toc
This gives a table of contents for a site, typically but not necessarily expressed in Schema.org, with pointers to structured data feeds of various kinds. Beyond Schema.org-based files, this could potentially also reference RSS/Atom and other feeds e.g. sitemaps, including different subsets of the larger site, summaries of non-public data feeds. It serves as a machine-readable entry point. The relationship to other relevant formats would need careful discussion.

The use of site-wide ".well-known" URLs is not always the most appropriate discovery mechanism. For situations where many independent sites share a common domain name, Schema.org itself (embedded in subsection homepages) can be used to discover the above site descriptions. This could be included alongside other site-level metadata, e.g. a "WebSite" description describing URLs for search actions, or contact, logo etc information.

Two (as yet tentative) schema.org properties can be used with WebSite to point to DataFeed URLs (corresponding to the .well-known/ services outlined above):

  * schema.org/generalFeedLink
  Definition (of a WebSite): "URL of a feed (e.g. expressed as schema.org/DataFeed) for a site that gives its default representation in Schema.org-based formats (typically JSON-LD). Usually consists of all the structured data from public pages on the site."
  * schema.org/feedDataContentsListLink
  Definition (of a Website): "URL of a machine readable feed for a site (typically using Schema.org/DataFeed) that gives a table of content for a site expressed in Schema.org, i.e. descriptions of all the various data feeds on the site, regardless of whether they are in classic/legacy formats (e.g. sitemaps XML; RSS; Atom…) or in Schema.org-oriented formats.

  This specification does not itself impose any specific structure on Feeds beyond introducing/standardizing the notion of Schema.org in stand-alone files rather than embedded in HTML.


## Advanced Topics (potential future )

These topics could be explored in future revisions of this document.

### Feed Validation

Building on the notion of Schema.org Feeds, we can introduce the notion of Schema.org Feeds that validate to a specific "vertical" data structure, specified using W3C SHACL or ShEx. For example,
a "conformsTo" property might indicate machine-readable validation rules defining the expected content of the feed.

### Other topics

 * Dataset diffs using https://schema.org/DataFeedItem can avoid need to re-transfer huge feeds repeatedly, but comes with subtle cornercases.
 * Pagination - idea of schema json-ld data being served (per page or in larger chunks) from a different URL instead of embedded via script tag.
 * per-page schema.org in separate files rather than pages.
 * mechanisms to associate feeds or their parts with pages (beyond the /url property).
