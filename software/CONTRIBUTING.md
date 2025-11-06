# Contributing to Schema.org

See [README](../README.md) for more details, especially on proposing schemas.

Essentials:

* Please join the [Schema.org Community Group](https://www.w3.org/community/schemaorg) over at W3C.
* Note the Schema.org official site (where schemas are published) [terms of service](https://schema.org/docs/terms.html), including CC license details.
* Please don't be offended if we [close your issue](https://github.com/schemaorg/schemaorg/issues/2050). We get 100s of suggestions, and they remain in the issue tracker.
* For software license see the [LICENSE](../LICENSE) file.
* See also our [how we work](http://schema.org/docs/howwework.html) and [repository README](https://github.com/schemaorg/schemaorg/blob/main/README.md) files.
* For recommendations concerning the coding, see the [CODE_README](CODE_README.md) file.

## Creating a Data Pull Request

Before creating a pull request to change the schema,
read the [Improving schemas](../README.md#improving-schemas) section.
If you add new types, or new attributes, please do not edit the files in the main `data` directory,
instead create new files in a the `data/ext/pending` directory named
`issue-XXXX.ttl` and `issue-XXXX-examples.txt` where `XXXX` is the relevant issue number.
The build system will pull in and merge all the files.

### Turtle files

The `.ttl` files are in the [Turtle Syntax](https://en.wikipedia.org/wiki/Turtle_(syntax)).
You can lint the files using the `software/util/reorg.py lint <file>` command.

### Example files

These are text files which are divided into sections: `TYPES`,  `PRE-MARKUP`, `MICRODATA`, `RDFA`, `JSON`.
The python parser is in the [`schemaexamples.py`](SchemaExamples/schemaexamples.py) file.
You need to populate at least the `TYPES` and at least one of the following examples section,
in general it is preferable to prioritise the `JSON` section.

The first value in the `TYPES` line is the key used for this example, use the bug number with a `#` prefix,
the following comma separated values identify the types the examples apply to.

The `PRE-MARKUP` contains example HTML with no sematic annotations.
Use this to show an example of what an un-annotated web page would look like.

The `MICRODATA`  section should contain the same HTML but with microdata annotations.

The `RDFA` section should contain the same HTML with RDFA annotations.

The `JSON` section should contain the JSON-LD data, wrapped in a `<script type="application/ld+json">` tag.


```
TYPES: #000 Thing

PRE-MARKUP:

Introducing the <strong>Fnuffl</strong>.
More information <a href="http://example.com">here</a>.

MICRODATA:

<div itemscope itemtype="https://schema.org/Thing">
Introducing the <strong itemprop="name">Fnuffl</strong>.
More information <a itemprop="url" href="http://example.com/fnuffl">here</a>.
</div>

RDFA:

n/a

JSON:

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Thing",
  "name": "Fnuffl",
  "url": "http://example.com/fnuffl"
}
</script>

```
