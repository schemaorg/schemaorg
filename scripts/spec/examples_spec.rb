$:.unshift File.expand_path("..", __FILE__)
require 'spec_helper'

describe "Examples" do
  before(:all) {RDF::Reasoner.apply(:rdfs, :owl, :schema)}

  # Examples from sdo-mainEntity-examples.txt
  specify("sdo-mainEntity-examples.txt[12] - mainEntity-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntity-1-microdata.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[23] - mainEntity-1 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntity-1-rdfa.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[27] - mainEntity-1 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntity-1-jsonld.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[56] - mainEntity-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntity-2-microdata.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[65] - mainEntityOfPage-2 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntityOfPage-2-rdfa.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[74] - mainEntityOfPage-2 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntityOfPage-2-jsonld.html").to lint_cleanly}

  # Examples from sdo-invoice-examples.txt
  specify("sdo-invoice-examples.txt[18] - invoice-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/invoice-1-microdata.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[44] - Invoice-BankOrCreditUnion-Person-PriceSpecification-3 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-BankOrCreditUnion-Person-PriceSpecification-3-rdfa.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[70] - Invoice-BankOrCreditUnion-Person-PriceSpecification-3 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-BankOrCreditUnion-Person-PriceSpecification-3-jsonld.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[119] - Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4-microdata.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[158] - Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4-rdfa.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[197] - Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4-jsonld.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[263] - Order-OrderItem-Organization-Person-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Order-OrderItem-Organization-Person-5-microdata.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[298] - Order-OrderItem-Organization-Person-5 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Order-OrderItem-Organization-Person-5-rdfa.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[333] - Order-OrderItem-Organization-Person-5 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Order-OrderItem-Organization-Person-5-jsonld.html").to lint_cleanly}

  # Examples from sdo-course-examples.txt
  specify("sdo-course-examples.txt[22] - Course1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course1-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[26] - Course-CourseInstance-hasCourseInstance-courseMode-6 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-6-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[48] - Course-CourseInstance-hasCourseInstance-courseMode-6 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-6-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[108] - Course2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course2-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[113] - Course-CourseInstance-hasCourseInstance-courseMode-7 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-7-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[155] - Course-CourseInstance-hasCourseInstance-courseMode-7 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-7-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[209] - Course3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course3-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[214] - Course-CourseInstance-hasCourseInstance-courseMode-8 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-8-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[242] - Course-CourseInstance-hasCourseInstance-courseMode-8 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-8-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[290] - Course4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course4-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[295] - educationalCredentialAwarded-9 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-9-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[305] - educationalCredentialAwarded-9 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-9-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[332] - Course5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course5-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[337] - educationalCredentialAwarded-10 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-10-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[352] - educationalCredentialAwarded-10 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-10-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[391] - Course6 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course6-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[396] - instructor-provider-11 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/instructor-provider-11-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[427] - instructor-provider-11 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/instructor-provider-11-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[480] - Course7 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course7-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[485] - Course-courseCode-provider-12 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-courseCode-provider-12-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[503] - Course-courseCode-provider-12 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-courseCode-provider-12-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[528] - comma-separated-list-here replace  with content.-13 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/comma-separated-list-here replace  with content.-13-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[533] - comma-separated-list-here replace  with content.-13 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/comma-separated-list-here replace  with content.-13-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[537] - comma-separated-list-here replace  with content.-13 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/comma-separated-list-here replace  with content.-13-jsonld.html").to lint_cleanly}

  # Examples from sdo-lrmi-examples.txt
  specify("sdo-lrmi-examples.txt[14] - lrmi-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/lrmi-1-microdata.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[36] - learningResourceType-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-audience-EducationalAudience-educationalRole-14 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/learningResourceType-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-audience-EducationalAudience-educationalRole-14-rdfa.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[59] - learningResourceType-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-audience-EducationalAudience-educationalRole-14 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/learningResourceType-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-audience-EducationalAudience-educationalRole-14-jsonld.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[116] - lrmi-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/lrmi-2-microdata.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[174] - typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-15 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-15-rdfa.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[232] - typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-15 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-15-jsonld.html").to lint_cleanly}

  # Examples from sdo-property-value-examples.txt
  specify("sdo-property-value-examples.txt[20] - exif (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/exif-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[54] - ImageObject-PropertyValue-additionalProperty-16 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-PropertyValue-additionalProperty-16-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[88] - ImageObject-PropertyValue-additionalProperty-16 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-PropertyValue-additionalProperty-16-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[146] - pointvalue-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/pointvalue-1-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[159] - PropertyValue-additionalProperty-17 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-17-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[162] - PropertyValue-additionalProperty-17 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-17-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[181] - pointvalue-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/pointvalue-1-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[194] - PropertyValue-additionalProperty-18 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-18-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[197] - PropertyValue-additionalProperty-18 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-18-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[216] - pointvalue-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/pointvalue-3-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[229] - PropertyValue-additionalProperty-19 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-19-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[232] - PropertyValue-additionalProperty-19 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-19-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[253] - range-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/range-1-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[267] - PropertyValue-additionalProperty-20 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-20-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[270] - PropertyValue-additionalProperty-20 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-20-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[290] - openinterval (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/openinterval-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[304] - PropertyValue-additionalProperty-21 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-21-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[307] - PropertyValue-additionalProperty-21 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-21-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[328] - intervals (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/intervals-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[342] - PropertyValue-additionalProperty-22 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-22-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[345] - PropertyValue-additionalProperty-22 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-22-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[366] - range-and-enumeration (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/range-and-enumeration-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[380] - PropertyValue-23 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-23-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[383] - PropertyValue-23 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-23-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[401] - boolean (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/boolean-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[413] - PropertyValue-additionalProperty-24 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-24-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[416] - PropertyValue-additionalProperty-24 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-24-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[434] - qualitative-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/qualitative-1-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[446] - PropertyValue-additionalProperty-25 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-25-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[449] - PropertyValue-additionalProperty-25 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-25-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[469] - qualitative-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/qualitative-2-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[482] - PropertyValue-additionalProperty-26 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-26-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[485] - PropertyValue-additionalProperty-26 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-26-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[506] - property-id-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/property-id-1-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[520] - PropertyValue-additionalProperty-27 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-27-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[523] - PropertyValue-additionalProperty-27 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-27-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[544] - property-id-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/property-id-2-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[558] - PropertyValue-additionalProperty-28 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-28-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[561] - PropertyValue-additionalProperty-28 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-28-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[587] - valueref (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/valueref-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[606] - PropertyValue-additionalProperty-29 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-29-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[609] - PropertyValue-additionalProperty-29 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-29-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[633] - ratios (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ratios-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[650] - PropertyValue-additionalProperty-30 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-30-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[653] - PropertyValue-additionalProperty-30 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-30-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[679] - grouping (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/grouping-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[700] - PropertyValue-additionalProperty-31 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-31-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[703] - PropertyValue-additionalProperty-31 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-31-jsonld.html").to lint_cleanly}

  # Examples from sdo-periodical-examples.txt
  specify("sdo-periodical-examples.txt[20] - bib-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/bib-1-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[48] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[76] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[144] - bib-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/bib-2-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[189] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[232] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[295] - bib-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/bib-3-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[344] - Book-PublicationVolume-34 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-PublicationVolume-34-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[393] - Book-PublicationVolume-34 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-PublicationVolume-34-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[475] - bib-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/bib-4-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[497] - PublicationIssue-PublicationVolume-ScholarlyArticle-35 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PublicationIssue-PublicationVolume-ScholarlyArticle-35-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[519] - PublicationIssue-PublicationVolume-ScholarlyArticle-35 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PublicationIssue-PublicationVolume-ScholarlyArticle-35-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[587] - bib-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/bib-5-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[629] - exampleOfWork-workExample-36 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/exampleOfWork-workExample-36-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[673] - exampleOfWork-workExample-36 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/exampleOfWork-workExample-36-jsonld.html").to lint_cleanly}

  # Examples from sdo-datafeed-examples.txt
  specify("sdo-datafeed-examples.txt[14] - datafeed-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/datafeed-1-microdata.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[18] - DataFeed-37 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DataFeed-37-rdfa.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[22] - DataFeed-37 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DataFeed-37-jsonld.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[60] - datafeed-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/datafeed-2-microdata.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[64] - MobileApplication-DataFeed-supportingData-38 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MobileApplication-DataFeed-supportingData-38-rdfa.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[68] - MobileApplication-DataFeed-supportingData-38 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MobileApplication-DataFeed-supportingData-38-jsonld.html").to lint_cleanly}

  # Examples from sdo-sponsor-examples.txt
  specify("sdo-sponsor-examples.txt[27] - sponsor-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sponsor-1-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[71] - Event-39 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-39-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[121] - Event-39 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-39-jsonld.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[178] - sponsor-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sponsor-2-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[186] - Person-40 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-40-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[194] - Person-40 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-40-jsonld.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[215] - sponsor-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sponsor-3-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[224] - Person-41 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-41-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[233] - Person-41 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-41-jsonld.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[256] - sponsor-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sponsor-4-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[266] - Organization-42 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-42-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[277] - Organization-42 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-42-jsonld.html").to lint_cleanly}

  # Examples from sdo-menu-examples.txt
  specify("sdo-menu-examples.txt[10] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43-microdata.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[14] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43-rdfa.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[18] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43-jsonld.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[78] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44-microdata.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[82] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44-rdfa.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[86] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44-jsonld.html").to lint_cleanly}

  # Examples from sdo-tv-listing-examples.txt
  specify("sdo-tv-listing-examples.txt[6] - tv-listing1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tv-listing1-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[17] - Organization-BroadcastService-45 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-45-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[29] - Organization-BroadcastService-45 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-45-jsonld.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[51] - tv-listing2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tv-listing2-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[68] - Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[86] - Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46-jsonld.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[117] - tv-listing3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tv-listing3-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[135] - BroadcastEvent-BroadcastService-TVEpisode-47 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-BroadcastService-TVEpisode-47-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[154] - BroadcastEvent-BroadcastService-TVEpisode-47 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-BroadcastService-TVEpisode-47-jsonld.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[184] - tv-listing4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tv-listing4-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[206] - BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[230] - BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48-jsonld.html").to lint_cleanly}

  # Examples from sdo-tourism-examples.txt
  specify("sdo-tourism-examples.txt[13] - tourism-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-1-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[28] - TouristAttraction-isAccessibleForFree-49 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-49-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[43] - TouristAttraction-isAccessibleForFree-49 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-49-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[70] - tourism-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-2-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[96] - AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[122] - AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[146] - tourism-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-3-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[166] - TouristAttraction-availableLanguage-51 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-availableLanguage-51-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[186] - TouristAttraction-availableLanguage-51 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-availableLanguage-51-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[213] - tourism-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-4-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[239] - TouristAttraction-touristType-Museum-52 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Museum-52-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[264] - TouristAttraction-touristType-Museum-52 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Museum-52-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[292] - tourism-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-5-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[304] - TouristAttraction-publicAccess-53 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-publicAccess-53-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[316] - TouristAttraction-publicAccess-53 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-publicAccess-53-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[339] - tourism-6 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-6-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[356] - TouristAttraction-event-Event-54 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-event-Event-54-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[373] - TouristAttraction-event-Event-54 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-event-Event-54-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[407] - tourism-7 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-7-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[433] - TouristAttraction-isAccessibleForFree-55 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-55-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[456] - TouristAttraction-isAccessibleForFree-55 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-55-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[523] - tourism-8 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-8-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[554] - TouristAttraction-touristType-isAccessibleForFree-Cemetery-56 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-isAccessibleForFree-Cemetery-56-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[584] - TouristAttraction-touristType-isAccessibleForFree-Cemetery-56 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-isAccessibleForFree-Cemetery-56-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[639] - tourism-9 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-9-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[667] - TouristAttraction-touristType-Winery-57 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Winery-57-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[694] - TouristAttraction-touristType-Winery-57 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Winery-57-jsonld.html").to lint_cleanly}

  # Examples from sdo-map-examples.txt
  specify("sdo-map-examples.txt[10] - map-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/map-1-microdata.html").to lint_cleanly}
  specify("sdo-map-examples.txt[20] - Map-VenueMap-58 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Map-VenueMap-58-rdfa.html").to lint_cleanly}
  specify("sdo-map-examples.txt[30] - Map-VenueMap-58 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Map-VenueMap-58-jsonld.html").to lint_cleanly}

  # Examples from examples.txt
  specify("examples.txt[22] - eg-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-1-microdata.html").to lint_cleanly}
  specify("examples.txt[52] - Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59-rdfa.html").to lint_cleanly}
  specify("examples.txt[82] - Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59-jsonld.html").to lint_cleanly}
  specify("examples.txt[118] - eg2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg2-microdata.html").to lint_cleanly}
  specify("examples.txt[132] - Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60-rdfa.html").to lint_cleanly}
  specify("examples.txt[146] - Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60-jsonld.html").to lint_cleanly}
  specify("examples.txt[171] - eg-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-3-microdata.html").to lint_cleanly}
  specify("examples.txt[179] - Painting-genre-61 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-genre-61-rdfa.html").to lint_cleanly}
  specify("examples.txt[186] - Painting-genre-61 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-genre-61-jsonld.html").to lint_cleanly}
  specify("examples.txt[217] - eg-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-4-microdata.html").to lint_cleanly}
  specify("examples.txt[252] - Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62-rdfa.html").to lint_cleanly}
  specify("examples.txt[287] - Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62-jsonld.html").to lint_cleanly}
  specify("examples.txt[330] - eg-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-5-microdata.html").to lint_cleanly}
  specify("examples.txt[343] - Place-GeoCoordinates-latitude-longitude-geo-63 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-GeoCoordinates-latitude-longitude-geo-63-rdfa.html").to lint_cleanly}
  specify("examples.txt[356] - Place-GeoCoordinates-latitude-longitude-geo-63 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-GeoCoordinates-latitude-longitude-geo-63-jsonld.html").to lint_cleanly}
  specify("examples.txt[383] - eg-6 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-6-microdata.html").to lint_cleanly}
  specify("examples.txt[402] - MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64-rdfa.html").to lint_cleanly}
  specify("examples.txt[421] - MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64-jsonld.html").to lint_cleanly}
  specify("examples.txt[453] - eg-7 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-7-microdata.html").to lint_cleanly}
  specify("examples.txt[484] - Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65-rdfa.html").to lint_cleanly}
  specify("examples.txt[514] - Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65-jsonld.html").to lint_cleanly}
  specify("examples.txt[569] - eg-8 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-8-microdata.html").to lint_cleanly}
  specify("examples.txt[599] - NGO-66 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NGO-66-rdfa.html").to lint_cleanly}
  specify("examples.txt[629] - NGO-66 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NGO-66-jsonld.html").to lint_cleanly}
  specify("examples.txt[676] - eg-9 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-9-microdata.html").to lint_cleanly}
  specify("examples.txt[704] - Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67-rdfa.html").to lint_cleanly}
  specify("examples.txt[732] - Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67-jsonld.html").to lint_cleanly}
  specify("examples.txt[784] - eg-10 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-10-microdata.html").to lint_cleanly}
  specify("examples.txt[841] - Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68-rdfa.html").to lint_cleanly}
  specify("examples.txt[896] - Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68-jsonld.html").to lint_cleanly}
  specify("examples.txt[965] - eg-11 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-11-microdata.html").to lint_cleanly}
  specify("examples.txt[996] - Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69-rdfa.html").to lint_cleanly}
  specify("examples.txt[1019] - Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69-jsonld.html").to lint_cleanly}
  specify("examples.txt[1086] - eg-12 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-12-microdata.html").to lint_cleanly}
  specify("examples.txt[1145] - WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70-rdfa.html").to lint_cleanly}
  specify("examples.txt[1204] - WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70-jsonld.html").to lint_cleanly}
  specify("examples.txt[1291] - eg-13 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-13-microdata.html").to lint_cleanly}
  specify("examples.txt[1337] - Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71-rdfa.html").to lint_cleanly}
  specify("examples.txt[1382] - Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71-jsonld.html").to lint_cleanly}
  specify("examples.txt[1477] - eg-14 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-14-microdata.html").to lint_cleanly}
  specify("examples.txt[1538] - VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72-rdfa.html").to lint_cleanly}
  specify("examples.txt[1598] - VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72-jsonld.html").to lint_cleanly}
  specify("examples.txt[1681] - ItemList-73 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-73-microdata.html").to lint_cleanly}
  specify("examples.txt[1692] - ItemList-73 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-73-rdfa.html").to lint_cleanly}
  specify("examples.txt[1703] - ItemList-73 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-73-jsonld.html").to lint_cleanly}
  specify("examples.txt[1732] - Movie-74 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-74-microdata.html").to lint_cleanly}
  specify("examples.txt[1769] - Movie-74 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-74-rdfa.html").to lint_cleanly}
  specify("examples.txt[1806] - Movie-74 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-74-jsonld.html").to lint_cleanly}
  specify("examples.txt[1870] - Table-75 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Table-75-microdata.html").to lint_cleanly}
  specify("examples.txt[1888] - Table-75 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Table-75-rdfa.html").to lint_cleanly}
  specify("examples.txt[1906] - Table-75 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Table-75-jsonld.html").to lint_cleanly}
  specify("examples.txt[1926] - PostalAddress-76 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-76-microdata.html").to lint_cleanly}
  specify("examples.txt[1937] - PostalAddress-76 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-76-rdfa.html").to lint_cleanly}
  specify("examples.txt[1948] - PostalAddress-76 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-76-jsonld.html").to lint_cleanly}
  specify("examples.txt[1975] - CreativeWork-ContentRating-77 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-ContentRating-77-microdata.html").to lint_cleanly}
  specify("examples.txt[1986] - CreativeWork-ContentRating-77 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-ContentRating-77-rdfa.html").to lint_cleanly}
  specify("examples.txt[1997] - CreativeWork-ContentRating-77 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-ContentRating-77-jsonld.html").to lint_cleanly}
  specify("examples.txt[2023] - ImageObject-78 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-78-microdata.html").to lint_cleanly}
  specify("examples.txt[2040] - ImageObject-78 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-78-rdfa.html").to lint_cleanly}
  specify("examples.txt[2056] - ImageObject-78 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-78-jsonld.html").to lint_cleanly}
  specify("examples.txt[2083] - MusicPlaylist-79 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicPlaylist-79-microdata.html").to lint_cleanly}
  specify("examples.txt[2130] - MusicPlaylist-79 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicPlaylist-79-rdfa.html").to lint_cleanly}
  specify("examples.txt[2177] - MusicPlaylist-79 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicPlaylist-79-jsonld.html").to lint_cleanly}
  specify("examples.txt[2238] - InteractionCounter-Article-80 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-Article-80-microdata.html").to lint_cleanly}
  specify("examples.txt[2257] - InteractionCounter-Article-80 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-Article-80-rdfa.html").to lint_cleanly}
  specify("examples.txt[2277] - InteractionCounter-Article-80 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-Article-80-jsonld.html").to lint_cleanly}
  specify("examples.txt[2315] - CivicStructure-Place-81 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CivicStructure-Place-81-microdata.html").to lint_cleanly}
  specify("examples.txt[2325] - CivicStructure-Place-81 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CivicStructure-Place-81-rdfa.html").to lint_cleanly}
  specify("examples.txt[2335] - CivicStructure-Place-81 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CivicStructure-Place-81-jsonld.html").to lint_cleanly}
  specify("examples.txt[2361] - EducationalOrganization-82 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOrganization-82-microdata.html").to lint_cleanly}
  specify("examples.txt[2379] - EducationalOrganization-82 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOrganization-82-rdfa.html").to lint_cleanly}
  specify("examples.txt[2397] - EducationalOrganization-82 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOrganization-82-jsonld.html").to lint_cleanly}
  specify("examples.txt[2436] - TVSeries-TVSeason-TVEpisode-83 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-83-microdata.html").to lint_cleanly}
  specify("examples.txt[2466] - TVSeries-TVSeason-TVEpisode-83 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-83-rdfa.html").to lint_cleanly}
  specify("examples.txt[2496] - TVSeries-TVSeason-TVEpisode-83 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-83-jsonld.html").to lint_cleanly}
  specify("examples.txt[2550] - MusicAlbum-84 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-84-microdata.html").to lint_cleanly}
  specify("examples.txt[2577] - MusicAlbum-84 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-84-rdfa.html").to lint_cleanly}
  specify("examples.txt[2604] - MusicAlbum-84 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-84-jsonld.html").to lint_cleanly}
  specify("examples.txt[2687] - JobPosting-85 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-85-microdata.html").to lint_cleanly}
  specify("examples.txt[2752] - JobPosting-85 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-85-rdfa.html").to lint_cleanly}
  specify("examples.txt[2817] - JobPosting-85 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-85-jsonld.html").to lint_cleanly}
  specify("examples.txt[2860] - IndividualProduct-86 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IndividualProduct-86-microdata.html").to lint_cleanly}
  specify("examples.txt[2872] - IndividualProduct-86 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IndividualProduct-86-rdfa.html").to lint_cleanly}
  specify("examples.txt[2884] - IndividualProduct-86 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IndividualProduct-86-jsonld.html").to lint_cleanly}
  specify("examples.txt[2907] - SomeProducts-87 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SomeProducts-87-microdata.html").to lint_cleanly}
  specify("examples.txt[2922] - SomeProducts-87 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SomeProducts-87-rdfa.html").to lint_cleanly}
  specify("examples.txt[2937] - SomeProducts-87 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SomeProducts-87-jsonld.html").to lint_cleanly}
  specify("examples.txt[2960] - ProductModel-88 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProductModel-88-microdata.html").to lint_cleanly}
  specify("examples.txt[2983] - ProductModel-88 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProductModel-88-rdfa.html").to lint_cleanly}
  specify("examples.txt[3006] - ProductModel-88 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProductModel-88-jsonld.html").to lint_cleanly}
  specify("examples.txt[3026] - Action-89 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-89-microdata.html").to lint_cleanly}
  specify("examples.txt[3030] - Action-89 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-89-rdfa.html").to lint_cleanly}
  specify("examples.txt[3034] - Action-89 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-89-jsonld.html").to lint_cleanly}
  specify("examples.txt[3070] - Action-90 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-90-microdata.html").to lint_cleanly}
  specify("examples.txt[3074] - Action-90 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-90-rdfa.html").to lint_cleanly}
  specify("examples.txt[3078] - Action-90 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-90-jsonld.html").to lint_cleanly}
  specify("examples.txt[3106] - AchieveAction-91 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AchieveAction-91-microdata.html").to lint_cleanly}
  specify("examples.txt[3110] - AchieveAction-91 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AchieveAction-91-rdfa.html").to lint_cleanly}
  specify("examples.txt[3114] - AchieveAction-91 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AchieveAction-91-jsonld.html").to lint_cleanly}
  specify("examples.txt[3138] - LoseAction-92 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoseAction-92-microdata.html").to lint_cleanly}
  specify("examples.txt[3142] - LoseAction-92 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoseAction-92-rdfa.html").to lint_cleanly}
  specify("examples.txt[3146] - LoseAction-92 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoseAction-92-jsonld.html").to lint_cleanly}
  specify("examples.txt[3174] - TieAction-93 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TieAction-93-microdata.html").to lint_cleanly}
  specify("examples.txt[3178] - TieAction-93 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TieAction-93-rdfa.html").to lint_cleanly}
  specify("examples.txt[3182] - TieAction-93 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TieAction-93-jsonld.html").to lint_cleanly}
  specify("examples.txt[3210] - WinAction-94 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WinAction-94-microdata.html").to lint_cleanly}
  specify("examples.txt[3214] - WinAction-94 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WinAction-94-rdfa.html").to lint_cleanly}
  specify("examples.txt[3218] - WinAction-94 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WinAction-94-jsonld.html").to lint_cleanly}
  specify("examples.txt[3242] - AssessAction-95 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssessAction-95-microdata.html").to lint_cleanly}
  specify("examples.txt[3246] - AssessAction-95 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssessAction-95-rdfa.html").to lint_cleanly}
  specify("examples.txt[3250] - AssessAction-95 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssessAction-95-jsonld.html").to lint_cleanly}
  specify("examples.txt[3274] - ChooseAction-96 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-96-microdata.html").to lint_cleanly}
  specify("examples.txt[3278] - ChooseAction-96 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-96-rdfa.html").to lint_cleanly}
  specify("examples.txt[3282] - ChooseAction-96 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-96-jsonld.html").to lint_cleanly}
  specify("examples.txt[3316] - ChooseAction-97 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-97-microdata.html").to lint_cleanly}
  specify("examples.txt[3320] - ChooseAction-97 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-97-rdfa.html").to lint_cleanly}
  specify("examples.txt[3324] - ChooseAction-97 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-97-jsonld.html").to lint_cleanly}
  specify("examples.txt[3349] - VoteAction-98 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VoteAction-98-microdata.html").to lint_cleanly}
  specify("examples.txt[3353] - VoteAction-98 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VoteAction-98-rdfa.html").to lint_cleanly}
  specify("examples.txt[3357] - VoteAction-98 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VoteAction-98-jsonld.html").to lint_cleanly}
  specify("examples.txt[3381] - IgnoreAction-99 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-99-microdata.html").to lint_cleanly}
  specify("examples.txt[3385] - IgnoreAction-99 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-99-rdfa.html").to lint_cleanly}
  specify("examples.txt[3389] - IgnoreAction-99 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-99-jsonld.html").to lint_cleanly}
  specify("examples.txt[3413] - IgnoreAction-100 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-100-microdata.html").to lint_cleanly}
  specify("examples.txt[3417] - IgnoreAction-100 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-100-rdfa.html").to lint_cleanly}
  specify("examples.txt[3421] - IgnoreAction-100 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-100-jsonld.html").to lint_cleanly}
  specify("examples.txt[3449] - IgnoreAction-101 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-101-microdata.html").to lint_cleanly}
  specify("examples.txt[3453] - IgnoreAction-101 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-101-rdfa.html").to lint_cleanly}
  specify("examples.txt[3457] - IgnoreAction-101 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-101-jsonld.html").to lint_cleanly}
  specify("examples.txt[3488] - ReactAction-102 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReactAction-102-microdata.html").to lint_cleanly}
  specify("examples.txt[3492] - ReactAction-102 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReactAction-102-rdfa.html").to lint_cleanly}
  specify("examples.txt[3496] - ReactAction-102 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReactAction-102-jsonld.html").to lint_cleanly}
  specify("examples.txt[3520] - AgreeAction-103 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AgreeAction-103-microdata.html").to lint_cleanly}
  specify("examples.txt[3524] - AgreeAction-103 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AgreeAction-103-rdfa.html").to lint_cleanly}
  specify("examples.txt[3528] - AgreeAction-103 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AgreeAction-103-jsonld.html").to lint_cleanly}
  specify("examples.txt[3556] - DisagreeAction-104 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DisagreeAction-104-microdata.html").to lint_cleanly}
  specify("examples.txt[3560] - DisagreeAction-104 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DisagreeAction-104-rdfa.html").to lint_cleanly}
  specify("examples.txt[3564] - DisagreeAction-104 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DisagreeAction-104-jsonld.html").to lint_cleanly}
  specify("examples.txt[3596] - DislikeAction-105 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DislikeAction-105-microdata.html").to lint_cleanly}
  specify("examples.txt[3600] - DislikeAction-105 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DislikeAction-105-rdfa.html").to lint_cleanly}
  specify("examples.txt[3604] - DislikeAction-105 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DislikeAction-105-jsonld.html").to lint_cleanly}
  specify("examples.txt[3632] - EndorseAction-106 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EndorseAction-106-microdata.html").to lint_cleanly}
  specify("examples.txt[3636] - EndorseAction-106 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EndorseAction-106-rdfa.html").to lint_cleanly}
  specify("examples.txt[3640] - EndorseAction-106 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EndorseAction-106-jsonld.html").to lint_cleanly}
  specify("examples.txt[3664] - LikeAction-107 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LikeAction-107-microdata.html").to lint_cleanly}
  specify("examples.txt[3668] - LikeAction-107 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LikeAction-107-rdfa.html").to lint_cleanly}
  specify("examples.txt[3672] - LikeAction-107 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LikeAction-107-jsonld.html").to lint_cleanly}
  specify("examples.txt[3700] - WantAction-108 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WantAction-108-microdata.html").to lint_cleanly}
  specify("examples.txt[3704] - WantAction-108 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WantAction-108-rdfa.html").to lint_cleanly}
  specify("examples.txt[3708] - WantAction-108 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WantAction-108-jsonld.html").to lint_cleanly}
  specify("examples.txt[3736] - ReviewAction-109 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReviewAction-109-microdata.html").to lint_cleanly}
  specify("examples.txt[3740] - ReviewAction-109 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReviewAction-109-rdfa.html").to lint_cleanly}
  specify("examples.txt[3744] - ReviewAction-109 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReviewAction-109-jsonld.html").to lint_cleanly}
  specify("examples.txt[3776] - ConsumeAction-110 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConsumeAction-110-microdata.html").to lint_cleanly}
  specify("examples.txt[3780] - ConsumeAction-110 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConsumeAction-110-rdfa.html").to lint_cleanly}
  specify("examples.txt[3784] - ConsumeAction-110 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConsumeAction-110-jsonld.html").to lint_cleanly}
  specify("examples.txt[3808] - DrinkAction-111 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrinkAction-111-microdata.html").to lint_cleanly}
  specify("examples.txt[3812] - DrinkAction-111 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrinkAction-111-rdfa.html").to lint_cleanly}
  specify("examples.txt[3816] - DrinkAction-111 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrinkAction-111-jsonld.html").to lint_cleanly}
  specify("examples.txt[3840] - EatAction-112 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EatAction-112-microdata.html").to lint_cleanly}
  specify("examples.txt[3844] - EatAction-112 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EatAction-112-rdfa.html").to lint_cleanly}
  specify("examples.txt[3848] - EatAction-112 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EatAction-112-jsonld.html").to lint_cleanly}
  specify("examples.txt[3872] - InstallAction-113 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InstallAction-113-microdata.html").to lint_cleanly}
  specify("examples.txt[3876] - InstallAction-113 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InstallAction-113-rdfa.html").to lint_cleanly}
  specify("examples.txt[3880] - InstallAction-113 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InstallAction-113-jsonld.html").to lint_cleanly}
  specify("examples.txt[3904] - ListenAction-114 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-114-microdata.html").to lint_cleanly}
  specify("examples.txt[3908] - ListenAction-114 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-114-rdfa.html").to lint_cleanly}
  specify("examples.txt[3912] - ListenAction-114 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-114-jsonld.html").to lint_cleanly}
  specify("examples.txt[3936] - ListenAction-115 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-115-microdata.html").to lint_cleanly}
  specify("examples.txt[3940] - ListenAction-115 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-115-rdfa.html").to lint_cleanly}
  specify("examples.txt[3944] - ListenAction-115 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-115-jsonld.html").to lint_cleanly}
  specify("examples.txt[3968] - ListenAction-116 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-116-microdata.html").to lint_cleanly}
  specify("examples.txt[3972] - ListenAction-116 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-116-rdfa.html").to lint_cleanly}
  specify("examples.txt[3976] - ListenAction-116 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-116-jsonld.html").to lint_cleanly}
  specify("examples.txt[4000] - ReadAction-117 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-117-microdata.html").to lint_cleanly}
  specify("examples.txt[4004] - ReadAction-117 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-117-rdfa.html").to lint_cleanly}
  specify("examples.txt[4008] - ReadAction-117 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-117-jsonld.html").to lint_cleanly}
  specify("examples.txt[4032] - ReadAction-118 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-118-microdata.html").to lint_cleanly}
  specify("examples.txt[4036] - ReadAction-118 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-118-rdfa.html").to lint_cleanly}
  specify("examples.txt[4040] - ReadAction-118 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-118-jsonld.html").to lint_cleanly}
  specify("examples.txt[4064] - ReadAction-119 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-119-microdata.html").to lint_cleanly}
  specify("examples.txt[4068] - ReadAction-119 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-119-rdfa.html").to lint_cleanly}
  specify("examples.txt[4072] - ReadAction-119 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-119-jsonld.html").to lint_cleanly}
  specify("examples.txt[4096] - ReadAction-120 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-120-microdata.html").to lint_cleanly}
  specify("examples.txt[4100] - ReadAction-120 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-120-rdfa.html").to lint_cleanly}
  specify("examples.txt[4104] - ReadAction-120 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-120-jsonld.html").to lint_cleanly}
  specify("examples.txt[4128] - UseAction-121 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UseAction-121-microdata.html").to lint_cleanly}
  specify("examples.txt[4132] - UseAction-121 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UseAction-121-rdfa.html").to lint_cleanly}
  specify("examples.txt[4136] - UseAction-121 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UseAction-121-jsonld.html").to lint_cleanly}
  specify("examples.txt[4160] - WearAction-122 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WearAction-122-microdata.html").to lint_cleanly}
  specify("examples.txt[4164] - WearAction-122 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WearAction-122-rdfa.html").to lint_cleanly}
  specify("examples.txt[4168] - WearAction-122 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WearAction-122-jsonld.html").to lint_cleanly}
  specify("examples.txt[4192] - ViewAction-123 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-123-microdata.html").to lint_cleanly}
  specify("examples.txt[4196] - ViewAction-123 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-123-rdfa.html").to lint_cleanly}
  specify("examples.txt[4200] - ViewAction-123 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-123-jsonld.html").to lint_cleanly}
  specify("examples.txt[4224] - ViewAction-124 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-124-microdata.html").to lint_cleanly}
  specify("examples.txt[4228] - ViewAction-124 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-124-rdfa.html").to lint_cleanly}
  specify("examples.txt[4232] - ViewAction-124 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-124-jsonld.html").to lint_cleanly}
  specify("examples.txt[4256] - ViewAction-125 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-125-microdata.html").to lint_cleanly}
  specify("examples.txt[4260] - ViewAction-125 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-125-rdfa.html").to lint_cleanly}
  specify("examples.txt[4264] - ViewAction-125 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-125-jsonld.html").to lint_cleanly}
  specify("examples.txt[4288] - WatchAction-126 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-126-microdata.html").to lint_cleanly}
  specify("examples.txt[4292] - WatchAction-126 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-126-rdfa.html").to lint_cleanly}
  specify("examples.txt[4296] - WatchAction-126 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-126-jsonld.html").to lint_cleanly}
  specify("examples.txt[4320] - WatchAction-127 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-127-microdata.html").to lint_cleanly}
  specify("examples.txt[4324] - WatchAction-127 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-127-rdfa.html").to lint_cleanly}
  specify("examples.txt[4328] - WatchAction-127 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-127-jsonld.html").to lint_cleanly}
  specify("examples.txt[4352] - WatchAction-128 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-128-microdata.html").to lint_cleanly}
  specify("examples.txt[4356] - WatchAction-128 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-128-rdfa.html").to lint_cleanly}
  specify("examples.txt[4360] - WatchAction-128 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-128-jsonld.html").to lint_cleanly}
  specify("examples.txt[4384] - WatchAction-129 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-129-microdata.html").to lint_cleanly}
  specify("examples.txt[4388] - WatchAction-129 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-129-rdfa.html").to lint_cleanly}
  specify("examples.txt[4392] - WatchAction-129 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-129-jsonld.html").to lint_cleanly}
  specify("examples.txt[4420] - CreateAction-130 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreateAction-130-microdata.html").to lint_cleanly}
  specify("examples.txt[4424] - CreateAction-130 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreateAction-130-rdfa.html").to lint_cleanly}
  specify("examples.txt[4428] - CreateAction-130 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreateAction-130-jsonld.html").to lint_cleanly}
  specify("examples.txt[4452] - CookAction-131 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CookAction-131-microdata.html").to lint_cleanly}
  specify("examples.txt[4456] - CookAction-131 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CookAction-131-rdfa.html").to lint_cleanly}
  specify("examples.txt[4460] - CookAction-131 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CookAction-131-jsonld.html").to lint_cleanly}
  specify("examples.txt[4484] - DrawAction-132 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrawAction-132-microdata.html").to lint_cleanly}
  specify("examples.txt[4488] - DrawAction-132 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrawAction-132-rdfa.html").to lint_cleanly}
  specify("examples.txt[4492] - DrawAction-132 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrawAction-132-jsonld.html").to lint_cleanly}
  specify("examples.txt[4516] - FilmAction-133 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FilmAction-133-microdata.html").to lint_cleanly}
  specify("examples.txt[4520] - FilmAction-133 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FilmAction-133-rdfa.html").to lint_cleanly}
  specify("examples.txt[4524] - FilmAction-133 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FilmAction-133-jsonld.html").to lint_cleanly}
  specify("examples.txt[4548] - PaintAction-134 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaintAction-134-microdata.html").to lint_cleanly}
  specify("examples.txt[4552] - PaintAction-134 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaintAction-134-rdfa.html").to lint_cleanly}
  specify("examples.txt[4556] - PaintAction-134 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaintAction-134-jsonld.html").to lint_cleanly}
  specify("examples.txt[4580] - PhotographAction-135 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PhotographAction-135-microdata.html").to lint_cleanly}
  specify("examples.txt[4584] - PhotographAction-135 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PhotographAction-135-rdfa.html").to lint_cleanly}
  specify("examples.txt[4588] - PhotographAction-135 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PhotographAction-135-jsonld.html").to lint_cleanly}
  specify("examples.txt[4612] - WriteAction-136 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WriteAction-136-microdata.html").to lint_cleanly}
  specify("examples.txt[4616] - WriteAction-136 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WriteAction-136-rdfa.html").to lint_cleanly}
  specify("examples.txt[4620] - WriteAction-136 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WriteAction-136-jsonld.html").to lint_cleanly}
  specify("examples.txt[4644] - FindAction-137 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FindAction-137-microdata.html").to lint_cleanly}
  specify("examples.txt[4648] - FindAction-137 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FindAction-137-rdfa.html").to lint_cleanly}
  specify("examples.txt[4652] - FindAction-137 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FindAction-137-jsonld.html").to lint_cleanly}
  specify("examples.txt[4676] - CheckAction-138 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-138-microdata.html").to lint_cleanly}
  specify("examples.txt[4680] - CheckAction-138 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-138-rdfa.html").to lint_cleanly}
  specify("examples.txt[4684] - CheckAction-138 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-138-jsonld.html").to lint_cleanly}
  specify("examples.txt[4709] - CheckAction-139 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-139-microdata.html").to lint_cleanly}
  specify("examples.txt[4713] - CheckAction-139 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-139-rdfa.html").to lint_cleanly}
  specify("examples.txt[4717] - CheckAction-139 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-139-jsonld.html").to lint_cleanly}
  specify("examples.txt[4741] - DiscoverAction-140 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscoverAction-140-microdata.html").to lint_cleanly}
  specify("examples.txt[4745] - DiscoverAction-140 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscoverAction-140-rdfa.html").to lint_cleanly}
  specify("examples.txt[4749] - DiscoverAction-140 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscoverAction-140-jsonld.html").to lint_cleanly}
  specify("examples.txt[4773] - TrackAction-141 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrackAction-141-microdata.html").to lint_cleanly}
  specify("examples.txt[4777] - TrackAction-141 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrackAction-141-rdfa.html").to lint_cleanly}
  specify("examples.txt[4781] - TrackAction-141 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrackAction-141-jsonld.html").to lint_cleanly}
  specify("examples.txt[4809] - InteractAction-142 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-142-microdata.html").to lint_cleanly}
  specify("examples.txt[4813] - InteractAction-142 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-142-rdfa.html").to lint_cleanly}
  specify("examples.txt[4817] - InteractAction-142 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-142-jsonld.html").to lint_cleanly}
  specify("examples.txt[4841] - InteractAction-143 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-143-microdata.html").to lint_cleanly}
  specify("examples.txt[4845] - InteractAction-143 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-143-rdfa.html").to lint_cleanly}
  specify("examples.txt[4849] - InteractAction-143 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-143-jsonld.html").to lint_cleanly}
  specify("examples.txt[4873] - BefriendAction-144 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BefriendAction-144-microdata.html").to lint_cleanly}
  specify("examples.txt[4877] - BefriendAction-144 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BefriendAction-144-rdfa.html").to lint_cleanly}
  specify("examples.txt[4881] - BefriendAction-144 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BefriendAction-144-jsonld.html").to lint_cleanly}
  specify("examples.txt[4905] - CommunicateAction-145 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-145-microdata.html").to lint_cleanly}
  specify("examples.txt[4909] - CommunicateAction-145 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-145-rdfa.html").to lint_cleanly}
  specify("examples.txt[4913] - CommunicateAction-145 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-145-jsonld.html").to lint_cleanly}
  specify("examples.txt[4937] - CommunicateAction-146 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-146-microdata.html").to lint_cleanly}
  specify("examples.txt[4941] - CommunicateAction-146 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-146-rdfa.html").to lint_cleanly}
  specify("examples.txt[4945] - CommunicateAction-146 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-146-jsonld.html").to lint_cleanly}
  specify("examples.txt[4970] - AskAction-Question-147 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AskAction-Question-147-microdata.html").to lint_cleanly}
  specify("examples.txt[4974] - AskAction-Question-147 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AskAction-Question-147-rdfa.html").to lint_cleanly}
  specify("examples.txt[4978] - AskAction-Question-147 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AskAction-Question-147-jsonld.html").to lint_cleanly}
  specify("examples.txt[5006] - CheckInAction-148 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-148-microdata.html").to lint_cleanly}
  specify("examples.txt[5010] - CheckInAction-148 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-148-rdfa.html").to lint_cleanly}
  specify("examples.txt[5014] - CheckInAction-148 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-148-jsonld.html").to lint_cleanly}
  specify("examples.txt[5045] - CheckInAction-149 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-149-microdata.html").to lint_cleanly}
  specify("examples.txt[5049] - CheckInAction-149 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-149-rdfa.html").to lint_cleanly}
  specify("examples.txt[5053] - CheckInAction-149 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-149-jsonld.html").to lint_cleanly}
  specify("examples.txt[5093] - CheckInAction-150 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-150-microdata.html").to lint_cleanly}
  specify("examples.txt[5097] - CheckInAction-150 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-150-rdfa.html").to lint_cleanly}
  specify("examples.txt[5101] - CheckInAction-150 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-150-jsonld.html").to lint_cleanly}
  specify("examples.txt[5129] - CheckOutAction-151 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckOutAction-151-microdata.html").to lint_cleanly}
  specify("examples.txt[5133] - CheckOutAction-151 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckOutAction-151-rdfa.html").to lint_cleanly}
  specify("examples.txt[5137] - CheckOutAction-151 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckOutAction-151-jsonld.html").to lint_cleanly}
  specify("examples.txt[5165] - CommentAction-152 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommentAction-152-microdata.html").to lint_cleanly}
  specify("examples.txt[5169] - CommentAction-152 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommentAction-152-rdfa.html").to lint_cleanly}
  specify("examples.txt[5173] - CommentAction-152 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommentAction-152-jsonld.html").to lint_cleanly}
  specify("examples.txt[5201] - InformAction-153 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InformAction-153-microdata.html").to lint_cleanly}
  specify("examples.txt[5205] - InformAction-153 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InformAction-153-rdfa.html").to lint_cleanly}
  specify("examples.txt[5209] - InformAction-153 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InformAction-153-jsonld.html").to lint_cleanly}
  specify("examples.txt[5237] - ConfirmAction-154 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConfirmAction-154-microdata.html").to lint_cleanly}
  specify("examples.txt[5241] - ConfirmAction-154 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConfirmAction-154-rdfa.html").to lint_cleanly}
  specify("examples.txt[5245] - ConfirmAction-154 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConfirmAction-154-jsonld.html").to lint_cleanly}
  specify("examples.txt[5269] - RsvpAction-155 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RsvpAction-155-microdata.html").to lint_cleanly}
  specify("examples.txt[5273] - RsvpAction-155 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RsvpAction-155-rdfa.html").to lint_cleanly}
  specify("examples.txt[5277] - RsvpAction-155 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RsvpAction-155-jsonld.html").to lint_cleanly}
  specify("examples.txt[5301] - InviteAction-156 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InviteAction-156-microdata.html").to lint_cleanly}
  specify("examples.txt[5305] - InviteAction-156 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InviteAction-156-rdfa.html").to lint_cleanly}
  specify("examples.txt[5309] - InviteAction-156 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InviteAction-156-jsonld.html").to lint_cleanly}
  specify("examples.txt[5337] - ReplyAction-Question-Answer-157 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplyAction-Question-Answer-157-microdata.html").to lint_cleanly}
  specify("examples.txt[5341] - ReplyAction-Question-Answer-157 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplyAction-Question-Answer-157-rdfa.html").to lint_cleanly}
  specify("examples.txt[5345] - ReplyAction-Question-Answer-157 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplyAction-Question-Answer-157-jsonld.html").to lint_cleanly}
  specify("examples.txt[5377] - ShareAction-158 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-158-microdata.html").to lint_cleanly}
  specify("examples.txt[5381] - ShareAction-158 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-158-rdfa.html").to lint_cleanly}
  specify("examples.txt[5385] - ShareAction-158 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-158-jsonld.html").to lint_cleanly}
  specify("examples.txt[5413] - ShareAction-159 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-159-microdata.html").to lint_cleanly}
  specify("examples.txt[5417] - ShareAction-159 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-159-rdfa.html").to lint_cleanly}
  specify("examples.txt[5421] - ShareAction-159 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-159-jsonld.html").to lint_cleanly}
  specify("examples.txt[5450] - FollowAction-160 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FollowAction-160-microdata.html").to lint_cleanly}
  specify("examples.txt[5454] - FollowAction-160 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FollowAction-160-rdfa.html").to lint_cleanly}
  specify("examples.txt[5458] - FollowAction-160 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FollowAction-160-jsonld.html").to lint_cleanly}
  specify("examples.txt[5486] - JoinAction-161 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-161-microdata.html").to lint_cleanly}
  specify("examples.txt[5490] - JoinAction-161 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-161-rdfa.html").to lint_cleanly}
  specify("examples.txt[5494] - JoinAction-161 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-161-jsonld.html").to lint_cleanly}
  specify("examples.txt[5518] - JoinAction-162 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-162-microdata.html").to lint_cleanly}
  specify("examples.txt[5522] - JoinAction-162 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-162-rdfa.html").to lint_cleanly}
  specify("examples.txt[5526] - JoinAction-162 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-162-jsonld.html").to lint_cleanly}
  specify("examples.txt[5550] - JoinAction-163 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-163-microdata.html").to lint_cleanly}
  specify("examples.txt[5554] - JoinAction-163 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-163-rdfa.html").to lint_cleanly}
  specify("examples.txt[5558] - JoinAction-163 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-163-jsonld.html").to lint_cleanly}
  specify("examples.txt[5582] - JoinAction-164 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-164-microdata.html").to lint_cleanly}
  specify("examples.txt[5586] - JoinAction-164 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-164-rdfa.html").to lint_cleanly}
  specify("examples.txt[5590] - JoinAction-164 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-164-jsonld.html").to lint_cleanly}
  specify("examples.txt[5614] - LeaveAction-165 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LeaveAction-165-microdata.html").to lint_cleanly}
  specify("examples.txt[5618] - LeaveAction-165 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LeaveAction-165-rdfa.html").to lint_cleanly}
  specify("examples.txt[5622] - LeaveAction-165 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LeaveAction-165-jsonld.html").to lint_cleanly}
  specify("examples.txt[5646] - MarryAction-166 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MarryAction-166-microdata.html").to lint_cleanly}
  specify("examples.txt[5650] - MarryAction-166 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MarryAction-166-rdfa.html").to lint_cleanly}
  specify("examples.txt[5654] - MarryAction-166 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MarryAction-166-jsonld.html").to lint_cleanly}
  specify("examples.txt[5678] - RegisterAction-167 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-167-microdata.html").to lint_cleanly}
  specify("examples.txt[5682] - RegisterAction-167 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-167-rdfa.html").to lint_cleanly}
  specify("examples.txt[5686] - RegisterAction-167 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-167-jsonld.html").to lint_cleanly}
  specify("examples.txt[5710] - RegisterAction-168 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-168-microdata.html").to lint_cleanly}
  specify("examples.txt[5714] - RegisterAction-168 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-168-rdfa.html").to lint_cleanly}
  specify("examples.txt[5718] - RegisterAction-168 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-168-jsonld.html").to lint_cleanly}
  specify("examples.txt[5742] - RegisterAction-169 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-169-microdata.html").to lint_cleanly}
  specify("examples.txt[5746] - RegisterAction-169 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-169-rdfa.html").to lint_cleanly}
  specify("examples.txt[5750] - RegisterAction-169 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-169-jsonld.html").to lint_cleanly}
  specify("examples.txt[5774] - SubscribeAction-170 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SubscribeAction-170-microdata.html").to lint_cleanly}
  specify("examples.txt[5778] - SubscribeAction-170 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SubscribeAction-170-rdfa.html").to lint_cleanly}
  specify("examples.txt[5782] - SubscribeAction-170 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SubscribeAction-170-jsonld.html").to lint_cleanly}
  specify("examples.txt[5806] - UnRegisterAction-171 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UnRegisterAction-171-microdata.html").to lint_cleanly}
  specify("examples.txt[5810] - UnRegisterAction-171 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UnRegisterAction-171-rdfa.html").to lint_cleanly}
  specify("examples.txt[5814] - UnRegisterAction-171 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UnRegisterAction-171-jsonld.html").to lint_cleanly}
  specify("examples.txt[5838] - MoveAction-172 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MoveAction-172-microdata.html").to lint_cleanly}
  specify("examples.txt[5842] - MoveAction-172 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MoveAction-172-rdfa.html").to lint_cleanly}
  specify("examples.txt[5846] - MoveAction-172 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MoveAction-172-jsonld.html").to lint_cleanly}
  specify("examples.txt[5878] - ArriveAction-173 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArriveAction-173-microdata.html").to lint_cleanly}
  specify("examples.txt[5882] - ArriveAction-173 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArriveAction-173-rdfa.html").to lint_cleanly}
  specify("examples.txt[5886] - ArriveAction-173 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArriveAction-173-jsonld.html").to lint_cleanly}
  specify("examples.txt[5910] - DepartAction-174 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepartAction-174-microdata.html").to lint_cleanly}
  specify("examples.txt[5914] - DepartAction-174 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepartAction-174-rdfa.html").to lint_cleanly}
  specify("examples.txt[5918] - DepartAction-174 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepartAction-174-jsonld.html").to lint_cleanly}
  specify("examples.txt[5942] - TravelAction-175 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-175-microdata.html").to lint_cleanly}
  specify("examples.txt[5946] - TravelAction-175 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-175-rdfa.html").to lint_cleanly}
  specify("examples.txt[5950] - TravelAction-175 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-175-jsonld.html").to lint_cleanly}
  specify("examples.txt[5974] - TravelAction-176 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-176-microdata.html").to lint_cleanly}
  specify("examples.txt[5978] - TravelAction-176 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-176-rdfa.html").to lint_cleanly}
  specify("examples.txt[5982] - TravelAction-176 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-176-jsonld.html").to lint_cleanly}
  specify("examples.txt[6014] - OrganizeAction-177 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-177-microdata.html").to lint_cleanly}
  specify("examples.txt[6018] - OrganizeAction-177 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-177-rdfa.html").to lint_cleanly}
  specify("examples.txt[6022] - OrganizeAction-177 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-177-jsonld.html").to lint_cleanly}
  specify("examples.txt[6046] - OrganizeAction-178 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-178-microdata.html").to lint_cleanly}
  specify("examples.txt[6050] - OrganizeAction-178 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-178-rdfa.html").to lint_cleanly}
  specify("examples.txt[6054] - OrganizeAction-178 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-178-jsonld.html").to lint_cleanly}
  specify("examples.txt[6078] - AllocateAction-179 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AllocateAction-179-microdata.html").to lint_cleanly}
  specify("examples.txt[6082] - AllocateAction-179 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AllocateAction-179-rdfa.html").to lint_cleanly}
  specify("examples.txt[6086] - AllocateAction-179 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AllocateAction-179-jsonld.html").to lint_cleanly}
  specify("examples.txt[6114] - AcceptAction-180 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AcceptAction-180-microdata.html").to lint_cleanly}
  specify("examples.txt[6118] - AcceptAction-180 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AcceptAction-180-rdfa.html").to lint_cleanly}
  specify("examples.txt[6122] - AcceptAction-180 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AcceptAction-180-jsonld.html").to lint_cleanly}
  specify("examples.txt[6150] - AssignAction-181 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssignAction-181-microdata.html").to lint_cleanly}
  specify("examples.txt[6154] - AssignAction-181 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssignAction-181-rdfa.html").to lint_cleanly}
  specify("examples.txt[6158] - AssignAction-181 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssignAction-181-jsonld.html").to lint_cleanly}
  specify("examples.txt[6190] - AuthorizeAction-182 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AuthorizeAction-182-microdata.html").to lint_cleanly}
  specify("examples.txt[6194] - AuthorizeAction-182 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AuthorizeAction-182-rdfa.html").to lint_cleanly}
  specify("examples.txt[6198] - AuthorizeAction-182 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AuthorizeAction-182-jsonld.html").to lint_cleanly}
  specify("examples.txt[6230] - RejectAction-183 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RejectAction-183-microdata.html").to lint_cleanly}
  specify("examples.txt[6234] - RejectAction-183 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RejectAction-183-rdfa.html").to lint_cleanly}
  specify("examples.txt[6238] - RejectAction-183 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RejectAction-183-jsonld.html").to lint_cleanly}
  specify("examples.txt[6266] - ApplyAction-184 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ApplyAction-184-microdata.html").to lint_cleanly}
  specify("examples.txt[6270] - ApplyAction-184 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ApplyAction-184-rdfa.html").to lint_cleanly}
  specify("examples.txt[6274] - ApplyAction-184 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ApplyAction-184-jsonld.html").to lint_cleanly}
  specify("examples.txt[6298] - BookmarkAction-185 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookmarkAction-185-microdata.html").to lint_cleanly}
  specify("examples.txt[6302] - BookmarkAction-185 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookmarkAction-185-rdfa.html").to lint_cleanly}
  specify("examples.txt[6306] - BookmarkAction-185 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookmarkAction-185-jsonld.html").to lint_cleanly}
  specify("examples.txt[6335] - PlanAction-186 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-186-microdata.html").to lint_cleanly}
  specify("examples.txt[6339] - PlanAction-186 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-186-rdfa.html").to lint_cleanly}
  specify("examples.txt[6343] - PlanAction-186 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-186-jsonld.html").to lint_cleanly}
  specify("examples.txt[6371] - PlanAction-187 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-187-microdata.html").to lint_cleanly}
  specify("examples.txt[6375] - PlanAction-187 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-187-rdfa.html").to lint_cleanly}
  specify("examples.txt[6379] - PlanAction-187 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-187-jsonld.html").to lint_cleanly}
  specify("examples.txt[6407] - CancelAction-188 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CancelAction-188-microdata.html").to lint_cleanly}
  specify("examples.txt[6411] - CancelAction-188 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CancelAction-188-rdfa.html").to lint_cleanly}
  specify("examples.txt[6415] - CancelAction-188 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CancelAction-188-jsonld.html").to lint_cleanly}
  specify("examples.txt[6443] - ReserveAction-189 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-189-microdata.html").to lint_cleanly}
  specify("examples.txt[6447] - ReserveAction-189 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-189-rdfa.html").to lint_cleanly}
  specify("examples.txt[6451] - ReserveAction-189 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-189-jsonld.html").to lint_cleanly}
  specify("examples.txt[6476] - ScheduleAction-190 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScheduleAction-190-microdata.html").to lint_cleanly}
  specify("examples.txt[6480] - ScheduleAction-190 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScheduleAction-190-rdfa.html").to lint_cleanly}
  specify("examples.txt[6484] - ScheduleAction-190 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScheduleAction-190-jsonld.html").to lint_cleanly}
  specify("examples.txt[6511] - PlayAction-191 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlayAction-191-microdata.html").to lint_cleanly}
  specify("examples.txt[6515] - PlayAction-191 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlayAction-191-rdfa.html").to lint_cleanly}
  specify("examples.txt[6519] - PlayAction-191 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlayAction-191-jsonld.html").to lint_cleanly}
  specify("examples.txt[6547] - ExerciseAction-192 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-192-microdata.html").to lint_cleanly}
  specify("examples.txt[6551] - ExerciseAction-192 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-192-rdfa.html").to lint_cleanly}
  specify("examples.txt[6555] - ExerciseAction-192 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-192-jsonld.html").to lint_cleanly}
  specify("examples.txt[6581] - ExerciseAction-193 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-193-microdata.html").to lint_cleanly}
  specify("examples.txt[6585] - ExerciseAction-193 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-193-rdfa.html").to lint_cleanly}
  specify("examples.txt[6589] - ExerciseAction-193 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-193-jsonld.html").to lint_cleanly}
  specify("examples.txt[6614] - PerformAction-194 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PerformAction-194-microdata.html").to lint_cleanly}
  specify("examples.txt[6618] - PerformAction-194 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PerformAction-194-rdfa.html").to lint_cleanly}
  specify("examples.txt[6622] - PerformAction-194 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PerformAction-194-jsonld.html").to lint_cleanly}
  specify("examples.txt[6654] - SearchAction-195 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-195-microdata.html").to lint_cleanly}
  specify("examples.txt[6658] - SearchAction-195 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-195-rdfa.html").to lint_cleanly}
  specify("examples.txt[6662] - SearchAction-195 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-195-jsonld.html").to lint_cleanly}
  specify("examples.txt[6683] - SearchAction-196 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-196-microdata.html").to lint_cleanly}
  specify("examples.txt[6687] - SearchAction-196 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-196-rdfa.html").to lint_cleanly}
  specify("examples.txt[6691] - SearchAction-196 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-196-jsonld.html").to lint_cleanly}
  specify("examples.txt[6712] - TradeAction-197 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TradeAction-197-microdata.html").to lint_cleanly}
  specify("examples.txt[6716] - TradeAction-197 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TradeAction-197-rdfa.html").to lint_cleanly}
  specify("examples.txt[6720] - TradeAction-197 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TradeAction-197-jsonld.html").to lint_cleanly}
  specify("examples.txt[6746] - BuyAction-198 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BuyAction-198-microdata.html").to lint_cleanly}
  specify("examples.txt[6750] - BuyAction-198 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BuyAction-198-rdfa.html").to lint_cleanly}
  specify("examples.txt[6754] - BuyAction-198 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BuyAction-198-jsonld.html").to lint_cleanly}
  specify("examples.txt[6782] - DonateAction-199 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DonateAction-199-microdata.html").to lint_cleanly}
  specify("examples.txt[6786] - DonateAction-199 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DonateAction-199-rdfa.html").to lint_cleanly}
  specify("examples.txt[6790] - DonateAction-199 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DonateAction-199-jsonld.html").to lint_cleanly}
  specify("examples.txt[6816] - OrderAction-200 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrderAction-200-microdata.html").to lint_cleanly}
  specify("examples.txt[6820] - OrderAction-200 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrderAction-200-rdfa.html").to lint_cleanly}
  specify("examples.txt[6824] - OrderAction-200 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrderAction-200-jsonld.html").to lint_cleanly}
  specify("examples.txt[6852] - PayAction-201 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PayAction-201-microdata.html").to lint_cleanly}
  specify("examples.txt[6856] - PayAction-201 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PayAction-201-rdfa.html").to lint_cleanly}
  specify("examples.txt[6860] - PayAction-201 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PayAction-201-jsonld.html").to lint_cleanly}
  specify("examples.txt[6886] - QuoteAction-202 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/QuoteAction-202-microdata.html").to lint_cleanly}
  specify("examples.txt[6890] - QuoteAction-202 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/QuoteAction-202-rdfa.html").to lint_cleanly}
  specify("examples.txt[6894] - QuoteAction-202 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/QuoteAction-202-jsonld.html").to lint_cleanly}
  specify("examples.txt[6920] - RentAction-203 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentAction-203-microdata.html").to lint_cleanly}
  specify("examples.txt[6924] - RentAction-203 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentAction-203-rdfa.html").to lint_cleanly}
  specify("examples.txt[6928] - RentAction-203 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentAction-203-jsonld.html").to lint_cleanly}
  specify("examples.txt[6956] - SellAction-204 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SellAction-204-microdata.html").to lint_cleanly}
  specify("examples.txt[6960] - SellAction-204 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SellAction-204-rdfa.html").to lint_cleanly}
  specify("examples.txt[6964] - SellAction-204 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SellAction-204-jsonld.html").to lint_cleanly}
  specify("examples.txt[6993] - TipAction-205 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TipAction-205-microdata.html").to lint_cleanly}
  specify("examples.txt[6997] - TipAction-205 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TipAction-205-rdfa.html").to lint_cleanly}
  specify("examples.txt[7001] - TipAction-205 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TipAction-205-jsonld.html").to lint_cleanly}
  specify("examples.txt[7030] - TransferAction-206 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TransferAction-206-microdata.html").to lint_cleanly}
  specify("examples.txt[7034] - TransferAction-206 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TransferAction-206-rdfa.html").to lint_cleanly}
  specify("examples.txt[7038] - TransferAction-206 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TransferAction-206-jsonld.html").to lint_cleanly}
  specify("examples.txt[7070] - BorrowAction-207 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BorrowAction-207-microdata.html").to lint_cleanly}
  specify("examples.txt[7074] - BorrowAction-207 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BorrowAction-207-rdfa.html").to lint_cleanly}
  specify("examples.txt[7078] - BorrowAction-207 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BorrowAction-207-jsonld.html").to lint_cleanly}
  specify("examples.txt[7106] - DownloadAction-208 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DownloadAction-208-microdata.html").to lint_cleanly}
  specify("examples.txt[7110] - DownloadAction-208 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DownloadAction-208-rdfa.html").to lint_cleanly}
  specify("examples.txt[7114] - DownloadAction-208 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DownloadAction-208-jsonld.html").to lint_cleanly}
  specify("examples.txt[7138] - GiveAction-209 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-209-microdata.html").to lint_cleanly}
  specify("examples.txt[7142] - GiveAction-209 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-209-rdfa.html").to lint_cleanly}
  specify("examples.txt[7146] - GiveAction-209 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-209-jsonld.html").to lint_cleanly}
  specify("examples.txt[7174] - LendAction-210 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LendAction-210-microdata.html").to lint_cleanly}
  specify("examples.txt[7178] - LendAction-210 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LendAction-210-rdfa.html").to lint_cleanly}
  specify("examples.txt[7182] - LendAction-210 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LendAction-210-jsonld.html").to lint_cleanly}
  specify("examples.txt[7211] - ReceiveAction-211 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReceiveAction-211-microdata.html").to lint_cleanly}
  specify("examples.txt[7215] - ReceiveAction-211 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReceiveAction-211-rdfa.html").to lint_cleanly}
  specify("examples.txt[7219] - ReceiveAction-211 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReceiveAction-211-jsonld.html").to lint_cleanly}
  specify("examples.txt[7259] - ReturnAction-212 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReturnAction-212-microdata.html").to lint_cleanly}
  specify("examples.txt[7263] - ReturnAction-212 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReturnAction-212-rdfa.html").to lint_cleanly}
  specify("examples.txt[7267] - ReturnAction-212 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReturnAction-212-jsonld.html").to lint_cleanly}
  specify("examples.txt[7295] - SendAction-213 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SendAction-213-microdata.html").to lint_cleanly}
  specify("examples.txt[7299] - SendAction-213 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SendAction-213-rdfa.html").to lint_cleanly}
  specify("examples.txt[7303] - SendAction-213 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SendAction-213-jsonld.html").to lint_cleanly}
  specify("examples.txt[7343] - GiveAction-214 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-214-microdata.html").to lint_cleanly}
  specify("examples.txt[7347] - GiveAction-214 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-214-rdfa.html").to lint_cleanly}
  specify("examples.txt[7351] - GiveAction-214 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-214-jsonld.html").to lint_cleanly}
  specify("examples.txt[7379] - UpdateAction-215 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UpdateAction-215-microdata.html").to lint_cleanly}
  specify("examples.txt[7383] - UpdateAction-215 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UpdateAction-215-rdfa.html").to lint_cleanly}
  specify("examples.txt[7387] - UpdateAction-215 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UpdateAction-215-jsonld.html").to lint_cleanly}
  specify("examples.txt[7412] - AddAction-216 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-216-microdata.html").to lint_cleanly}
  specify("examples.txt[7416] - AddAction-216 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-216-rdfa.html").to lint_cleanly}
  specify("examples.txt[7420] - AddAction-216 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-216-jsonld.html").to lint_cleanly}
  specify("examples.txt[7449] - AddAction-217 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-217-microdata.html").to lint_cleanly}
  specify("examples.txt[7453] - AddAction-217 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-217-rdfa.html").to lint_cleanly}
  specify("examples.txt[7457] - AddAction-217 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-217-jsonld.html").to lint_cleanly}
  specify("examples.txt[7486] - InsertAction-218 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InsertAction-218-microdata.html").to lint_cleanly}
  specify("examples.txt[7490] - InsertAction-218 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InsertAction-218-rdfa.html").to lint_cleanly}
  specify("examples.txt[7494] - InsertAction-218 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InsertAction-218-jsonld.html").to lint_cleanly}
  specify("examples.txt[7523] - AppendAction-219 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AppendAction-219-microdata.html").to lint_cleanly}
  specify("examples.txt[7527] - AppendAction-219 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AppendAction-219-rdfa.html").to lint_cleanly}
  specify("examples.txt[7531] - AppendAction-219 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AppendAction-219-jsonld.html").to lint_cleanly}
  specify("examples.txt[7560] - PrependAction-220 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PrependAction-220-microdata.html").to lint_cleanly}
  specify("examples.txt[7564] - PrependAction-220 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PrependAction-220-rdfa.html").to lint_cleanly}
  specify("examples.txt[7568] - PrependAction-220 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PrependAction-220-jsonld.html").to lint_cleanly}
  specify("examples.txt[7597] - DeleteAction-221 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DeleteAction-221-microdata.html").to lint_cleanly}
  specify("examples.txt[7601] - DeleteAction-221 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DeleteAction-221-rdfa.html").to lint_cleanly}
  specify("examples.txt[7605] - DeleteAction-221 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DeleteAction-221-jsonld.html").to lint_cleanly}
  specify("examples.txt[7634] - ReplaceAction-222 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplaceAction-222-microdata.html").to lint_cleanly}
  specify("examples.txt[7638] - ReplaceAction-222 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplaceAction-222-rdfa.html").to lint_cleanly}
  specify("examples.txt[7642] - ReplaceAction-222 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplaceAction-222-jsonld.html").to lint_cleanly}
  specify("examples.txt[7682] - TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223-microdata.html").to lint_cleanly}
  specify("examples.txt[7714] - TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223-rdfa.html").to lint_cleanly}
  specify("examples.txt[7746] - TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223-jsonld.html").to lint_cleanly}
  specify("examples.txt[7794] - RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224-microdata.html").to lint_cleanly}
  specify("examples.txt[7818] - RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224-rdfa.html").to lint_cleanly}
  specify("examples.txt[7842] - RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224-jsonld.html").to lint_cleanly}
  specify("examples.txt[7880] - GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225-microdata.html").to lint_cleanly}
  specify("examples.txt[7896] - GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225-rdfa.html").to lint_cleanly}
  specify("examples.txt[7912] - GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225-jsonld.html").to lint_cleanly}
  specify("examples.txt[7944] - GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226-microdata.html").to lint_cleanly}
  specify("examples.txt[7948] - GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226-rdfa.html").to lint_cleanly}
  specify("examples.txt[7952] - GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226-jsonld.html").to lint_cleanly}
  specify("examples.txt[8019] - Event-Place-PostalAddress-Offer-227 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-227-microdata.html").to lint_cleanly}
  specify("examples.txt[8042] - Event-Place-PostalAddress-Offer-227 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-227-rdfa.html").to lint_cleanly}
  specify("examples.txt[8070] - Event-Place-PostalAddress-Offer-227 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-227-jsonld.html").to lint_cleanly}
  specify("examples.txt[8123] - Event-Place-PostalAddress-Offer-EventCancelled-228 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-EventCancelled-228-microdata.html").to lint_cleanly}
  specify("examples.txt[8148] - Event-Place-PostalAddress-Offer-EventCancelled-228 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-EventCancelled-228-rdfa.html").to lint_cleanly}
  specify("examples.txt[8172] - Event-Place-PostalAddress-Offer-EventCancelled-228 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-EventCancelled-228-jsonld.html").to lint_cleanly}
  specify("examples.txt[8223] - Event-Place-PostalAddress-Offer-229 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-229-microdata.html").to lint_cleanly}
  specify("examples.txt[8249] - Event-Place-PostalAddress-Offer-229 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-229-rdfa.html").to lint_cleanly}
  specify("examples.txt[8276] - Event-Place-PostalAddress-Offer-229 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-229-jsonld.html").to lint_cleanly}
  specify("examples.txt[8324] - Event-Place-PostalAddress-Offer-SoldOut-230 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-SoldOut-230-microdata.html").to lint_cleanly}
  specify("examples.txt[8348] - Event-Place-PostalAddress-Offer-SoldOut-230 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-SoldOut-230-rdfa.html").to lint_cleanly}
  specify("examples.txt[8377] - Event-Place-PostalAddress-Offer-SoldOut-230 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-SoldOut-230-jsonld.html").to lint_cleanly}
  specify("examples.txt[8412] - Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231-microdata.html").to lint_cleanly}
  specify("examples.txt[8416] - Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231-rdfa.html").to lint_cleanly}
  specify("examples.txt[8420] - Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231-jsonld.html").to lint_cleanly}
  specify("examples.txt[8508] - Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232-microdata.html").to lint_cleanly}
  specify("examples.txt[8582] - Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232-rdfa.html").to lint_cleanly}
  specify("examples.txt[8656] - Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232-jsonld.html").to lint_cleanly}
  specify("examples.txt[8710] - accessibilityFeature-accessibilityHazard-encodingFormat-233 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessibilityFeature-accessibilityHazard-encodingFormat-233-microdata.html").to lint_cleanly}
  specify("examples.txt[8721] - accessibilityFeature-accessibilityHazard-encodingFormat-233 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessibilityFeature-accessibilityHazard-encodingFormat-233-rdfa.html").to lint_cleanly}
  specify("examples.txt[8732] - accessibilityFeature-accessibilityHazard-encodingFormat-233 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessibilityFeature-accessibilityHazard-encodingFormat-233-jsonld.html").to lint_cleanly}
  specify("examples.txt[8741] - encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234-microdata.html").to lint_cleanly}
  specify("examples.txt[8762] - encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234-rdfa.html").to lint_cleanly}
  specify("examples.txt[8783] - encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234-jsonld.html").to lint_cleanly}
  specify("examples.txt[8823] - TrainReservation-TrainTrip-235 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainReservation-TrainTrip-235-microdata.html").to lint_cleanly}
  specify("examples.txt[8827] - TrainReservation-TrainTrip-235 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainReservation-TrainTrip-235-rdfa.html").to lint_cleanly}
  specify("examples.txt[8831] - TrainReservation-TrainTrip-235 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainReservation-TrainTrip-235-jsonld.html").to lint_cleanly}
  specify("examples.txt[8878] - BusReservation-BusTrip-236 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusReservation-BusTrip-236-microdata.html").to lint_cleanly}
  specify("examples.txt[8882] - BusReservation-BusTrip-236 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusReservation-BusTrip-236-rdfa.html").to lint_cleanly}
  specify("examples.txt[8886] - BusReservation-BusTrip-236 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusReservation-BusTrip-236-jsonld.html").to lint_cleanly}
  specify("examples.txt[8937] - EventReservation-Ticket-Seat-237 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventReservation-Ticket-Seat-237-microdata.html").to lint_cleanly}
  specify("examples.txt[8941] - EventReservation-Ticket-Seat-237 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventReservation-Ticket-Seat-237-rdfa.html").to lint_cleanly}
  specify("examples.txt[8945] - EventReservation-Ticket-Seat-237 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventReservation-Ticket-Seat-237-jsonld.html").to lint_cleanly}
  specify("examples.txt[9003] - Flight-FlightReservation-238 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Flight-FlightReservation-238-microdata.html").to lint_cleanly}
  specify("examples.txt[9007] - Flight-FlightReservation-238 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Flight-FlightReservation-238-rdfa.html").to lint_cleanly}
  specify("examples.txt[9011] - Flight-FlightReservation-238 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Flight-FlightReservation-238-jsonld.html").to lint_cleanly}
  specify("examples.txt[9071] - FoodEstablishmentReservation-239 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FoodEstablishmentReservation-239-microdata.html").to lint_cleanly}
  specify("examples.txt[9075] - FoodEstablishmentReservation-239 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FoodEstablishmentReservation-239-rdfa.html").to lint_cleanly}
  specify("examples.txt[9079] - FoodEstablishmentReservation-239 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FoodEstablishmentReservation-239-jsonld.html").to lint_cleanly}
  specify("examples.txt[9123] - LodgingReservation-240 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LodgingReservation-240-microdata.html").to lint_cleanly}
  specify("examples.txt[9127] - LodgingReservation-240 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LodgingReservation-240-rdfa.html").to lint_cleanly}
  specify("examples.txt[9131] - LodgingReservation-240 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LodgingReservation-240-jsonld.html").to lint_cleanly}
  specify("examples.txt[9181] - RentalCarReservation-241 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentalCarReservation-241-microdata.html").to lint_cleanly}
  specify("examples.txt[9185] - RentalCarReservation-241 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentalCarReservation-241-rdfa.html").to lint_cleanly}
  specify("examples.txt[9189] - RentalCarReservation-241 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentalCarReservation-241-jsonld.html").to lint_cleanly}
  specify("examples.txt[9255] - TaxiReservation-242 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TaxiReservation-242-microdata.html").to lint_cleanly}
  specify("examples.txt[9259] - TaxiReservation-242 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TaxiReservation-242-rdfa.html").to lint_cleanly}
  specify("examples.txt[9263] - TaxiReservation-242 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TaxiReservation-242-jsonld.html").to lint_cleanly}
  specify("examples.txt[9330] - Question-Answer-243 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Question-Answer-243-microdata.html").to lint_cleanly}
  specify("examples.txt[9357] - Question-Answer-243 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Question-Answer-243-rdfa.html").to lint_cleanly}
  specify("examples.txt[9384] - Question-Answer-243 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Question-Answer-243-jsonld.html").to lint_cleanly}
  specify("examples.txt[9433] - WatchAction-Movie-244 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-Movie-244-microdata.html").to lint_cleanly}
  specify("examples.txt[9442] - WatchAction-Movie-244 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-Movie-244-rdfa.html").to lint_cleanly}
  specify("examples.txt[9451] - WatchAction-Movie-244 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-Movie-244-jsonld.html").to lint_cleanly}
  specify("examples.txt[9475] - Restaurant-ViewAction-EntryPoint-SoftwareApplication-245 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-ViewAction-EntryPoint-SoftwareApplication-245-microdata.html").to lint_cleanly}
  specify("examples.txt[9479] - Restaurant-ViewAction-EntryPoint-SoftwareApplication-245 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-ViewAction-EntryPoint-SoftwareApplication-245-rdfa.html").to lint_cleanly}
  specify("examples.txt[9483] - Restaurant-ViewAction-EntryPoint-SoftwareApplication-245 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-ViewAction-EntryPoint-SoftwareApplication-245-jsonld.html").to lint_cleanly}
  specify("examples.txt[9581] - MusicEvent-Event-CreativeWork-MusicGroup-Person-246 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Event-CreativeWork-MusicGroup-Person-246-microdata.html").to lint_cleanly}
  specify("examples.txt[9649] - MusicEvent-Event-CreativeWork-MusicGroup-Person-246 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Event-CreativeWork-MusicGroup-Person-246-rdfa.html").to lint_cleanly}
  specify("examples.txt[9711] - MusicEvent-Event-CreativeWork-MusicGroup-Person-246 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Event-CreativeWork-MusicGroup-Person-246-jsonld.html").to lint_cleanly}
  specify("examples.txt[9771] - Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247-microdata.html").to lint_cleanly}
  specify("examples.txt[9794] - Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247-rdfa.html").to lint_cleanly}
  specify("examples.txt[9817] - Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247-jsonld.html").to lint_cleanly}
  specify("examples.txt[9856] - SportsEvent-248 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsEvent-248-microdata.html").to lint_cleanly}
  specify("examples.txt[9860] - SportsEvent-248 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsEvent-248-rdfa.html").to lint_cleanly}
  specify("examples.txt[9864] - SportsEvent-248 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsEvent-248-jsonld.html").to lint_cleanly}
  specify("examples.txt[9892] - Restaurant-249 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-249-microdata.html").to lint_cleanly}
  specify("examples.txt[9902] - Restaurant-249 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-249-rdfa.html").to lint_cleanly}
  specify("examples.txt[9912] - Restaurant-249 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-249-jsonld.html").to lint_cleanly}
  specify("examples.txt[9947] - Store-OpeningHoursSpecification-250 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-OpeningHoursSpecification-250-microdata.html").to lint_cleanly}
  specify("examples.txt[9967] - Store-OpeningHoursSpecification-250 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-OpeningHoursSpecification-250-rdfa.html").to lint_cleanly}
  specify("examples.txt[9987] - Store-OpeningHoursSpecification-250 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-OpeningHoursSpecification-250-jsonld.html").to lint_cleanly}
  specify("examples.txt[10027] - Pharmacy-openingHours-telephone-251 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Pharmacy-openingHours-telephone-251-microdata.html").to lint_cleanly}
  specify("examples.txt[10037] - Pharmacy-openingHours-telephone-251 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Pharmacy-openingHours-telephone-251-rdfa.html").to lint_cleanly}
  specify("examples.txt[10047] - Pharmacy-openingHours-telephone-251 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Pharmacy-openingHours-telephone-251-jsonld.html").to lint_cleanly}
  specify("examples.txt[10084] - Store-Pharmacy-252 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-Pharmacy-252-microdata.html").to lint_cleanly}
  specify("examples.txt[10104] - Store-Pharmacy-252 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-Pharmacy-252-rdfa.html").to lint_cleanly}
  specify("examples.txt[10124] - Store-Pharmacy-252 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-Pharmacy-252-jsonld.html").to lint_cleanly}
  specify("examples.txt[10179] - Store-DryCleaningOrLaundry-Corporation-Pharmacy-253 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-DryCleaningOrLaundry-Corporation-Pharmacy-253-microdata.html").to lint_cleanly}
  specify("examples.txt[10209] - Store-DryCleaningOrLaundry-Corporation-Pharmacy-253 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-DryCleaningOrLaundry-Corporation-Pharmacy-253-rdfa.html").to lint_cleanly}
  specify("examples.txt[10238] - Store-DryCleaningOrLaundry-Corporation-Pharmacy-253 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-DryCleaningOrLaundry-Corporation-Pharmacy-253-jsonld.html").to lint_cleanly}
  specify("examples.txt[10302] - Store-PostalAddress-Pharmacy-254 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-PostalAddress-Pharmacy-254-microdata.html").to lint_cleanly}
  specify("examples.txt[10327] - Store-PostalAddress-Pharmacy-254 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-PostalAddress-Pharmacy-254-rdfa.html").to lint_cleanly}
  specify("examples.txt[10352] - Store-PostalAddress-Pharmacy-254 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-PostalAddress-Pharmacy-254-jsonld.html").to lint_cleanly}
  specify("examples.txt[10414] - PostalAddress-Pharmacy-Store-255 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-Pharmacy-Store-255-microdata.html").to lint_cleanly}
  specify("examples.txt[10444] - PostalAddress-Pharmacy-Store-255 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-Pharmacy-Store-255-rdfa.html").to lint_cleanly}
  specify("examples.txt[10474] - PostalAddress-Pharmacy-Store-255 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-Pharmacy-Store-255-jsonld.html").to lint_cleanly}
  specify("examples.txt[10517] - Organization-ContactPoint-256 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-ContactPoint-256-microdata.html").to lint_cleanly}
  specify("examples.txt[10521] - Organization-ContactPoint-256 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-ContactPoint-256-rdfa.html").to lint_cleanly}
  specify("examples.txt[10525] - Organization-ContactPoint-256 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-ContactPoint-256-jsonld.html").to lint_cleanly}
  specify("examples.txt[10545] - HearingImpairedSupported-TollFree-ContactPoint-Organization-257 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HearingImpairedSupported-TollFree-ContactPoint-Organization-257-microdata.html").to lint_cleanly}
  specify("examples.txt[10549] - HearingImpairedSupported-TollFree-ContactPoint-Organization-257 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HearingImpairedSupported-TollFree-ContactPoint-Organization-257-rdfa.html").to lint_cleanly}
  specify("examples.txt[10553] - HearingImpairedSupported-TollFree-ContactPoint-Organization-257 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HearingImpairedSupported-TollFree-ContactPoint-Organization-257-jsonld.html").to lint_cleanly}
  specify("examples.txt[10597] - MusicEvent-Place-Offer-258 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-Offer-258-microdata.html").to lint_cleanly}
  specify("examples.txt[10601] - MusicEvent-Place-Offer-258 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-Offer-258-rdfa.html").to lint_cleanly}
  specify("examples.txt[10605] - MusicEvent-Place-Offer-258 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-Offer-258-jsonld.html").to lint_cleanly}
  specify("examples.txt[10647] - MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259-microdata.html").to lint_cleanly}
  specify("examples.txt[10651] - MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259-rdfa.html").to lint_cleanly}
  specify("examples.txt[10655] - MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259-jsonld.html").to lint_cleanly}
  specify("examples.txt[10717] - Role-OrganizationRole-260 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-260-microdata.html").to lint_cleanly}
  specify("examples.txt[10731] - Role-OrganizationRole-260 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-260-rdfa.html").to lint_cleanly}
  specify("examples.txt[10743] - Role-OrganizationRole-260 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-260-jsonld.html").to lint_cleanly}
  specify("examples.txt[10771] - Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261-microdata.html").to lint_cleanly}
  specify("examples.txt[10785] - Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261-rdfa.html").to lint_cleanly}
  specify("examples.txt[10799] - Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261-jsonld.html").to lint_cleanly}
  specify("examples.txt[10829] - Role-PerformanceRole-262 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-PerformanceRole-262-microdata.html").to lint_cleanly}
  specify("examples.txt[10844] - Role-PerformanceRole-262 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-PerformanceRole-262-rdfa.html").to lint_cleanly}
  specify("examples.txt[10857] - Role-PerformanceRole-262 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-PerformanceRole-262-jsonld.html").to lint_cleanly}
  specify("examples.txt[10884] - Role-OrganizationRole-Person-SportsTeam-Organization-263 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-Person-SportsTeam-Organization-263-microdata.html").to lint_cleanly}
  specify("examples.txt[10898] - Role-OrganizationRole-Person-SportsTeam-Organization-263 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-Person-SportsTeam-Organization-263-rdfa.html").to lint_cleanly}
  specify("examples.txt[10912] - Role-OrganizationRole-Person-SportsTeam-Organization-263 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-Person-SportsTeam-Organization-263-jsonld.html").to lint_cleanly}
  specify("examples.txt[10949] - WebPage-CollegeOrUniversity-264 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-CollegeOrUniversity-264-microdata.html").to lint_cleanly}
  specify("examples.txt[10964] - WebPage-CollegeOrUniversity-264 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-CollegeOrUniversity-264-rdfa.html").to lint_cleanly}
  specify("examples.txt[10978] - WebPage-CollegeOrUniversity-264 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-CollegeOrUniversity-264-jsonld.html").to lint_cleanly}
  specify("examples.txt[11015] - ItemList-Product-Offer-265 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-Product-Offer-265-microdata.html").to lint_cleanly}
  specify("examples.txt[11035] - ItemList-Product-Offer-265 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-Product-Offer-265-rdfa.html").to lint_cleanly}
  specify("examples.txt[11052] - ItemList-Product-Offer-265 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-Product-Offer-265-jsonld.html").to lint_cleanly}
  specify("examples.txt[11091] - ItemList-CreativeWork-266 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-CreativeWork-266-microdata.html").to lint_cleanly}
  specify("examples.txt[11155] - ItemList-CreativeWork-266 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-CreativeWork-266-rdfa.html").to lint_cleanly}
  specify("examples.txt[11222] - ItemList-CreativeWork-266 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-CreativeWork-266-jsonld.html").to lint_cleanly}
  specify("examples.txt[11321] - ItemList-267 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-267-microdata.html").to lint_cleanly}
  specify("examples.txt[11356] - ItemList-267 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-267-rdfa.html").to lint_cleanly}
  specify("examples.txt[11391] - ItemList-267 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-267-jsonld.html").to lint_cleanly}
  specify("examples.txt[11448] - ItemList-MusicAlbum-268 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-MusicAlbum-268-microdata.html").to lint_cleanly}
  specify("examples.txt[11475] - ItemList-MusicAlbum-268 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-MusicAlbum-268-rdfa.html").to lint_cleanly}
  specify("examples.txt[11504] - ItemList-MusicAlbum-268 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-MusicAlbum-268-jsonld.html").to lint_cleanly}
  specify("examples.txt[11555] - Person-disambiguatingDescription-269 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-disambiguatingDescription-269-microdata.html").to lint_cleanly}
  specify("examples.txt[11567] - Person-disambiguatingDescription-269 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-disambiguatingDescription-269-rdfa.html").to lint_cleanly}
  specify("examples.txt[11579] - Person-disambiguatingDescription-269 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-disambiguatingDescription-269-jsonld.html").to lint_cleanly}

  # Examples from sdo-sports-examples.txt
  specify("sdo-sports-examples.txt[10] - sports-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sports-1-microdata.html").to lint_cleanly}
  specify("sdo-sports-examples.txt[14] - SportsTeam-SportsOrganization-270 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsTeam-SportsOrganization-270-rdfa.html").to lint_cleanly}
  specify("sdo-sports-examples.txt[18] - SportsTeam-SportsOrganization-270 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsTeam-SportsOrganization-270-jsonld.html").to lint_cleanly}

  # Examples from sdo-howto-examples.txt
  specify("sdo-howto-examples.txt[91] - howto-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/howto-1-microdata.html").to lint_cleanly}
  specify("sdo-howto-examples.txt[222] - HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-271 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-271-rdfa.html").to lint_cleanly}
  specify("sdo-howto-examples.txt[354] - HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-271 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-271-jsonld.html").to lint_cleanly}

  # Examples from sdo-identifier-examples.txt
  specify("sdo-identifier-examples.txt[13] - identifier-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-1-microdata.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[25] - identifier-272 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-272-rdfa.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[39] - identifier-272 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-272-jsonld.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[66] - identifier-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-2-microdata.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[76] - identifier-273 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-273-rdfa.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[88] - identifier-273 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-273-jsonld.html").to lint_cleanly}

  # Examples from sdo-service-examples.txt
  specify("sdo-service-examples.txt[7] - service-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/service-1-microdata.html").to lint_cleanly}
  specify("sdo-service-examples.txt[25] - Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-274 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-274-rdfa.html").to lint_cleanly}
  specify("sdo-service-examples.txt[43] - Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-274 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-274-jsonld.html").to lint_cleanly}

  # Examples from sdo-automobile-examples.txt
  specify("sdo-automobile-examples.txt[22] - Car-275 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car-275-microdata.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[53] - Car-275 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car-275-rdfa.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[83] - Car-275 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car-275-jsonld.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[142] - Car makesOffer-276 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car makesOffer-276-microdata.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[173] - Car makesOffer-276 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car makesOffer-276-rdfa.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[203] - Car makesOffer-276 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car makesOffer-276-jsonld.html").to lint_cleanly}

  # Examples from issue-1004-examples.txt
  specify("issue-1004-examples.txt[7] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-277 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-277-microdata.html").to lint_cleanly}
  specify("issue-1004-examples.txt[18] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-277 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-277-rdfa.html").to lint_cleanly}
  specify("issue-1004-examples.txt[30] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-277 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-277-jsonld.html").to lint_cleanly}
  specify("issue-1004-examples.txt[52] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-278 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-278-microdata.html").to lint_cleanly}
  specify("issue-1004-examples.txt[62] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-278 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-278-rdfa.html").to lint_cleanly}
  specify("issue-1004-examples.txt[74] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-278 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-278-jsonld.html").to lint_cleanly}

  # Examples from sdo-userinteraction-examples.txt
  specify("sdo-userinteraction-examples.txt[11] - interaction-counter-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/interaction-counter-1-microdata.html").to lint_cleanly}
  specify("sdo-userinteraction-examples.txt[67] - InteractionCounter-VideoObject-279 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-VideoObject-279-rdfa.html").to lint_cleanly}
  specify("sdo-userinteraction-examples.txt[123] - InteractionCounter-VideoObject-279 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-VideoObject-279-jsonld.html").to lint_cleanly}

  # Examples from sdo-visualartwork-examples.txt
  specify("sdo-visualartwork-examples.txt[41] - VisualArtwork-Person-280 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-Person-280-microdata.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[90] - VisualArtwork-Person-280 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-Person-280-rdfa.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[139] - VisualArtwork-Person-280 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-Person-280-jsonld.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[210] - VisualArtwork-281 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-281-microdata.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[253] - VisualArtwork-281 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-281-rdfa.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[296] - VisualArtwork-281 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-281-jsonld.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[357] - VisualArtwork-282 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-282-microdata.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[399] - VisualArtwork-282 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-282-rdfa.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[441] - VisualArtwork-282 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-282-jsonld.html").to lint_cleanly}

  # Examples from sdo-screeningevent-examples.txt
  specify("sdo-screeningevent-examples.txt[21] - screening-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/screening-1-microdata.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[39] - ScreeningEvent-Movie-MovieTheater-283 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScreeningEvent-Movie-MovieTheater-283-rdfa.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[64] - ScreeningEvent-Movie-MovieTheater-283 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScreeningEvent-Movie-MovieTheater-283-jsonld.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[94] - screening-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/screening-2-microdata.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[106] - Movie-countryOfOrigin-284 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-countryOfOrigin-284-rdfa.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[118] - Movie-countryOfOrigin-284 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-countryOfOrigin-284-jsonld.html").to lint_cleanly}

  # Examples from sdo-website-examples.txt
  specify("sdo-website-examples.txt[7] - website-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/website-1-microdata.html").to lint_cleanly}
  specify("sdo-website-examples.txt[18] - SearchAction-WebSite-285 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-WebSite-285-rdfa.html").to lint_cleanly}
  specify("sdo-website-examples.txt[29] - SearchAction-WebSite-285 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-WebSite-285-jsonld.html").to lint_cleanly}

  # Examples from sdo-creativework-examples.txt
  specify("sdo-creativework-examples.txt[9] - creativework-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/creativework-1-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[26] - Painting-contentLocation-locationCreated-286 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-contentLocation-locationCreated-286-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[43] - Painting-contentLocation-locationCreated-286 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-contentLocation-locationCreated-286-jsonld.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[76] - creativework-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/creativework-2-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[107] - Conversation-Message-287 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Conversation-Message-287-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[138] - Conversation-Message-287 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Conversation-Message-287-jsonld.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[189] - creativework-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/creativework-3-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[208] - Message-288 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Message-288-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[227] - Message-288 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Message-288-jsonld.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[260] - creativework-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/creativework-4-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[288] - EmailMessage-toRecipient-bccRecipient-ccRecipient-289 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmailMessage-toRecipient-bccRecipient-ccRecipient-289-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[316] - EmailMessage-toRecipient-bccRecipient-ccRecipient-289 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmailMessage-toRecipient-bccRecipient-ccRecipient-289-jsonld.html").to lint_cleanly}

  # Examples from sdo-fibo-examples.txt
  specify("sdo-fibo-examples.txt[12] - fiboex-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-1-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[38] - CreditCard-MonetaryAmount-UnitPriceSpecification-290 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-MonetaryAmount-UnitPriceSpecification-290-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[65] - CreditCard-MonetaryAmount-UnitPriceSpecification-290 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-MonetaryAmount-UnitPriceSpecification-290-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[122] - fiboex-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-2-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[165] - LoanOrCredit-MonetaryAmount-291 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoanOrCredit-MonetaryAmount-291-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[210] - LoanOrCredit-MonetaryAmount-291 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoanOrCredit-MonetaryAmount-291-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[288] - fiboex-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-3-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[371] - BankAccount-292 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankAccount-292-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[454] - BankAccount-292 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankAccount-292-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[595] - fiboex-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-4-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[631] - DepositAccount-MonetaryAmount-293 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepositAccount-MonetaryAmount-293-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[667] - DepositAccount-MonetaryAmount-293 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepositAccount-MonetaryAmount-293-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[751] - fiboex-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-5-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[768] - PaymentCard-294 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentCard-294-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[785] - PaymentCard-294 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentCard-294-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[838] - fiboex-6 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-6-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[896] - PaymentService-295 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentService-295-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[951] - PaymentService-295 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentService-295-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1049] - fiboex-7 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-7-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1061] - FinancialProduct-296 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FinancialProduct-296-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1073] - FinancialProduct-296 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FinancialProduct-296-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1108] - fiboex-8 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/fiboex-8-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1119] - InvestmentOrDeposit-297 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentOrDeposit-297-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1130] - InvestmentOrDeposit-297 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentOrDeposit-297-jsonld.html").to lint_cleanly}

  # Examples from sdo-hotels-examples.txt
  specify("sdo-hotels-examples.txt[20] - Hotel-298 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-298-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[40] - Hotel-298 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-298-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[60] - Hotel-298 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-298-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[95] - starRating-299 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-299-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[106] - starRating-299 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-299-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[109] - starRating-299 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-299-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[123] - starRating-300 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-300-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[138] - starRating-300 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-300-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[141] - starRating-300 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-300-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[155] - Hotel-logo-image-301 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-logo-image-301-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[165] - Hotel-logo-image-301 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-logo-image-301-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[168] - Hotel-logo-image-301 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-logo-image-301-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[181] - hasMap-302 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/hasMap-302-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[190] - hasMap-302 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/hasMap-302-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[193] - hasMap-302 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/hasMap-302-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[201] - GeoCoordinates-geo-303 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GeoCoordinates-geo-303-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[220] - GeoCoordinates-geo-303 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GeoCoordinates-geo-303-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[223] - GeoCoordinates-geo-303 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GeoCoordinates-geo-303-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[231] - numberOfRooms-304 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-304-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[240] - numberOfRooms-304 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-304-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[243] - numberOfRooms-304 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-304-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[251] - numberOfRooms-305 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-305-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[267] - numberOfRooms-305 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-305-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[270] - numberOfRooms-305 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-305-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[278] - feature-LocationFeatureSpecification-306 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-306-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[297] - feature-LocationFeatureSpecification-306 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-306-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[300] - feature-LocationFeatureSpecification-306 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-306-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[308] - feature-LocationFeatureSpecification-hoursAvailable-307 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-hoursAvailable-307-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[328] - feature-LocationFeatureSpecification-hoursAvailable-307 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-hoursAvailable-307-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[331] - feature-LocationFeatureSpecification-hoursAvailable-307 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-hoursAvailable-307-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[339] - checkinTime-checkoutTime-308 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/checkinTime-checkoutTime-308-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[350] - checkinTime-checkoutTime-308 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/checkinTime-checkoutTime-308-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[353] - checkinTime-checkoutTime-308 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/checkinTime-checkoutTime-308-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[361] - availableLanguage-Language-309 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/availableLanguage-Language-309-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[378] - availableLanguage-Language-309 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/availableLanguage-Language-309-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[381] - availableLanguage-Language-309 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/availableLanguage-Language-309-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[389] - HotelRoom-Hotel-310 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HotelRoom-Hotel-310-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[409] - HotelRoom-Hotel-310 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HotelRoom-Hotel-310-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[412] - HotelRoom-Hotel-310 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HotelRoom-Hotel-310-jsonld.html").to lint_cleanly}

  # Examples from issue-1100-examples.txt
  specify("issue-1100-examples.txt[9] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-311 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-311-microdata.html").to lint_cleanly}
  specify("issue-1100-examples.txt[13] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-311 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-311-rdfa.html").to lint_cleanly}
  specify("issue-1100-examples.txt[17] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-311 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-311-jsonld.html").to lint_cleanly}
  specify("issue-1100-examples.txt[39] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-312 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-312-microdata.html").to lint_cleanly}
  specify("issue-1100-examples.txt[43] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-312 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-312-rdfa.html").to lint_cleanly}
  specify("issue-1100-examples.txt[47] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-312 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-312-jsonld.html").to lint_cleanly}
  specify("issue-1100-examples.txt[84] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-313 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-313-microdata.html").to lint_cleanly}
  specify("issue-1100-examples.txt[88] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-313 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-313-rdfa.html").to lint_cleanly}
  specify("issue-1100-examples.txt[92] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-313 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-313-jsonld.html").to lint_cleanly}

  # Examples from sdo-digital-document-examples.txt
  specify("sdo-digital-document-examples.txt[6] - digitaldocument-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/digitaldocument-1-microdata.html").to lint_cleanly}
  specify("sdo-digital-document-examples.txt[10] - DigitalDocument-ReadPermission-WritePermission-314 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DigitalDocument-ReadPermission-WritePermission-314-rdfa.html").to lint_cleanly}
  specify("sdo-digital-document-examples.txt[14] - DigitalDocument-ReadPermission-WritePermission-314 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DigitalDocument-ReadPermission-WritePermission-314-jsonld.html").to lint_cleanly}

  # Examples from sdo-videogame-examples.txt
  specify("sdo-videogame-examples.txt[47] - games-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-1-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[101] - VideoGame-315 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-315-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[153] - VideoGame-315 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-315-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[237] - games-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-2-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[279] - VideoGame-316 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-316-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[321] - VideoGame-316 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-316-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[422] - games-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-3-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[483] - VideoGame-317 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-317-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[544] - VideoGame-317 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-317-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[614] - games-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-4-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[641] - VideoGame-318 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-318-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[668] - VideoGame-318 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-318-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[704] - games-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-5-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[708] - VideoGame-319 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-319-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[712] - VideoGame-319 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-319-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[754] - games-6 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-6-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[770] - Game-320 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Game-320-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[786] - Game-320 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Game-320-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[818] - games-7 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/games-7-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[822] - VideoGame-321 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-321-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[826] - VideoGame-321 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-321-jsonld.html").to lint_cleanly}

  # Examples from sdo-ClaimReview-issue-1061-examples.txt
  specify("sdo-ClaimReview-issue-1061-examples.txt[46] - ClaimReview-322 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-322-microdata.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[94] - ClaimReview-322 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-322-rdfa.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[98] - ClaimReview-322 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-322-jsonld.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[147] - ClaimReview-323 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-323-microdata.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[151] - ClaimReview-323 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-323-rdfa.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[155] - ClaimReview-323 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-323-jsonld.html").to lint_cleanly}

  # Examples from sdo-exhibitionevent-examples.txt
  specify("sdo-exhibitionevent-examples.txt[12] - exhibitionevent-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/exhibitionevent-1-microdata.html").to lint_cleanly}
  specify("sdo-exhibitionevent-examples.txt[24] - ExhibitionEvent-324 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExhibitionEvent-324-rdfa.html").to lint_cleanly}
  specify("sdo-exhibitionevent-examples.txt[36] - ExhibitionEvent-324 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExhibitionEvent-324-jsonld.html").to lint_cleanly}

  # Examples from sdo-social-media-examples.txt
  specify("sdo-social-media-examples.txt[13] - social-media-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/social-media-1-microdata.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[37] - SocialMediaPosting-sharedContent-325 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SocialMediaPosting-sharedContent-325-rdfa.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[61] - SocialMediaPosting-sharedContent-325 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SocialMediaPosting-sharedContent-325-jsonld.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[105] - social-media-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/social-media-2-microdata.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[135] - LiveBlog-BlogPosting-326 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LiveBlog-BlogPosting-326-rdfa.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[166] - LiveBlog-BlogPosting-326 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LiveBlog-BlogPosting-326-jsonld.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[215] - social-media-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/social-media-3-microdata.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[229] - DiscussionForumPosting-327 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscussionForumPosting-327-rdfa.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[244] - DiscussionForumPosting-327 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscussionForumPosting-327-jsonld.html").to lint_cleanly}

  # Examples from sdo-itemlist-examples.txt
  specify("sdo-itemlist-examples.txt[14] - itemlist-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/itemlist-1-microdata.html").to lint_cleanly}
  specify("sdo-itemlist-examples.txt[31] - BreadcrumbList-ItemList-ListItem-itemListElement-item-328 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BreadcrumbList-ItemList-ListItem-itemListElement-item-328-rdfa.html").to lint_cleanly}
  specify("sdo-itemlist-examples.txt[47] - BreadcrumbList-ItemList-ListItem-itemListElement-item-328 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BreadcrumbList-ItemList-ListItem-itemListElement-item-328-jsonld.html").to lint_cleanly}

  # Examples from sdo-music-examples.txt
  specify("sdo-music-examples.txt[7] - music-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/music-1-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[11] - MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-329 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-329-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[15] - MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-329 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-329-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[84] - music-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/music-2-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[88] - Person-MusicComposition-Organization-330 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-MusicComposition-Organization-330-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[92] - Person-MusicComposition-Organization-330 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-MusicComposition-Organization-330-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[135] - music-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/music-3-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[139] - MusicGroup-City-MusicAlbum-331 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicGroup-City-MusicAlbum-331-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[143] - MusicGroup-City-MusicAlbum-331 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicGroup-City-MusicAlbum-331-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[217] - music-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/music-4-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[221] - MusicRecording-MusicComposition-332 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-332-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[225] - MusicRecording-MusicComposition-332 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-332-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[254] - music-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/music-5-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[258] - MusicRecording-MusicComposition-PublicationEvent-MusicRelease-333 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-PublicationEvent-MusicRelease-333-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[262] - MusicRecording-MusicComposition-PublicationEvent-MusicRelease-333 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-PublicationEvent-MusicRelease-333-jsonld.html").to lint_cleanly}

  # Examples from sdo-offeredby-examples.txt
  specify("sdo-offeredby-examples.txt[35] - offer-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offer-1-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[71] - Offer-offeredBy-Book-additionalType-334 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-offeredBy-Book-additionalType-334-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[116] - Offer-offeredBy-Book-additionalType-334 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-offeredBy-Book-additionalType-334-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[173] - offer-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offer-2-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[176] - Offer-makesOffer-335 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-makesOffer-335-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[216] - Offer-makesOffer-335 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-makesOffer-335-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[282] - offeredBy-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offeredBy-1-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[316] - offeredBy-Book-336 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offeredBy-Book-336-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[347] - offeredBy-Book-336 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offeredBy-Book-336-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[411] - offer-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offer-3-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[466] - Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-337 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-337-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[520] - Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-337 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-337-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[609] - offer-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offer-4-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[642] - Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-338 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-338-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[673] - Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-338 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-338-jsonld.html").to lint_cleanly}

  # Examples from sdo-library-examples.txt
  specify("sdo-library-examples.txt[45] - library-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/library-1-microdata.html").to lint_cleanly}
  specify("sdo-library-examples.txt[101] - Library-OpeningHoursSpecification-openingHoursSpecification-339 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Library-OpeningHoursSpecification-openingHoursSpecification-339-rdfa.html").to lint_cleanly}
  specify("sdo-library-examples.txt[156] - Library-OpeningHoursSpecification-openingHoursSpecification-339 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Library-OpeningHoursSpecification-openingHoursSpecification-339-jsonld.html").to lint_cleanly}

  # Examples from sdo-trip-examples.txt
  specify("sdo-trip-examples.txt[91] - trip-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/trip-1-microdata.html").to lint_cleanly}
  specify("sdo-trip-examples.txt[180] - Trip-TouristTrip-itinerary-340 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Trip-TouristTrip-itinerary-340-rdfa.html").to lint_cleanly}
  specify("sdo-trip-examples.txt[269] - Trip-TouristTrip-itinerary-340 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Trip-TouristTrip-itinerary-340-jsonld.html").to lint_cleanly}

  # Examples from MedicalScholarlyArticle-examples.txt
  specify("MedicalScholarlyArticle-examples.txt[21] - MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-341 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-341-microdata.html").to lint_cleanly}
  specify("MedicalScholarlyArticle-examples.txt[72] - MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-341 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-341-rdfa.html").to lint_cleanly}
  specify("MedicalScholarlyArticle-examples.txt[122] - MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-341 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-341-jsonld.html").to lint_cleanly}

  # Examples from medicalGuideline-examples.txt
  specify("medicalGuideline-examples.txt[14] - MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-342 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-342-microdata.html").to lint_cleanly}
  specify("medicalGuideline-examples.txt[46] - MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-342 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-342-rdfa.html").to lint_cleanly}
  specify("medicalGuideline-examples.txt[79] - MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-342 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-342-jsonld.html").to lint_cleanly}

  # Examples from medicalCondition-examples.txt
  specify("medicalCondition-examples.txt[34] - MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-343 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-343-microdata.html").to lint_cleanly}
  specify("medicalCondition-examples.txt[136] - MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-343 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-343-rdfa.html").to lint_cleanly}
  specify("medicalCondition-examples.txt[238] - MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-343 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-343-jsonld.html").to lint_cleanly}

  # Examples from medicalWebpage-examples.txt
  specify("medicalWebpage-examples.txt[15] - MedicalWebPage-DrugClass-344 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalWebPage-DrugClass-344-microdata.html").to lint_cleanly}
  specify("medicalWebpage-examples.txt[47] - MedicalWebPage-DrugClass-344 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalWebPage-DrugClass-344-rdfa.html").to lint_cleanly}
  specify("medicalWebpage-examples.txt[79] - MedicalWebPage-DrugClass-344 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalWebPage-DrugClass-344-jsonld.html").to lint_cleanly}

  # Examples from bsdo-newspaper-examples.txt
  specify("bsdo-newspaper-examples.txt[14] - Newspaper-345 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Newspaper-345-microdata.html").to lint_cleanly}
  specify("bsdo-newspaper-examples.txt[25] - Newspaper-345 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Newspaper-345-rdfa.html").to lint_cleanly}
  specify("bsdo-newspaper-examples.txt[34] - Newspaper-345 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Newspaper-345-jsonld.html").to lint_cleanly}

  # Examples from bsdo-thesis-examples.txt
  specify("bsdo-thesis-examples.txt[15] - Thesis-inSupportOf-346 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Thesis-inSupportOf-346-microdata.html").to lint_cleanly}
  specify("bsdo-thesis-examples.txt[27] - Thesis-inSupportOf-346 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Thesis-inSupportOf-346-rdfa.html").to lint_cleanly}
  specify("bsdo-thesis-examples.txt[37] - Thesis-inSupportOf-346 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Thesis-inSupportOf-346-jsonld.html").to lint_cleanly}

  # Examples from comics-examples.txt
  specify("comics-examples.txt[33] - ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-347 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-347-microdata.html").to lint_cleanly}
  specify("comics-examples.txt[82] - ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-347 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-347-rdfa.html").to lint_cleanly}
  specify("comics-examples.txt[131] - ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-347 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-347-jsonld.html").to lint_cleanly}

  # Examples from bsdo-chapter-examples.txt
  specify("bsdo-chapter-examples.txt[18] - Chapter-348 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Chapter-348-microdata.html").to lint_cleanly}
  specify("bsdo-chapter-examples.txt[35] - Chapter-348 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Chapter-348-rdfa.html").to lint_cleanly}
  specify("bsdo-chapter-examples.txt[51] - Chapter-348 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Chapter-348-jsonld.html").to lint_cleanly}

  # Examples from bsdo-atlas-examples.txt
  specify("bsdo-atlas-examples.txt[15] - Atlas-349 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Atlas-349-microdata.html").to lint_cleanly}
  specify("bsdo-atlas-examples.txt[27] - Atlas-349 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Atlas-349-rdfa.html").to lint_cleanly}
  specify("bsdo-atlas-examples.txt[37] - Atlas-349 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Atlas-349-jsonld.html").to lint_cleanly}

  # Examples from bsdo-collection-examples.txt
  specify("bsdo-collection-examples.txt[27] - Collection-350 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Collection-350-microdata.html").to lint_cleanly}
  specify("bsdo-collection-examples.txt[60] - Collection-350 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Collection-350-rdfa.html").to lint_cleanly}
  specify("bsdo-collection-examples.txt[92] - Collection-350 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Collection-350-jsonld.html").to lint_cleanly}

  # Examples from bsdo-audiobook-examples.txt
  specify("bsdo-audiobook-examples.txt[19] - Audiobook-readBy-351 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-readBy-351-microdata.html").to lint_cleanly}
  specify("bsdo-audiobook-examples.txt[39] - Audiobook-readBy-351 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-readBy-351-rdfa.html").to lint_cleanly}
  specify("bsdo-audiobook-examples.txt[59] - Audiobook-readBy-351 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-readBy-351-jsonld.html").to lint_cleanly}

  # Examples from bsdo-translation-examples.txt
  specify("bsdo-translation-examples.txt[26] - CreativeWork-Book-translator-translationOfWork-workTranslation-352 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Book-translator-translationOfWork-workTranslation-352-microdata.html").to lint_cleanly}
  specify("bsdo-translation-examples.txt[46] - CreativeWork-Book-translator-translationOfWork-workTranslation-352 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Book-translator-translationOfWork-workTranslation-352-rdfa.html").to lint_cleanly}
  specify("bsdo-translation-examples.txt[65] - CreativeWork-Book-translator-translationOfWork-workTranslation-352 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Book-translator-translationOfWork-workTranslation-352-jsonld.html").to lint_cleanly}

  # Examples from issue-1779-examples.txt
  specify("issue-1779-examples.txt[18] - EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-353 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-353-microdata.html").to lint_cleanly}
  specify("issue-1779-examples.txt[50] - EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-353 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-353-rdfa.html").to lint_cleanly}
  specify("issue-1779-examples.txt[79] - EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-353 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-353-jsonld.html").to lint_cleanly}
  specify("issue-1779-examples.txt[121] - EducationalOccupationalCredential-credentialCategory-354 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-354-microdata.html").to lint_cleanly}
  specify("issue-1779-examples.txt[144] - EducationalOccupationalCredential-credentialCategory-354 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-354-rdfa.html").to lint_cleanly}
  specify("issue-1779-examples.txt[165] - EducationalOccupationalCredential-credentialCategory-354 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-354-jsonld.html").to lint_cleanly}
  specify("issue-1779-examples.txt[198] - EducationalOccupationalCredential-Occupation-educationRequirements-355 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-Occupation-educationRequirements-355-microdata.html").to lint_cleanly}
  specify("issue-1779-examples.txt[209] - EducationalOccupationalCredential-Occupation-educationRequirements-355 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-Occupation-educationRequirements-355-rdfa.html").to lint_cleanly}
  specify("issue-1779-examples.txt[219] - EducationalOccupationalCredential-Occupation-educationRequirements-355 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-Occupation-educationRequirements-355-jsonld.html").to lint_cleanly}

  # Examples from issue-1457-examples.txt
  specify("issue-1457-examples.txt[7] - Event-Schedule-eventSchedule-356 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-356-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[11] - Event-Schedule-eventSchedule-356 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-356-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[15] - Event-Schedule-eventSchedule-356 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-356-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[43] - Event-Schedule-eventSchedule-357 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-357-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[47] - Event-Schedule-eventSchedule-357 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-357-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[51] - Event-Schedule-eventSchedule-357 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-357-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[74] - Event-Schedule-eventSchedule-358 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-358-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[78] - Event-Schedule-eventSchedule-358 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-358-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[82] - Event-Schedule-eventSchedule-358 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-358-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[107] - Event-Schedule-eventSchedule-359 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-359-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[111] - Event-Schedule-eventSchedule-359 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-359-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[115] - Event-Schedule-eventSchedule-359 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-359-jsonld.html").to lint_cleanly}

  # Examples from issue-1950-examples.txt
  specify("issue-1950-examples.txt[7] - CorrectionComment-correction-360 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CorrectionComment-correction-360-microdata.html").to lint_cleanly}
  specify("issue-1950-examples.txt[11] - CorrectionComment-correction-360 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CorrectionComment-correction-360-rdfa.html").to lint_cleanly}
  specify("issue-1950-examples.txt[16] - CorrectionComment-correction-360 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CorrectionComment-correction-360-jsonld.html").to lint_cleanly}

  # Examples from issue-2083-examples.txt
  specify("issue-2083-examples.txt[7] - JobPosting-applicantLocationRequirements-361 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-applicantLocationRequirements-361-microdata.html").to lint_cleanly}
  specify("issue-2083-examples.txt[11] - JobPosting-applicantLocationRequirements-361 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-applicantLocationRequirements-361-rdfa.html").to lint_cleanly}
  specify("issue-2083-examples.txt[16] - JobPosting-applicantLocationRequirements-361 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-applicantLocationRequirements-361-jsonld.html").to lint_cleanly}

  # Examples from issue-1156-examples.txt
  specify("issue-1156-examples.txt[57] - Legislation-362 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-362-microdata.html").to lint_cleanly}
  specify("issue-1156-examples.txt[112] - Legislation-362 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-362-rdfa.html").to lint_cleanly}
  specify("issue-1156-examples.txt[167] - Legislation-362 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-362-jsonld.html").to lint_cleanly}
  specify("issue-1156-examples.txt[257] - Legislation-LegislationObject-363 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-LegislationObject-363-microdata.html").to lint_cleanly}
  specify("issue-1156-examples.txt[302] - Legislation-LegislationObject-363 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-LegislationObject-363-rdfa.html").to lint_cleanly}
  specify("issue-1156-examples.txt[347] - Legislation-LegislationObject-363 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-LegislationObject-363-jsonld.html").to lint_cleanly}

  # Examples from issue-1698-examples.txt
  specify("issue-1698-examples.txt[7] - Person-Occupation-364 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-364-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[11] - Person-Occupation-364 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-364-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[15] - Person-Occupation-364 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-364-jsonld.html").to lint_cleanly}
  specify("issue-1698-examples.txt[36] - Person-Occupation-Role-365 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-Role-365-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[40] - Person-Occupation-Role-365 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-Role-365-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[44] - Person-Occupation-Role-365 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-Role-365-jsonld.html").to lint_cleanly}
  specify("issue-1698-examples.txt[76] - JobPosting-Occupation-366 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-Occupation-366-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[80] - JobPosting-Occupation-366 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-Occupation-366-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[84] - JobPosting-Occupation-366 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-Occupation-366-jsonld.html").to lint_cleanly}
  specify("issue-1698-examples.txt[109] - Occupation-MonetaryAmountDistribution-367 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-MonetaryAmountDistribution-367-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[113] - Occupation-MonetaryAmountDistribution-367 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-MonetaryAmountDistribution-367-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[117] - Occupation-MonetaryAmountDistribution-367 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-MonetaryAmountDistribution-367-jsonld.html").to lint_cleanly}

  # Examples from issue-894-examples.txt
  specify("issue-894-examples.txt[11] - defterm-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/defterm-1-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[19] - DefinedTerm-termCode-368 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-termCode-368-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[27] - DefinedTerm-termCode-368 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-termCode-368-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[58] - defterm-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/defterm-3-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[83] - DefinedTerm-DefinedTermSet-inDefinedTermSet-369 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-DefinedTermSet-inDefinedTermSet-369-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[107] - DefinedTerm-DefinedTermSet-inDefinedTermSet-369 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-DefinedTermSet-inDefinedTermSet-369-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[144] - defterm-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/defterm-4-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[152] - DefinedTerm-inDefinedTermSet-termCode-370 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-inDefinedTermSet-termCode-370-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[160] - DefinedTerm-inDefinedTermSet-termCode-370 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-inDefinedTermSet-termCode-370-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[182] - catcode-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/catcode-2-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[194] - CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-371 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-371-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[206] - CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-371 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-371-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[243] - catcode-5 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/catcode-5-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[265] - CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-372 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-372-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[286] - CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-372 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-372-jsonld.html").to lint_cleanly}

  # Examples from issue-1050-examples.txt
  specify("issue-1050-examples.txt[7] - contentReferenceTime-Event-Article-about-373 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/contentReferenceTime-Event-Article-about-373-microdata.html").to lint_cleanly}
  specify("issue-1050-examples.txt[11] - contentReferenceTime-Event-Article-about-373 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/contentReferenceTime-Event-Article-about-373-rdfa.html").to lint_cleanly}
  specify("issue-1050-examples.txt[15] - contentReferenceTime-Event-Article-about-373 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/contentReferenceTime-Event-Article-about-373-jsonld.html").to lint_cleanly}

  # Examples from issue-1810-examples.txt
  specify("issue-1810-examples.txt[67] - tourism-10 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-10-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[117] - TouristDestination-374 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristDestination-374-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[179] - TouristDestination-374 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristDestination-374-jsonld.html").to lint_cleanly}
  specify("issue-1810-examples.txt[283] - tourism-11 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-11-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[315] - TouristTrip-itinerary-375 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-itinerary-375-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[359] - TouristTrip-itinerary-375 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-itinerary-375-jsonld.html").to lint_cleanly}
  specify("issue-1810-examples.txt[434] - tourism-12 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-12-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[451] - TouristTrip-Trip-itinerary-376 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-Trip-itinerary-376-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[472] - TouristTrip-Trip-itinerary-376 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-Trip-itinerary-376-jsonld.html").to lint_cleanly}
  specify("issue-1810-examples.txt[631] - tourism-13 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/tourism-13-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[726] - TouristTrip-377 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-377-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[858] - TouristTrip-377 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-377-jsonld.html").to lint_cleanly}

  # Examples from issue-1045-examples.txt
  specify("issue-1045-examples.txt[7] - datafeed-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/datafeed-3-microdata.html").to lint_cleanly}
  specify("issue-1045-examples.txt[11] - ReserveAction-LinkRole-378 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-378-rdfa.html").to lint_cleanly}
  specify("issue-1045-examples.txt[15] - ReserveAction-LinkRole-378 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-378-jsonld.html").to lint_cleanly}
  specify("issue-1045-examples.txt[43] - datafeed-4 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/datafeed-4-microdata.html").to lint_cleanly}
  specify("issue-1045-examples.txt[47] - ReserveAction-LinkRole-379 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-379-rdfa.html").to lint_cleanly}
  specify("issue-1045-examples.txt[51] - ReserveAction-LinkRole-379 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-379-jsonld.html").to lint_cleanly}
  specify("issue-1045-examples.txt[60] - datafeed-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/datafeed-3-microdata.html").to lint_cleanly}
  specify("issue-1045-examples.txt[64] - ReserveAction-LinkRole-380 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-380-rdfa.html").to lint_cleanly}
  specify("issue-1045-examples.txt[68] - ReserveAction-LinkRole-380 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-380-jsonld.html").to lint_cleanly}

  # Examples from issue-2085-examples.txt
  specify("issue-2085-examples.txt[7] - ProgramMembership-membershipPointsEarned-381 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProgramMembership-membershipPointsEarned-381-microdata.html").to lint_cleanly}
  specify("issue-2085-examples.txt[11] - ProgramMembership-membershipPointsEarned-381 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProgramMembership-membershipPointsEarned-381-rdfa.html").to lint_cleanly}
  specify("issue-2085-examples.txt[16] - ProgramMembership-membershipPointsEarned-381 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProgramMembership-membershipPointsEarned-381-jsonld.html").to lint_cleanly}

  # Examples from issue-271-examples.txt
  specify("issue-271-examples.txt[7] - Quotation-spokenByCharacter-382 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-382-microdata.html").to lint_cleanly}
  specify("issue-271-examples.txt[11] - Quotation-spokenByCharacter-382 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-382-rdfa.html").to lint_cleanly}
  specify("issue-271-examples.txt[15] - Quotation-spokenByCharacter-382 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-382-jsonld.html").to lint_cleanly}
  specify("issue-271-examples.txt[40] - Quotation-spokenByCharacter-383 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-383-microdata.html").to lint_cleanly}
  specify("issue-271-examples.txt[44] - Quotation-spokenByCharacter-383 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-383-rdfa.html").to lint_cleanly}
  specify("issue-271-examples.txt[48] - Quotation-spokenByCharacter-383 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-383-jsonld.html").to lint_cleanly}

  # Examples from issue-1670-examples.txt
  specify("issue-1670-examples.txt[7] - CreativeWork-Thing-384 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Thing-384-microdata.html").to lint_cleanly}
  specify("issue-1670-examples.txt[11] - CreativeWork-Thing-384 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Thing-384-rdfa.html").to lint_cleanly}
  specify("issue-1670-examples.txt[15] - CreativeWork-Thing-384 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Thing-384-jsonld.html").to lint_cleanly}

  # Examples from issue-1741-examples.txt
  specify("issue-1741-examples.txt[7] - ActionAccessSpecification-MediaSubscription-ListenAction-385 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ActionAccessSpecification-MediaSubscription-ListenAction-385-microdata.html").to lint_cleanly}
  specify("issue-1741-examples.txt[11] - ActionAccessSpecification-MediaSubscription-ListenAction-385 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ActionAccessSpecification-MediaSubscription-ListenAction-385-rdfa.html").to lint_cleanly}
  specify("issue-1741-examples.txt[15] - ActionAccessSpecification-MediaSubscription-ListenAction-385 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ActionAccessSpecification-MediaSubscription-ListenAction-385-jsonld.html").to lint_cleanly}

  # Examples from issue-1062-examples.txt
  specify("issue-1062-examples.txt[9] - HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-386 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-386-microdata.html").to lint_cleanly}
  specify("issue-1062-examples.txt[13] - HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-386 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-386-rdfa.html").to lint_cleanly}
  specify("issue-1062-examples.txt[17] - HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-386 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-386-jsonld.html").to lint_cleanly}

  # Examples from issue-template-examples.txt
  specify("issue-template-examples.txt[7] - @@@@comma-separated-list-here@@@@ replace @@@@ with content.-387 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/@@@@comma-separated-list-here@@@@ replace @@@@ with content.-387-microdata.html").to lint_cleanly}
  specify("issue-template-examples.txt[11] - @@@@comma-separated-list-here@@@@ replace @@@@ with content.-387 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/@@@@comma-separated-list-here@@@@ replace @@@@ with content.-387-rdfa.html").to lint_cleanly}
  specify("issue-template-examples.txt[15] - @@@@comma-separated-list-here@@@@ replace @@@@ with content.-387 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/@@@@comma-separated-list-here@@@@ replace @@@@ with content.-387-jsonld.html").to lint_cleanly}

  # Examples from issue-1689-examples.txt
  specify("issue-1689-examples.txt[7] - EmployerAggregateRating-388 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmployerAggregateRating-388-microdata.html").to lint_cleanly}
  specify("issue-1689-examples.txt[11] - EmployerAggregateRating-388 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmployerAggregateRating-388-rdfa.html").to lint_cleanly}
  specify("issue-1689-examples.txt[15] - EmployerAggregateRating-388 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmployerAggregateRating-388-jsonld.html").to lint_cleanly}
  specify("issue-1689-examples.txt[39] - Review-Rating-reviewAspect-389 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Review-Rating-reviewAspect-389-microdata.html").to lint_cleanly}
  specify("issue-1689-examples.txt[43] - Review-Rating-reviewAspect-389 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Review-Rating-reviewAspect-389-rdfa.html").to lint_cleanly}
  specify("issue-1689-examples.txt[47] - Review-Rating-reviewAspect-389 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Review-Rating-reviewAspect-389-jsonld.html").to lint_cleanly}

  # Examples from issue-447-examples.txt
  specify("issue-447-examples.txt[7] - EventSeries-390 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventSeries-390-microdata.html").to lint_cleanly}
  specify("issue-447-examples.txt[11] - EventSeries-390 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventSeries-390-rdfa.html").to lint_cleanly}
  specify("issue-447-examples.txt[15] - EventSeries-390 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventSeries-390-jsonld.html").to lint_cleanly}

  # Examples from issue-2109-examples.txt
  specify("issue-2109-examples.txt[7] - RadioBroadcastService-callSign-391 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioBroadcastService-callSign-391-microdata.html").to lint_cleanly}
  specify("issue-2109-examples.txt[11] - RadioBroadcastService-callSign-391 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioBroadcastService-callSign-391-rdfa.html").to lint_cleanly}
  specify("issue-2109-examples.txt[15] - RadioBroadcastService-callSign-391 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioBroadcastService-callSign-391-jsonld.html").to lint_cleanly}

  # Examples from issue-383-examples.txt
  specify("issue-383-examples.txt[7] - Grant-392 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-392-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[11] - Grant-392 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-392-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[15] - Grant-392 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-392-jsonld.html").to lint_cleanly}
  specify("issue-383-examples.txt[41] - Grant-393 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-393-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[45] - Grant-393 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-393-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[49] - Grant-393 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-393-jsonld.html").to lint_cleanly}
  specify("issue-383-examples.txt[71] - Grant-394 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-394-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[75] - Grant-394 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-394-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[79] - Grant-394 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-394-jsonld.html").to lint_cleanly}
  specify("issue-383-examples.txt[112] - Grant-395 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-395-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[116] - Grant-395 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-395-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[120] - Grant-395 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-395-jsonld.html").to lint_cleanly}

  # Examples from issue-1253-examples.txt
  specify("issue-1253-examples.txt[13] - BrokerageAccount-396 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BrokerageAccount-396-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[24] - BrokerageAccount-396 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BrokerageAccount-396-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[35] - BrokerageAccount-396 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BrokerageAccount-396-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[70] - InvestmentFund-397 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentFund-397-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[81] - InvestmentFund-397 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentFund-397-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[92] - InvestmentFund-397 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentFund-397-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[141] - MortgageLoan-RepaymentSpecification-398 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MortgageLoan-RepaymentSpecification-398-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[176] - MortgageLoan-RepaymentSpecification-398 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MortgageLoan-RepaymentSpecification-398-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[210] - MortgageLoan-RepaymentSpecification-398 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MortgageLoan-RepaymentSpecification-398-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[271] - ExchangeRateSpecification-399 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExchangeRateSpecification-399-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[304] - ExchangeRateSpecification-399 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExchangeRateSpecification-399-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[336] - ExchangeRateSpecification-399 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExchangeRateSpecification-399-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[384] - CreditCard-400 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-400-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[406] - CreditCard-400 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-400-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[428] - CreditCard-400 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-400-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[476] - BankTransfer-401 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankTransfer-401-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[485] - BankTransfer-401 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankTransfer-401-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[494] - BankTransfer-401 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankTransfer-401-jsonld.html").to lint_cleanly}

  # Examples from issue-1525-examples.txt
  specify("issue-1525-examples.txt[7] - BasicNewsArticle-402 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BasicNewsArticle-402-microdata.html").to lint_cleanly}
  specify("issue-1525-examples.txt[11] - BasicNewsArticle-402 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BasicNewsArticle-402-rdfa.html").to lint_cleanly}
  specify("issue-1525-examples.txt[15] - BasicNewsArticle-402 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BasicNewsArticle-402-jsonld.html").to lint_cleanly}

  # Examples from issue-1389-examples.txt
  specify("issue-1389-examples.txt[7] - speakable-cssSelector-SpeakableSpecification-403 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-403-microdata.html").to lint_cleanly}
  specify("issue-1389-examples.txt[11] - speakable-cssSelector-SpeakableSpecification-403 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-403-rdfa.html").to lint_cleanly}
  specify("issue-1389-examples.txt[15] - speakable-cssSelector-SpeakableSpecification-403 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-403-jsonld.html").to lint_cleanly}
  specify("issue-1389-examples.txt[60] - speakable-cssSelector-SpeakableSpecification-404 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-404-microdata.html").to lint_cleanly}
  specify("issue-1389-examples.txt[75] - speakable-cssSelector-SpeakableSpecification-404 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-404-rdfa.html").to lint_cleanly}
  specify("issue-1389-examples.txt[79] - speakable-cssSelector-SpeakableSpecification-404 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-404-jsonld.html").to lint_cleanly}

  # Examples from issue-2021-examples.txt
  specify("issue-2021-examples.txt[7] - Clip-endOffset-startOffset-405 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Clip-endOffset-startOffset-405-microdata.html").to lint_cleanly}
  specify("issue-2021-examples.txt[11] - Clip-endOffset-startOffset-405 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Clip-endOffset-startOffset-405-rdfa.html").to lint_cleanly}
  specify("issue-2021-examples.txt[16] - Clip-endOffset-startOffset-405 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Clip-endOffset-startOffset-405-jsonld.html").to lint_cleanly}

  # Examples from issue-1759-examples.txt
  specify("issue-1759-examples.txt[9] - extent-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/extent-1-microdata.html").to lint_cleanly}
  specify("issue-1759-examples.txt[17] - materialExtent-CreativeWork-406 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-406-rdfa.html").to lint_cleanly}
  specify("issue-1759-examples.txt[24] - materialExtent-CreativeWork-406 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-406-jsonld.html").to lint_cleanly}
  specify("issue-1759-examples.txt[43] - extent-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/extent-2-microdata.html").to lint_cleanly}
  specify("issue-1759-examples.txt[59] - materialExtent-CreativeWork-407 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-407-rdfa.html").to lint_cleanly}
  specify("issue-1759-examples.txt[74] - materialExtent-CreativeWork-407 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-407-jsonld.html").to lint_cleanly}

  # Examples from issue-1423-examples.txt
  specify("issue-1423-examples.txt[7] - WebAPI-documentation-termsOfService-408 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebAPI-documentation-termsOfService-408-microdata.html").to lint_cleanly}
  specify("issue-1423-examples.txt[11] - WebAPI-documentation-termsOfService-408 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebAPI-documentation-termsOfService-408-rdfa.html").to lint_cleanly}
  specify("issue-1423-examples.txt[15] - WebAPI-documentation-termsOfService-408 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebAPI-documentation-termsOfService-408-jsonld.html").to lint_cleanly}

  # Examples from issue-1758-examples.txt
  specify("issue-1758-examples.txt[16] - arch-1 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/arch-1-microdata.html").to lint_cleanly}
  specify("issue-1758-examples.txt[29] - ArchiveOrganization-archiveHeld-409 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveOrganization-archiveHeld-409-rdfa.html").to lint_cleanly}
  specify("issue-1758-examples.txt[42] - ArchiveOrganization-archiveHeld-409 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveOrganization-archiveHeld-409-jsonld.html").to lint_cleanly}
  specify("issue-1758-examples.txt[88] - arch-2 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/arch-2-microdata.html").to lint_cleanly}
  specify("issue-1758-examples.txt[115] - ArchiveComponent-holdingArchive-410 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-holdingArchive-410-rdfa.html").to lint_cleanly}
  specify("issue-1758-examples.txt[142] - ArchiveComponent-holdingArchive-410 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-holdingArchive-410-jsonld.html").to lint_cleanly}
  specify("issue-1758-examples.txt[198] - arch-3 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/arch-3-microdata.html").to lint_cleanly}
  specify("issue-1758-examples.txt[227] - ArchiveComponent-411 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-411-rdfa.html").to lint_cleanly}
  specify("issue-1758-examples.txt[254] - ArchiveComponent-411 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-411-jsonld.html").to lint_cleanly}
end
