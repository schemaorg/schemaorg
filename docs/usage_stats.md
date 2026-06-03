# About Usage Statistics

## What is this?
As the web grows, the way people use this language changes. To help everyone see these
changes, Schema.org is publishing the Public Usage Statistics dataset via a collaboration
with Google.

This dataset looks at a huge sample of the public web to show a big-picture view of how
different Schema.org terms (like "Person", "Product", or "price") are used across millions
of unique websites.

This data is designed to help:

* **Website Owners, Developers and Toolmakers**: See which terms are most popular so you
  can focus on using the ones that have the most impact, use official data to justify your
  work, improve website plugins (like WordPress SEO tools), and build better analysis
  tools.
* **Community Groups and Researchers**: Track how the Schema.org language is growing, see
  what's new, and decide when old terms are no longer needed.

This dataset is compiled from observations within Google's public web crawling
infrastructure and contributed directly to the Schema.org community. By sharing this data
openly on the canonical Schema.org GitHub repository, we want to make the semantic web
more transparent and collaborative for everyone.

## How the Data is Gathered and Cleaned
Google uses an internal pipeline to gather, clean, and share this data:

1. **Gather**: Schema.org term frequencies are measured within Google's public web
   crawling infrastructure. The data is aggregated at the domain level (like example.com),
   not by individual pages. This means if you use the same term on 100 pages of your site,
   it still only counts as one domain using it.
2. **Group**: Instead of showing exact, raw numbers (which change daily and can be noisy),
   websites are grouped into range "buckets" (like "10K - 100K" domains). This keeps the
   data more stable and protects website privacy.
3. **Publish**: An updated file is pushed to GitHub every month.

## The Raw Data Files
The raw files are available on the GitHub site at [Google Public Stats dataset on
GitHub](https://github.com/schemaorg/schemaorg/tree/main/data/public_stats/google). They
are available in JSON and CSV with the same data and in a JSON summary format with
aggregated bucket distributions.

To make it easy for anyone (including independent developers and startups) to use this
data, the files are very simple. The dataset has three main fields:

* **Term Type**: The type of term. This is either `Type` (like "Person" or
  "Event") or `Property` (like "price" or "telephone").
* **URI**: The official URI of the term (for example:
  `http://schema.org/Person`).
* **Domain Count Bucket**: The range of unique domains using the term (for example:
  `100K - 1M` websites).

## Frequently Asked Questions (FAQs)

### Q: Why numerical ranges instead of exact numbers?

* **Filtering Out Daily Noise**: Web crawling isn't perfect. Temporary server issues,
  network slow-downs, or minor website updates can make exact counts jump up and down
  daily. Using ranges gives a much more stable, reliable "big picture" view.
* **Protecting Website Privacy**: Showing exact numbers could allow competitors or bad
  actors to track minor changes on specific websites or reverse-engineer how search
  engines crawl the web.

### Q: Does the data distinguish between different formats like JSON-LD, Microdata, or RDFa?

**A**: No. They are all combined into a single stat. If a website uses JSON-LD on the
homepage and Microdata on product pages, it still only counts as one website using those
terms.

### Q: Why is this updated monthly?

**A**: Web adoption trends change slowly, making monthly updates sufficient to track
meaningful shifts. Furthermore, each release requires manual validation and approval to
ensure data quality and filter out anomalies before publication.

### Q: A term I want to use is in the "< 1K" bucket. Does that mean search engines ignore it?

**A**: Not necessarily. The "< 1K" bucket includes both brand-new terms and highly
specialized terms (like medical or government terms). Because the total number of medical
websites is small compared to the whole internet, these terms will naturally stay in the
lower buckets. However, using them still builds deep authority for your specific niche.

### Q: How representative are these statistics of the entire web?

**A**: No single crawl can capture the entire internet simultaneously, so all web-scale
datasets inherit biases based on the crawler's scope and indexing methodology. These
statistics reflect the web as indexed by Google. This also means that there is no data
captured on robots.txt blocked websites, for instance.

### Q: Why do you aggregate by domain and not URL or number of objects?

**A**: URL counts and number of objects are very heavily influenced by the index
composition in search indices. There would need to be more sampling and complexity to
present this in a more objective manner rather than be biased toward head websites. Domain
count is slightly more universal in at least measuring wide-scale adoption.

### Q: Can other search engines or web archives contribute their own statistics?

**A**: Yes. The data format used for these statistics is fully open and documented in
Schema.org GitHub repository. Schema.org welcomes other search engines and web-scale
crawlers to publish their own adoption statistics in this format so the community can
compare datasets and build a multi-provider view.
