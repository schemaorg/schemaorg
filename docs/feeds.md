# Schema.org Feeds

* Status: Discussion draft
* Contacts: danbri@google.com, guha@google.com
* Discussion: https://github.com/schemaorg/schemaorg/issues/TODO

## Overview

This is a draft of a simple "Schema.org Feeds" specification.

Schema.org can be used to discover Web feeds, and to provide meaningful structure in such feeds. Feeds can provide an alternative way for sites to re-distribute some or all of the data that they can also include via per-page embedding. Feeds also allow sites to add detail to machine readable structured data without adding to the page weight performance challenges of human-facing pages.

The initial emphasis here is on feeds that use Schema.org primarily, rather than formats such as RSS/Atom, Sitemaps XML etc., which are complementary technologies.

## Purpose of this Specification

This specification does not itself impose any specific structure on Feeds beyond introducing/standardizing the notion of Schema.org in stand-alone files rather than embedded in HTML.


# Feed discovery

The main innovation in this document is to define two mechanisms for Schema.org Feed discovery. These are unlikely to be the only mechanisms through which schema.org feeds are found and shared, but provide a baseline for content intended for a general audience.

The schema.org DataFeed type provides an extensible foundation for using Schema.org to describe the location and format of data feeds, regardless of whether the actual feeds use Schema.org.

* Well Known URLs
 * Two (as yet unregistered) Well Known URLs can be used for site-wide discovery of feed URLs, at the domain name level:
 * See Wikipedia for an explanation of the /.well-known/ URL path standard. In brief:
   It is increasingly common for Web-based protocols to require the discovery of policy or other information about a host ("site-wide metadata") before making a request. RFC8615 defines a path prefix in HTTP(S) URIs for these "well-known locations", "/.well-known/".
 * /.well-known/feeddata-general
This gives a site's default representation in structured data formats, typically but not necessarily in JSON-LD format using Schema.org as the base vocabulary. It usually consists of all the structured data that is embedded in public pages on the site. For large data files, this URL could redirect to feeddata-toc, which would describe the set of component files making up the feed.
 * /.well-known/feeddata-toc
This gives a table of contents for a site, typically but not necessarily expressed in Schema.org, with pointers to structured data feeds of various kinds RSS, Atom and other feeds e.g. sitemaps, including different subsets of the larger site, summaries of non-public data feeds. It serves as a machine-readable entry point.

The use of site-wide ".well-known" URLs is not always the most appropriate discovery mechanism. For situations where many independent sites share a common domain name, Schema.org itself (embedded in subsection homepages) can be used to discover the above site descriptions. This could be included alongside other site-level metadata, e.g. the "WebSite" description published for a sitelinks-searchbox.

Two (as yet tentative) schema.org properties can be used with WebSite to point to DataFeed URLs:

  * schema.org/generalFeedLink
  Definition (of a WebSite): "URL of a feed (e.g. expressed as schema.org/DataFeed) for a site that gives its default representation in Schema.org-based formats (typically JSON-LD). Usually consists of all the structured data from public pages on the site."
  * schema.org/feedDataContentsListLink
  Definition (of a Website): "URL of a machine readable feed for a site (typically using Schema.org/DataFeed) that gives a table of content for a site expressed in Schema.org, i.e. descriptions of all the various data feeds on the site, regardless of whether they are in classic/legacy formats (e.g. sitemaps XML; RSS; Atom…) or in Schema.org-oriented formats.


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
