$:.unshift File.expand_path("..", __FILE__)
require 'spec_helper'

describe "Examples" do
  before(:all) {RDF::Reasoner.apply(:rdfs, :owl, :schema)}

  # Examples from sdo-mainEntity-examples.txt
  specify("sdo-mainEntity-examples.txt[12] - eg-0382 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0382-microdata.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[23] - mainEntity-1 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntity-1-rdfa.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[27] - mainEntity-1 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntity-1-jsonld.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[55] - eg-0383 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0383-microdata.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[64] - mainEntityOfPage-2 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntityOfPage-2-rdfa.html").to lint_cleanly}
  specify("sdo-mainEntity-examples.txt[73] - mainEntityOfPage-2 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/mainEntityOfPage-2-jsonld.html").to lint_cleanly}

  # Examples from sdo-invoice-examples.txt
  specify("sdo-invoice-examples.txt[18] - eg-0374 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0374-microdata.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[43] - Invoice-BankOrCreditUnion-Person-PriceSpecification-3 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-BankOrCreditUnion-Person-PriceSpecification-3-rdfa.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[68] - Invoice-BankOrCreditUnion-Person-PriceSpecification-3 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-BankOrCreditUnion-Person-PriceSpecification-3-jsonld.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[117] - eg-0375 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0375-microdata.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[155] - Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4-rdfa.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[193] - Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Invoice-Order-LocalBusiness-Person-PriceSpecification-Service-4-jsonld.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[259] - eg-0376 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0376-microdata.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[293] - Order-OrderItem-Organization-Person-5 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Order-OrderItem-Organization-Person-5-rdfa.html").to lint_cleanly}
  specify("sdo-invoice-examples.txt[327] - Order-OrderItem-Organization-Person-5 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Order-OrderItem-Organization-Person-5-jsonld.html").to lint_cleanly}

  # Examples from sdo-course-examples.txt
  specify("sdo-course-examples.txt[22] - eg-0332 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0332-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[26] - Course-CourseInstance-hasCourseInstance-courseMode-6 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-6-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[48] - Course-CourseInstance-hasCourseInstance-courseMode-6 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-6-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[107] - eg-0333 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0333-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[111] - Course-CourseInstance-hasCourseInstance-courseMode-7 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-7-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[153] - Course-CourseInstance-hasCourseInstance-courseMode-7 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-7-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[207] - eg-0334 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0334-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[211] - Course-CourseInstance-hasCourseInstance-courseMode-8 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-8-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[239] - Course-CourseInstance-hasCourseInstance-courseMode-8 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-CourseInstance-hasCourseInstance-courseMode-8-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[287] - eg-0335 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0335-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[291] - educationalCredentialAwarded-9 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-9-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[301] - educationalCredentialAwarded-9 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-9-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[328] - eg-0336 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0336-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[332] - educationalCredentialAwarded-10 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-10-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[347] - educationalCredentialAwarded-10 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/educationalCredentialAwarded-10-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[385] - eg-0337 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0337-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[389] - instructor-provider-11 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/instructor-provider-11-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[420] - instructor-provider-11 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/instructor-provider-11-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[473] - eg-0338 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0338-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[477] - Course-courseCode-provider-12 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-courseCode-provider-12-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[495] - Course-courseCode-provider-12 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Course-courseCode-provider-12-jsonld.html").to lint_cleanly}
  specify("sdo-course-examples.txt[517] - eg-0339 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0339-microdata.html").to lint_cleanly}
  specify("sdo-course-examples.txt[521] - comma-separated-list-here replace  with content.-13 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/comma-separated-list-here replace  with content.-13-rdfa.html").to lint_cleanly}
  specify("sdo-course-examples.txt[525] - comma-separated-list-here replace  with content.-13 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/comma-separated-list-here replace  with content.-13-jsonld.html").to lint_cleanly}

  # Examples from sdo-lrmi-examples.txt
  specify("sdo-lrmi-examples.txt[14] - eg-0379 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0379-microdata.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[35] - learningResourceType-educationalLevel-audience-EducationalAudience-educationalRole-14 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/learningResourceType-educationalLevel-audience-EducationalAudience-educationalRole-14-rdfa.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[57] - learningResourceType-educationalLevel-audience-EducationalAudience-educationalRole-14 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/learningResourceType-educationalLevel-audience-EducationalAudience-educationalRole-14-jsonld.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[112] - eg-0380 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0380-microdata.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[178] - typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-educationalLevel-15 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-educationalLevel-15-rdfa.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[241] - typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-educationalLevel-15 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/typicalAgeRange-timeRequired-educationalAlignment-AlignmentObject-educationalFramework-alignmentType-targetName-targetUrl-educationalLevel-15-jsonld.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[324] - eg-0381 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0381-microdata.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[341] - isBasedOn-16 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/isBasedOn-16-rdfa.html").to lint_cleanly}
  specify("sdo-lrmi-examples.txt[358] - isBasedOn-16 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/isBasedOn-16-jsonld.html").to lint_cleanly}

  # Examples from sdo-property-value-examples.txt
  specify("sdo-property-value-examples.txt[20] - eg-0404 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0404-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[54] - ImageObject-PropertyValue-additionalProperty-17 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-PropertyValue-additionalProperty-17-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[88] - ImageObject-PropertyValue-additionalProperty-17 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-PropertyValue-additionalProperty-17-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[145] - eg-0405 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0405-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[158] - PropertyValue-additionalProperty-18 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-18-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[162] - PropertyValue-additionalProperty-18 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-18-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[180] - eg-0406 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0406-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[193] - PropertyValue-additionalProperty-19 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-19-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[197] - PropertyValue-additionalProperty-19 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-19-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[217] - eg-0407 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0407-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[231] - PropertyValue-additionalProperty-20 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-20-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[235] - PropertyValue-additionalProperty-20 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-20-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[254] - eg-0408 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0408-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[268] - PropertyValue-additionalProperty-21 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-21-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[272] - PropertyValue-additionalProperty-21 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-21-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[292] - eg-0409 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0409-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[306] - PropertyValue-additionalProperty-22 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-22-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[310] - PropertyValue-additionalProperty-22 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-22-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[330] - eg-0410 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0410-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[344] - PropertyValue-23 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-23-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[348] - PropertyValue-23 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-23-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[365] - eg-0411 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0411-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[377] - PropertyValue-additionalProperty-24 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-24-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[381] - PropertyValue-additionalProperty-24 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-24-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[398] - eg-0412 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0412-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[410] - PropertyValue-additionalProperty-25 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-25-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[414] - PropertyValue-additionalProperty-25 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-25-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[433] - eg-0413 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0413-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[446] - PropertyValue-additionalProperty-26 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-26-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[450] - PropertyValue-additionalProperty-26 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-26-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[470] - eg-0414 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0414-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[484] - PropertyValue-additionalProperty-27 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-27-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[488] - PropertyValue-additionalProperty-27 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-27-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[507] - eg-0415 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0415-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[521] - PropertyValue-additionalProperty-28 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-28-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[525] - PropertyValue-additionalProperty-28 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-28-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[550] - eg-0416 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0416-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[569] - PropertyValue-additionalProperty-29 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-29-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[573] - PropertyValue-additionalProperty-29 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-29-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[596] - eg-0417 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0417-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[613] - PropertyValue-additionalProperty-30 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-30-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[617] - PropertyValue-additionalProperty-30 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-30-jsonld.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[643] - eg-0418 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0418-microdata.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[664] - PropertyValue-additionalProperty-31 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-31-rdfa.html").to lint_cleanly}
  specify("sdo-property-value-examples.txt[668] - PropertyValue-additionalProperty-31 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PropertyValue-additionalProperty-31-jsonld.html").to lint_cleanly}

  # Examples from sdo-periodical-examples.txt
  specify("sdo-periodical-examples.txt[20] - eg-0398 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0398-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[48] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[76] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-32-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[144] - eg-0399 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0399-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[189] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[232] - Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Article-Periodical-PublicationIssue-PublicationVolume-ScholarlyArticle-33-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[295] - eg-0400 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0400-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[344] - Book-PublicationVolume-34 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-PublicationVolume-34-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[393] - Book-PublicationVolume-34 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-PublicationVolume-34-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[475] - eg-0401 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0401-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[497] - PublicationIssue-PublicationVolume-ScholarlyArticle-35 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PublicationIssue-PublicationVolume-ScholarlyArticle-35-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[519] - PublicationIssue-PublicationVolume-ScholarlyArticle-35 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PublicationIssue-PublicationVolume-ScholarlyArticle-35-jsonld.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[587] - eg-0402 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0402-microdata.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[629] - exampleOfWork-workExample-36 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/exampleOfWork-workExample-36-rdfa.html").to lint_cleanly}
  specify("sdo-periodical-examples.txt[673] - exampleOfWork-workExample-36 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/exampleOfWork-workExample-36-jsonld.html").to lint_cleanly}

  # Examples from sdo-datafeed-examples.txt
  specify("sdo-datafeed-examples.txt[13] - eg-0344 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0344-microdata.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[17] - DataFeed-37 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DataFeed-37-rdfa.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[21] - DataFeed-37 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DataFeed-37-jsonld.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[58] - eg-0345 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0345-microdata.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[62] - MobileApplication-DataFeed-supportingData-38 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MobileApplication-DataFeed-supportingData-38-rdfa.html").to lint_cleanly}
  specify("sdo-datafeed-examples.txt[66] - MobileApplication-DataFeed-supportingData-38 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MobileApplication-DataFeed-supportingData-38-jsonld.html").to lint_cleanly}

  # Examples from sdo-sponsor-examples.txt
  specify("sdo-sponsor-examples.txt[27] - eg-0426 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0426-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[71] - Event-39 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-39-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[121] - Event-39 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-39-jsonld.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[179] - eg-0427 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0427-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[187] - Person-40 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-40-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[195] - Person-40 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-40-jsonld.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[217] - eg-0428 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0428-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[226] - Person-41 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-41-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[235] - Person-41 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-41-jsonld.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[259] - eg-0429 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0429-microdata.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[270] - Organization-42 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-42-rdfa.html").to lint_cleanly}
  specify("sdo-sponsor-examples.txt[281] - Organization-42 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-42-jsonld.html").to lint_cleanly}

  # Examples from sdo-menu-examples.txt
  specify("sdo-menu-examples.txt[9] - eg-0385 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0385-microdata.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[13] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43-rdfa.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[17] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-43-jsonld.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[74] - eg-0386 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0386-microdata.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[78] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44-rdfa.html").to lint_cleanly}
  specify("sdo-menu-examples.txt[82] - Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Menu-MenuSection-hasMenuItem-hasMenuSection-NutritionInformation-MenuItem-44-jsonld.html").to lint_cleanly}

  # Examples from sdo-tv-listing-examples.txt
  specify("sdo-tv-listing-examples.txt[7] - eg-0442 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0442-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[19] - Organization-BroadcastService-45 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-45-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[31] - Organization-BroadcastService-45 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-45-jsonld.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[54] - eg-0443 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0443-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[72] - Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[90] - Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-BroadcastService-TelevisionChannel-CableOrSatelliteService-46-jsonld.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[121] - eg-0444 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0444-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[140] - BroadcastEvent-BroadcastService-TVEpisode-47 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-BroadcastService-TVEpisode-47-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[159] - BroadcastEvent-BroadcastService-TVEpisode-47 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-BroadcastService-TVEpisode-47-jsonld.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[190] - eg-0445 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0445-microdata.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[213] - BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48-rdfa.html").to lint_cleanly}
  specify("sdo-tv-listing-examples.txt[236] - BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BroadcastEvent-SportsEvent-broadcastOfEvent-isLiveBroadcast-videoFormat-competitor-48-jsonld.html").to lint_cleanly}

  # Examples from sdo-tourism-examples.txt
  specify("sdo-tourism-examples.txt[12] - eg-0431 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0431-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[27] - TouristAttraction-isAccessibleForFree-49 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-49-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[42] - TouristAttraction-isAccessibleForFree-49 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-49-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[69] - eg-0432 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0432-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[95] - AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[121] - AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AmusementPark-TouristAttraction-isAccessibleForFree-currenciesAccepted-openingHours-paymentAccepted-50-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[145] - eg-0433 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0433-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[165] - TouristAttraction-availableLanguage-51 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-availableLanguage-51-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[185] - TouristAttraction-availableLanguage-51 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-availableLanguage-51-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[218] - eg-0434 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0434-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[244] - TouristAttraction-touristType-Museum-52 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Museum-52-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[269] - TouristAttraction-touristType-Museum-52 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Museum-52-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[297] - eg-0435 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0435-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[309] - TouristAttraction-publicAccess-53 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-publicAccess-53-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[321] - TouristAttraction-publicAccess-53 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-publicAccess-53-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[344] - eg-0436 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0436-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[361] - TouristAttraction-event-Event-54 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-event-Event-54-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[378] - TouristAttraction-event-Event-54 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-event-Event-54-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[412] - eg-0437 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0437-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[438] - TouristAttraction-isAccessibleForFree-55 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-55-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[461] - TouristAttraction-isAccessibleForFree-55 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-isAccessibleForFree-55-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[528] - eg-0438 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0438-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[559] - TouristAttraction-touristType-isAccessibleForFree-Cemetery-56 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-isAccessibleForFree-Cemetery-56-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[589] - TouristAttraction-touristType-isAccessibleForFree-Cemetery-56 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-isAccessibleForFree-Cemetery-56-jsonld.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[644] - eg-0439 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0439-microdata.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[672] - TouristAttraction-touristType-Winery-57 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Winery-57-rdfa.html").to lint_cleanly}
  specify("sdo-tourism-examples.txt[699] - TouristAttraction-touristType-Winery-57 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristAttraction-touristType-Winery-57-jsonld.html").to lint_cleanly}

  # Examples from sdo-map-examples.txt
  specify("sdo-map-examples.txt[10] - eg-0384 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0384-microdata.html").to lint_cleanly}
  specify("sdo-map-examples.txt[20] - Map-VenueMap-58 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Map-VenueMap-58-rdfa.html").to lint_cleanly}
  specify("sdo-map-examples.txt[30] - Map-VenueMap-58 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Map-VenueMap-58-jsonld.html").to lint_cleanly}

  # Examples from examples.txt
  specify("examples.txt[22] - eg-0001 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0001-microdata.html").to lint_cleanly}
  specify("examples.txt[52] - Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59-rdfa.html").to lint_cleanly}
  specify("examples.txt[82] - Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-PostalAddress-addressRegion-postalCode-address-streetAddress-telephone-email-url-addressLocality-59-jsonld.html").to lint_cleanly}
  specify("examples.txt[118] - eg-0015 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0015-microdata.html").to lint_cleanly}
  specify("examples.txt[132] - Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60-rdfa.html").to lint_cleanly}
  specify("examples.txt[146] - Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-LocalBusiness-address-streetAddress-addressLocality-PostalAddress-telephone-60-jsonld.html").to lint_cleanly}
  specify("examples.txt[171] - eg-0003 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0003-microdata.html").to lint_cleanly}
  specify("examples.txt[179] - Painting-genre-61 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-genre-61-rdfa.html").to lint_cleanly}
  specify("examples.txt[187] - Painting-genre-61 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-genre-61-jsonld.html").to lint_cleanly}
  specify("examples.txt[218] - eg-0004 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0004-microdata.html").to lint_cleanly}
  specify("examples.txt[253] - Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62-rdfa.html").to lint_cleanly}
  specify("examples.txt[288] - Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-AggregateRating-FoodEstablishment-LocalBusiness-aggregateRating-ratingValue-reviewCount-62-jsonld.html").to lint_cleanly}
  specify("examples.txt[331] - eg-0005 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0005-microdata.html").to lint_cleanly}
  specify("examples.txt[344] - Place-GeoCoordinates-latitude-longitude-geo-63 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-GeoCoordinates-latitude-longitude-geo-63-rdfa.html").to lint_cleanly}
  specify("examples.txt[357] - Place-GeoCoordinates-latitude-longitude-geo-63 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Place-GeoCoordinates-latitude-longitude-geo-63-jsonld.html").to lint_cleanly}
  specify("examples.txt[384] - eg-0006 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0006-microdata.html").to lint_cleanly}
  specify("examples.txt[403] - MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64-rdfa.html").to lint_cleanly}
  specify("examples.txt[422] - MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MediaObject-AudioObject-encodingFormat-contentUrl-description-duration-64-jsonld.html").to lint_cleanly}
  specify("examples.txt[454] - eg-0007 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0007-microdata.html").to lint_cleanly}
  specify("examples.txt[485] - Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65-rdfa.html").to lint_cleanly}
  specify("examples.txt[515] - Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-PostalAddress-address-streetAddress-postalCode-addressLocality-faxNumber-telephone-65-jsonld.html").to lint_cleanly}
  specify("examples.txt[570] - eg-0008 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0008-microdata.html").to lint_cleanly}
  specify("examples.txt[600] - NGO-66 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NGO-66-rdfa.html").to lint_cleanly}
  specify("examples.txt[630] - NGO-66 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NGO-66-jsonld.html").to lint_cleanly}
  specify("examples.txt[677] - eg-0009 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0009-microdata.html").to lint_cleanly}
  specify("examples.txt[705] - Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67-rdfa.html").to lint_cleanly}
  specify("examples.txt[733] - Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-AggregateOffer-location-startDate-address-offers-offerCount-67-jsonld.html").to lint_cleanly}
  specify("examples.txt[785] - eg-0010 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0010-microdata.html").to lint_cleanly}
  specify("examples.txt[842] - Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68-rdfa.html").to lint_cleanly}
  specify("examples.txt[897] - Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-Offer-Review-Rating-price-aggregateRating-ratingValue-reviewCount-availability-InStock-68-jsonld.html").to lint_cleanly}
  specify("examples.txt[966] - eg-0011 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0011-microdata.html").to lint_cleanly}
  specify("examples.txt[997] - Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69-rdfa.html").to lint_cleanly}
  specify("examples.txt[1020] - Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Product-AggregateRating-AggregateOffer-Offer-aggregateRating-image-offers-69-jsonld.html").to lint_cleanly}
  specify("examples.txt[1087] - eg-0012 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0012-microdata.html").to lint_cleanly}
  specify("examples.txt[1146] - WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70-rdfa.html").to lint_cleanly}
  specify("examples.txt[1205] - WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-Book-AggregateRating-Offer-Review-CreativeWork-mainEntity-70-jsonld.html").to lint_cleanly}
  specify("examples.txt[1292] - eg-0013 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0013-microdata.html").to lint_cleanly}
  specify("examples.txt[1338] - Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71-rdfa.html").to lint_cleanly}
  specify("examples.txt[1383] - Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recipe-NutritionInformation-image-datePublished-prepTime-cookTime-recipeYield-recipeIngredient-calories-fatContent-suitableForDiet-LowFatDiet-RestrictedDiet-71-jsonld.html").to lint_cleanly}
  specify("examples.txt[1473] - eg-0014 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0014-microdata.html").to lint_cleanly}
  specify("examples.txt[1533] - VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72-rdfa.html").to lint_cleanly}
  specify("examples.txt[1593] - VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoObject-MusicGroup-MusicRecording-Event-video-interactionStatistic-InteractionCounter-duration-interactionStatistic-interactionType-72-jsonld.html").to lint_cleanly}
  specify("examples.txt[1676] - eg-0016 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0016-microdata.html").to lint_cleanly}
  specify("examples.txt[1687] - ItemList-73 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-73-rdfa.html").to lint_cleanly}
  specify("examples.txt[1698] - ItemList-73 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-73-jsonld.html").to lint_cleanly}
  specify("examples.txt[1727] - eg-0017 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0017-microdata.html").to lint_cleanly}
  specify("examples.txt[1764] - Movie-74 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-74-rdfa.html").to lint_cleanly}
  specify("examples.txt[1801] - Movie-74 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-74-jsonld.html").to lint_cleanly}
  specify("examples.txt[1865] - eg-0018 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0018-microdata.html").to lint_cleanly}
  specify("examples.txt[1883] - Table-75 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Table-75-rdfa.html").to lint_cleanly}
  specify("examples.txt[1901] - Table-75 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Table-75-jsonld.html").to lint_cleanly}
  specify("examples.txt[1921] - eg-0019 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0019-microdata.html").to lint_cleanly}
  specify("examples.txt[1932] - PostalAddress-76 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-76-rdfa.html").to lint_cleanly}
  specify("examples.txt[1943] - PostalAddress-76 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-76-jsonld.html").to lint_cleanly}
  specify("examples.txt[1970] - eg-0020 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0020-microdata.html").to lint_cleanly}
  specify("examples.txt[1981] - CreativeWork-ContentRating-77 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-ContentRating-77-rdfa.html").to lint_cleanly}
  specify("examples.txt[1992] - CreativeWork-ContentRating-77 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-ContentRating-77-jsonld.html").to lint_cleanly}
  specify("examples.txt[2018] - eg-0021 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0021-microdata.html").to lint_cleanly}
  specify("examples.txt[2035] - ImageObject-78 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-78-rdfa.html").to lint_cleanly}
  specify("examples.txt[2051] - ImageObject-78 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ImageObject-78-jsonld.html").to lint_cleanly}
  specify("examples.txt[2078] - eg-0022 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0022-microdata.html").to lint_cleanly}
  specify("examples.txt[2125] - MusicPlaylist-79 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicPlaylist-79-rdfa.html").to lint_cleanly}
  specify("examples.txt[2172] - MusicPlaylist-79 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicPlaylist-79-jsonld.html").to lint_cleanly}
  specify("examples.txt[2233] - eg-0023 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0023-microdata.html").to lint_cleanly}
  specify("examples.txt[2252] - InteractionCounter-Article-80 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-Article-80-rdfa.html").to lint_cleanly}
  specify("examples.txt[2272] - InteractionCounter-Article-80 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-Article-80-jsonld.html").to lint_cleanly}
  specify("examples.txt[2310] - eg-0024 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0024-microdata.html").to lint_cleanly}
  specify("examples.txt[2320] - CivicStructure-Place-81 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CivicStructure-Place-81-rdfa.html").to lint_cleanly}
  specify("examples.txt[2330] - CivicStructure-Place-81 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CivicStructure-Place-81-jsonld.html").to lint_cleanly}
  specify("examples.txt[2356] - eg-0025 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0025-microdata.html").to lint_cleanly}
  specify("examples.txt[2374] - EducationalOrganization-82 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOrganization-82-rdfa.html").to lint_cleanly}
  specify("examples.txt[2392] - EducationalOrganization-82 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOrganization-82-jsonld.html").to lint_cleanly}
  specify("examples.txt[2431] - eg-0026 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0026-microdata.html").to lint_cleanly}
  specify("examples.txt[2461] - TVSeries-TVSeason-TVEpisode-83 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-83-rdfa.html").to lint_cleanly}
  specify("examples.txt[2491] - TVSeries-TVSeason-TVEpisode-83 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-83-jsonld.html").to lint_cleanly}
  specify("examples.txt[2545] - eg-0027 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0027-microdata.html").to lint_cleanly}
  specify("examples.txt[2572] - MusicAlbum-84 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-84-rdfa.html").to lint_cleanly}
  specify("examples.txt[2599] - MusicAlbum-84 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-84-jsonld.html").to lint_cleanly}
  specify("examples.txt[2682] - eg-0028 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0028-microdata.html").to lint_cleanly}
  specify("examples.txt[2747] - JobPosting-85 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-85-rdfa.html").to lint_cleanly}
  specify("examples.txt[2812] - JobPosting-85 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-85-jsonld.html").to lint_cleanly}
  specify("examples.txt[2855] - eg-0029 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0029-microdata.html").to lint_cleanly}
  specify("examples.txt[2867] - IndividualProduct-86 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IndividualProduct-86-rdfa.html").to lint_cleanly}
  specify("examples.txt[2879] - IndividualProduct-86 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IndividualProduct-86-jsonld.html").to lint_cleanly}
  specify("examples.txt[2902] - eg-0030 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0030-microdata.html").to lint_cleanly}
  specify("examples.txt[2917] - SomeProducts-87 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SomeProducts-87-rdfa.html").to lint_cleanly}
  specify("examples.txt[2932] - SomeProducts-87 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SomeProducts-87-jsonld.html").to lint_cleanly}
  specify("examples.txt[2955] - eg-0031 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0031-microdata.html").to lint_cleanly}
  specify("examples.txt[2978] - ProductModel-88 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProductModel-88-rdfa.html").to lint_cleanly}
  specify("examples.txt[3001] - ProductModel-88 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProductModel-88-jsonld.html").to lint_cleanly}
  specify("examples.txt[3021] - eg-0032 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0032-microdata.html").to lint_cleanly}
  specify("examples.txt[3025] - Action-89 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-89-rdfa.html").to lint_cleanly}
  specify("examples.txt[3029] - Action-89 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-89-jsonld.html").to lint_cleanly}
  specify("examples.txt[3065] - eg-0033 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0033-microdata.html").to lint_cleanly}
  specify("examples.txt[3069] - Action-90 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-90-rdfa.html").to lint_cleanly}
  specify("examples.txt[3073] - Action-90 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Action-90-jsonld.html").to lint_cleanly}
  specify("examples.txt[3101] - eg-0034 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0034-microdata.html").to lint_cleanly}
  specify("examples.txt[3105] - AchieveAction-91 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AchieveAction-91-rdfa.html").to lint_cleanly}
  specify("examples.txt[3109] - AchieveAction-91 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AchieveAction-91-jsonld.html").to lint_cleanly}
  specify("examples.txt[3133] - eg-0035 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0035-microdata.html").to lint_cleanly}
  specify("examples.txt[3137] - LoseAction-92 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoseAction-92-rdfa.html").to lint_cleanly}
  specify("examples.txt[3141] - LoseAction-92 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoseAction-92-jsonld.html").to lint_cleanly}
  specify("examples.txt[3169] - eg-0036 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0036-microdata.html").to lint_cleanly}
  specify("examples.txt[3173] - TieAction-93 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TieAction-93-rdfa.html").to lint_cleanly}
  specify("examples.txt[3177] - TieAction-93 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TieAction-93-jsonld.html").to lint_cleanly}
  specify("examples.txt[3205] - eg-0037 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0037-microdata.html").to lint_cleanly}
  specify("examples.txt[3209] - WinAction-94 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WinAction-94-rdfa.html").to lint_cleanly}
  specify("examples.txt[3213] - WinAction-94 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WinAction-94-jsonld.html").to lint_cleanly}
  specify("examples.txt[3237] - eg-0038 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0038-microdata.html").to lint_cleanly}
  specify("examples.txt[3241] - AssessAction-95 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssessAction-95-rdfa.html").to lint_cleanly}
  specify("examples.txt[3245] - AssessAction-95 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssessAction-95-jsonld.html").to lint_cleanly}
  specify("examples.txt[3269] - eg-0039 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0039-microdata.html").to lint_cleanly}
  specify("examples.txt[3273] - ChooseAction-96 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-96-rdfa.html").to lint_cleanly}
  specify("examples.txt[3277] - ChooseAction-96 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-96-jsonld.html").to lint_cleanly}
  specify("examples.txt[3311] - eg-0040 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0040-microdata.html").to lint_cleanly}
  specify("examples.txt[3315] - ChooseAction-97 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-97-rdfa.html").to lint_cleanly}
  specify("examples.txt[3319] - ChooseAction-97 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ChooseAction-97-jsonld.html").to lint_cleanly}
  specify("examples.txt[3344] - eg-0041 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0041-microdata.html").to lint_cleanly}
  specify("examples.txt[3348] - VoteAction-98 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VoteAction-98-rdfa.html").to lint_cleanly}
  specify("examples.txt[3352] - VoteAction-98 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VoteAction-98-jsonld.html").to lint_cleanly}
  specify("examples.txt[3376] - eg-0042 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0042-microdata.html").to lint_cleanly}
  specify("examples.txt[3380] - IgnoreAction-99 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-99-rdfa.html").to lint_cleanly}
  specify("examples.txt[3384] - IgnoreAction-99 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-99-jsonld.html").to lint_cleanly}
  specify("examples.txt[3408] - eg-0043 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0043-microdata.html").to lint_cleanly}
  specify("examples.txt[3412] - IgnoreAction-100 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-100-rdfa.html").to lint_cleanly}
  specify("examples.txt[3416] - IgnoreAction-100 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-100-jsonld.html").to lint_cleanly}
  specify("examples.txt[3444] - eg-0044 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0044-microdata.html").to lint_cleanly}
  specify("examples.txt[3448] - IgnoreAction-101 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-101-rdfa.html").to lint_cleanly}
  specify("examples.txt[3452] - IgnoreAction-101 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/IgnoreAction-101-jsonld.html").to lint_cleanly}
  specify("examples.txt[3483] - eg-0045 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0045-microdata.html").to lint_cleanly}
  specify("examples.txt[3487] - ReactAction-102 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReactAction-102-rdfa.html").to lint_cleanly}
  specify("examples.txt[3491] - ReactAction-102 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReactAction-102-jsonld.html").to lint_cleanly}
  specify("examples.txt[3515] - eg-0046 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0046-microdata.html").to lint_cleanly}
  specify("examples.txt[3519] - AgreeAction-103 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AgreeAction-103-rdfa.html").to lint_cleanly}
  specify("examples.txt[3523] - AgreeAction-103 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AgreeAction-103-jsonld.html").to lint_cleanly}
  specify("examples.txt[3551] - eg-0047 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0047-microdata.html").to lint_cleanly}
  specify("examples.txt[3555] - DisagreeAction-104 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DisagreeAction-104-rdfa.html").to lint_cleanly}
  specify("examples.txt[3559] - DisagreeAction-104 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DisagreeAction-104-jsonld.html").to lint_cleanly}
  specify("examples.txt[3591] - eg-0048 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0048-microdata.html").to lint_cleanly}
  specify("examples.txt[3595] - DislikeAction-105 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DislikeAction-105-rdfa.html").to lint_cleanly}
  specify("examples.txt[3599] - DislikeAction-105 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DislikeAction-105-jsonld.html").to lint_cleanly}
  specify("examples.txt[3627] - eg-0049 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0049-microdata.html").to lint_cleanly}
  specify("examples.txt[3631] - EndorseAction-106 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EndorseAction-106-rdfa.html").to lint_cleanly}
  specify("examples.txt[3635] - EndorseAction-106 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EndorseAction-106-jsonld.html").to lint_cleanly}
  specify("examples.txt[3659] - eg-0050 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0050-microdata.html").to lint_cleanly}
  specify("examples.txt[3663] - LikeAction-107 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LikeAction-107-rdfa.html").to lint_cleanly}
  specify("examples.txt[3667] - LikeAction-107 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LikeAction-107-jsonld.html").to lint_cleanly}
  specify("examples.txt[3695] - eg-0051 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0051-microdata.html").to lint_cleanly}
  specify("examples.txt[3699] - WantAction-108 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WantAction-108-rdfa.html").to lint_cleanly}
  specify("examples.txt[3703] - WantAction-108 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WantAction-108-jsonld.html").to lint_cleanly}
  specify("examples.txt[3731] - eg-0052 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0052-microdata.html").to lint_cleanly}
  specify("examples.txt[3735] - ReviewAction-109 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReviewAction-109-rdfa.html").to lint_cleanly}
  specify("examples.txt[3739] - ReviewAction-109 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReviewAction-109-jsonld.html").to lint_cleanly}
  specify("examples.txt[3771] - eg-0053 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0053-microdata.html").to lint_cleanly}
  specify("examples.txt[3775] - ConsumeAction-110 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConsumeAction-110-rdfa.html").to lint_cleanly}
  specify("examples.txt[3779] - ConsumeAction-110 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConsumeAction-110-jsonld.html").to lint_cleanly}
  specify("examples.txt[3803] - eg-0054 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0054-microdata.html").to lint_cleanly}
  specify("examples.txt[3807] - DrinkAction-111 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrinkAction-111-rdfa.html").to lint_cleanly}
  specify("examples.txt[3811] - DrinkAction-111 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrinkAction-111-jsonld.html").to lint_cleanly}
  specify("examples.txt[3835] - eg-0055 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0055-microdata.html").to lint_cleanly}
  specify("examples.txt[3839] - EatAction-112 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EatAction-112-rdfa.html").to lint_cleanly}
  specify("examples.txt[3843] - EatAction-112 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EatAction-112-jsonld.html").to lint_cleanly}
  specify("examples.txt[3867] - eg-0056 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0056-microdata.html").to lint_cleanly}
  specify("examples.txt[3871] - InstallAction-113 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InstallAction-113-rdfa.html").to lint_cleanly}
  specify("examples.txt[3875] - InstallAction-113 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InstallAction-113-jsonld.html").to lint_cleanly}
  specify("examples.txt[3899] - eg-0057 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0057-microdata.html").to lint_cleanly}
  specify("examples.txt[3903] - ListenAction-114 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-114-rdfa.html").to lint_cleanly}
  specify("examples.txt[3907] - ListenAction-114 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-114-jsonld.html").to lint_cleanly}
  specify("examples.txt[3931] - eg-0058 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0058-microdata.html").to lint_cleanly}
  specify("examples.txt[3935] - ListenAction-115 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-115-rdfa.html").to lint_cleanly}
  specify("examples.txt[3939] - ListenAction-115 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-115-jsonld.html").to lint_cleanly}
  specify("examples.txt[3963] - eg-0059 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0059-microdata.html").to lint_cleanly}
  specify("examples.txt[3967] - ListenAction-116 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-116-rdfa.html").to lint_cleanly}
  specify("examples.txt[3971] - ListenAction-116 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ListenAction-116-jsonld.html").to lint_cleanly}
  specify("examples.txt[3995] - eg-0060 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0060-microdata.html").to lint_cleanly}
  specify("examples.txt[3999] - ReadAction-117 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-117-rdfa.html").to lint_cleanly}
  specify("examples.txt[4003] - ReadAction-117 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-117-jsonld.html").to lint_cleanly}
  specify("examples.txt[4027] - eg-0061 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0061-microdata.html").to lint_cleanly}
  specify("examples.txt[4031] - ReadAction-118 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-118-rdfa.html").to lint_cleanly}
  specify("examples.txt[4035] - ReadAction-118 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-118-jsonld.html").to lint_cleanly}
  specify("examples.txt[4059] - eg-0062 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0062-microdata.html").to lint_cleanly}
  specify("examples.txt[4063] - ReadAction-119 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-119-rdfa.html").to lint_cleanly}
  specify("examples.txt[4067] - ReadAction-119 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-119-jsonld.html").to lint_cleanly}
  specify("examples.txt[4091] - eg-0063 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0063-microdata.html").to lint_cleanly}
  specify("examples.txt[4095] - ReadAction-120 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-120-rdfa.html").to lint_cleanly}
  specify("examples.txt[4099] - ReadAction-120 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReadAction-120-jsonld.html").to lint_cleanly}
  specify("examples.txt[4123] - eg-0064 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0064-microdata.html").to lint_cleanly}
  specify("examples.txt[4127] - UseAction-121 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UseAction-121-rdfa.html").to lint_cleanly}
  specify("examples.txt[4131] - UseAction-121 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UseAction-121-jsonld.html").to lint_cleanly}
  specify("examples.txt[4155] - eg-0065 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0065-microdata.html").to lint_cleanly}
  specify("examples.txt[4159] - WearAction-122 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WearAction-122-rdfa.html").to lint_cleanly}
  specify("examples.txt[4163] - WearAction-122 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WearAction-122-jsonld.html").to lint_cleanly}
  specify("examples.txt[4187] - eg-0066 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0066-microdata.html").to lint_cleanly}
  specify("examples.txt[4191] - ViewAction-123 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-123-rdfa.html").to lint_cleanly}
  specify("examples.txt[4195] - ViewAction-123 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-123-jsonld.html").to lint_cleanly}
  specify("examples.txt[4219] - eg-0067 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0067-microdata.html").to lint_cleanly}
  specify("examples.txt[4223] - ViewAction-124 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-124-rdfa.html").to lint_cleanly}
  specify("examples.txt[4227] - ViewAction-124 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-124-jsonld.html").to lint_cleanly}
  specify("examples.txt[4251] - eg-0068 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0068-microdata.html").to lint_cleanly}
  specify("examples.txt[4255] - ViewAction-125 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-125-rdfa.html").to lint_cleanly}
  specify("examples.txt[4259] - ViewAction-125 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ViewAction-125-jsonld.html").to lint_cleanly}
  specify("examples.txt[4283] - eg-0069 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0069-microdata.html").to lint_cleanly}
  specify("examples.txt[4287] - WatchAction-126 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-126-rdfa.html").to lint_cleanly}
  specify("examples.txt[4291] - WatchAction-126 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-126-jsonld.html").to lint_cleanly}
  specify("examples.txt[4315] - eg-0070 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0070-microdata.html").to lint_cleanly}
  specify("examples.txt[4319] - WatchAction-127 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-127-rdfa.html").to lint_cleanly}
  specify("examples.txt[4323] - WatchAction-127 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-127-jsonld.html").to lint_cleanly}
  specify("examples.txt[4347] - eg-0071 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0071-microdata.html").to lint_cleanly}
  specify("examples.txt[4351] - WatchAction-128 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-128-rdfa.html").to lint_cleanly}
  specify("examples.txt[4355] - WatchAction-128 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-128-jsonld.html").to lint_cleanly}
  specify("examples.txt[4379] - eg-0072 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0072-microdata.html").to lint_cleanly}
  specify("examples.txt[4383] - WatchAction-129 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-129-rdfa.html").to lint_cleanly}
  specify("examples.txt[4387] - WatchAction-129 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-129-jsonld.html").to lint_cleanly}
  specify("examples.txt[4415] - eg-0073 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0073-microdata.html").to lint_cleanly}
  specify("examples.txt[4419] - CreateAction-130 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreateAction-130-rdfa.html").to lint_cleanly}
  specify("examples.txt[4423] - CreateAction-130 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreateAction-130-jsonld.html").to lint_cleanly}
  specify("examples.txt[4447] - eg-0074 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0074-microdata.html").to lint_cleanly}
  specify("examples.txt[4451] - CookAction-131 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CookAction-131-rdfa.html").to lint_cleanly}
  specify("examples.txt[4455] - CookAction-131 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CookAction-131-jsonld.html").to lint_cleanly}
  specify("examples.txt[4479] - eg-0075 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0075-microdata.html").to lint_cleanly}
  specify("examples.txt[4483] - DrawAction-132 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrawAction-132-rdfa.html").to lint_cleanly}
  specify("examples.txt[4487] - DrawAction-132 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DrawAction-132-jsonld.html").to lint_cleanly}
  specify("examples.txt[4511] - eg-0076 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0076-microdata.html").to lint_cleanly}
  specify("examples.txt[4515] - FilmAction-133 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FilmAction-133-rdfa.html").to lint_cleanly}
  specify("examples.txt[4519] - FilmAction-133 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FilmAction-133-jsonld.html").to lint_cleanly}
  specify("examples.txt[4543] - eg-0077 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0077-microdata.html").to lint_cleanly}
  specify("examples.txt[4547] - PaintAction-134 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaintAction-134-rdfa.html").to lint_cleanly}
  specify("examples.txt[4551] - PaintAction-134 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaintAction-134-jsonld.html").to lint_cleanly}
  specify("examples.txt[4575] - eg-0078 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0078-microdata.html").to lint_cleanly}
  specify("examples.txt[4579] - PhotographAction-135 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PhotographAction-135-rdfa.html").to lint_cleanly}
  specify("examples.txt[4583] - PhotographAction-135 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PhotographAction-135-jsonld.html").to lint_cleanly}
  specify("examples.txt[4607] - eg-0079 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0079-microdata.html").to lint_cleanly}
  specify("examples.txt[4611] - WriteAction-136 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WriteAction-136-rdfa.html").to lint_cleanly}
  specify("examples.txt[4615] - WriteAction-136 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WriteAction-136-jsonld.html").to lint_cleanly}
  specify("examples.txt[4639] - eg-0080 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0080-microdata.html").to lint_cleanly}
  specify("examples.txt[4643] - FindAction-137 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FindAction-137-rdfa.html").to lint_cleanly}
  specify("examples.txt[4647] - FindAction-137 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FindAction-137-jsonld.html").to lint_cleanly}
  specify("examples.txt[4671] - eg-0081 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0081-microdata.html").to lint_cleanly}
  specify("examples.txt[4675] - CheckAction-138 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-138-rdfa.html").to lint_cleanly}
  specify("examples.txt[4679] - CheckAction-138 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-138-jsonld.html").to lint_cleanly}
  specify("examples.txt[4704] - eg-0082 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0082-microdata.html").to lint_cleanly}
  specify("examples.txt[4708] - CheckAction-139 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-139-rdfa.html").to lint_cleanly}
  specify("examples.txt[4712] - CheckAction-139 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckAction-139-jsonld.html").to lint_cleanly}
  specify("examples.txt[4736] - eg-0083 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0083-microdata.html").to lint_cleanly}
  specify("examples.txt[4740] - DiscoverAction-140 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscoverAction-140-rdfa.html").to lint_cleanly}
  specify("examples.txt[4744] - DiscoverAction-140 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscoverAction-140-jsonld.html").to lint_cleanly}
  specify("examples.txt[4768] - eg-0084 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0084-microdata.html").to lint_cleanly}
  specify("examples.txt[4772] - TrackAction-141 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrackAction-141-rdfa.html").to lint_cleanly}
  specify("examples.txt[4776] - TrackAction-141 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrackAction-141-jsonld.html").to lint_cleanly}
  specify("examples.txt[4804] - eg-0085 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0085-microdata.html").to lint_cleanly}
  specify("examples.txt[4808] - InteractAction-142 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-142-rdfa.html").to lint_cleanly}
  specify("examples.txt[4812] - InteractAction-142 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-142-jsonld.html").to lint_cleanly}
  specify("examples.txt[4836] - eg-0086 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0086-microdata.html").to lint_cleanly}
  specify("examples.txt[4840] - InteractAction-143 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-143-rdfa.html").to lint_cleanly}
  specify("examples.txt[4844] - InteractAction-143 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractAction-143-jsonld.html").to lint_cleanly}
  specify("examples.txt[4868] - eg-0087 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0087-microdata.html").to lint_cleanly}
  specify("examples.txt[4872] - BefriendAction-144 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BefriendAction-144-rdfa.html").to lint_cleanly}
  specify("examples.txt[4876] - BefriendAction-144 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BefriendAction-144-jsonld.html").to lint_cleanly}
  specify("examples.txt[4900] - eg-0088 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0088-microdata.html").to lint_cleanly}
  specify("examples.txt[4904] - CommunicateAction-145 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-145-rdfa.html").to lint_cleanly}
  specify("examples.txt[4908] - CommunicateAction-145 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-145-jsonld.html").to lint_cleanly}
  specify("examples.txt[4932] - eg-0089 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0089-microdata.html").to lint_cleanly}
  specify("examples.txt[4936] - CommunicateAction-146 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-146-rdfa.html").to lint_cleanly}
  specify("examples.txt[4940] - CommunicateAction-146 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommunicateAction-146-jsonld.html").to lint_cleanly}
  specify("examples.txt[4965] - eg-0090 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0090-microdata.html").to lint_cleanly}
  specify("examples.txt[4969] - AskAction-Question-147 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AskAction-Question-147-rdfa.html").to lint_cleanly}
  specify("examples.txt[4973] - AskAction-Question-147 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AskAction-Question-147-jsonld.html").to lint_cleanly}
  specify("examples.txt[5001] - eg-0091 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0091-microdata.html").to lint_cleanly}
  specify("examples.txt[5005] - CheckInAction-148 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-148-rdfa.html").to lint_cleanly}
  specify("examples.txt[5009] - CheckInAction-148 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-148-jsonld.html").to lint_cleanly}
  specify("examples.txt[5040] - eg-0092 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0092-microdata.html").to lint_cleanly}
  specify("examples.txt[5044] - CheckInAction-149 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-149-rdfa.html").to lint_cleanly}
  specify("examples.txt[5048] - CheckInAction-149 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-149-jsonld.html").to lint_cleanly}
  specify("examples.txt[5088] - eg-0093 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0093-microdata.html").to lint_cleanly}
  specify("examples.txt[5092] - CheckInAction-150 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-150-rdfa.html").to lint_cleanly}
  specify("examples.txt[5096] - CheckInAction-150 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckInAction-150-jsonld.html").to lint_cleanly}
  specify("examples.txt[5124] - eg-0094 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0094-microdata.html").to lint_cleanly}
  specify("examples.txt[5128] - CheckOutAction-151 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckOutAction-151-rdfa.html").to lint_cleanly}
  specify("examples.txt[5132] - CheckOutAction-151 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CheckOutAction-151-jsonld.html").to lint_cleanly}
  specify("examples.txt[5160] - eg-0095 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0095-microdata.html").to lint_cleanly}
  specify("examples.txt[5164] - CommentAction-152 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommentAction-152-rdfa.html").to lint_cleanly}
  specify("examples.txt[5168] - CommentAction-152 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CommentAction-152-jsonld.html").to lint_cleanly}
  specify("examples.txt[5196] - eg-0096 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0096-microdata.html").to lint_cleanly}
  specify("examples.txt[5200] - InformAction-153 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InformAction-153-rdfa.html").to lint_cleanly}
  specify("examples.txt[5204] - InformAction-153 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InformAction-153-jsonld.html").to lint_cleanly}
  specify("examples.txt[5232] - eg-0097 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0097-microdata.html").to lint_cleanly}
  specify("examples.txt[5236] - ConfirmAction-154 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConfirmAction-154-rdfa.html").to lint_cleanly}
  specify("examples.txt[5240] - ConfirmAction-154 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ConfirmAction-154-jsonld.html").to lint_cleanly}
  specify("examples.txt[5264] - eg-0098 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0098-microdata.html").to lint_cleanly}
  specify("examples.txt[5268] - RsvpAction-155 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RsvpAction-155-rdfa.html").to lint_cleanly}
  specify("examples.txt[5272] - RsvpAction-155 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RsvpAction-155-jsonld.html").to lint_cleanly}
  specify("examples.txt[5296] - eg-0099 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0099-microdata.html").to lint_cleanly}
  specify("examples.txt[5300] - InviteAction-156 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InviteAction-156-rdfa.html").to lint_cleanly}
  specify("examples.txt[5304] - InviteAction-156 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InviteAction-156-jsonld.html").to lint_cleanly}
  specify("examples.txt[5332] - eg-0100 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0100-microdata.html").to lint_cleanly}
  specify("examples.txt[5336] - ReplyAction-Question-Answer-157 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplyAction-Question-Answer-157-rdfa.html").to lint_cleanly}
  specify("examples.txt[5340] - ReplyAction-Question-Answer-157 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplyAction-Question-Answer-157-jsonld.html").to lint_cleanly}
  specify("examples.txt[5372] - eg-0101 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0101-microdata.html").to lint_cleanly}
  specify("examples.txt[5376] - ShareAction-158 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-158-rdfa.html").to lint_cleanly}
  specify("examples.txt[5380] - ShareAction-158 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-158-jsonld.html").to lint_cleanly}
  specify("examples.txt[5408] - eg-0102 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0102-microdata.html").to lint_cleanly}
  specify("examples.txt[5412] - ShareAction-159 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-159-rdfa.html").to lint_cleanly}
  specify("examples.txt[5416] - ShareAction-159 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ShareAction-159-jsonld.html").to lint_cleanly}
  specify("examples.txt[5445] - eg-0103 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0103-microdata.html").to lint_cleanly}
  specify("examples.txt[5449] - FollowAction-160 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FollowAction-160-rdfa.html").to lint_cleanly}
  specify("examples.txt[5453] - FollowAction-160 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FollowAction-160-jsonld.html").to lint_cleanly}
  specify("examples.txt[5481] - eg-0104 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0104-microdata.html").to lint_cleanly}
  specify("examples.txt[5485] - JoinAction-161 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-161-rdfa.html").to lint_cleanly}
  specify("examples.txt[5489] - JoinAction-161 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-161-jsonld.html").to lint_cleanly}
  specify("examples.txt[5513] - eg-0105 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0105-microdata.html").to lint_cleanly}
  specify("examples.txt[5517] - JoinAction-162 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-162-rdfa.html").to lint_cleanly}
  specify("examples.txt[5521] - JoinAction-162 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-162-jsonld.html").to lint_cleanly}
  specify("examples.txt[5545] - eg-0106 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0106-microdata.html").to lint_cleanly}
  specify("examples.txt[5549] - JoinAction-163 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-163-rdfa.html").to lint_cleanly}
  specify("examples.txt[5553] - JoinAction-163 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-163-jsonld.html").to lint_cleanly}
  specify("examples.txt[5577] - eg-0107 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0107-microdata.html").to lint_cleanly}
  specify("examples.txt[5581] - JoinAction-164 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-164-rdfa.html").to lint_cleanly}
  specify("examples.txt[5585] - JoinAction-164 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JoinAction-164-jsonld.html").to lint_cleanly}
  specify("examples.txt[5609] - eg-0108 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0108-microdata.html").to lint_cleanly}
  specify("examples.txt[5613] - LeaveAction-165 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LeaveAction-165-rdfa.html").to lint_cleanly}
  specify("examples.txt[5617] - LeaveAction-165 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LeaveAction-165-jsonld.html").to lint_cleanly}
  specify("examples.txt[5641] - eg-0109 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0109-microdata.html").to lint_cleanly}
  specify("examples.txt[5645] - MarryAction-166 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MarryAction-166-rdfa.html").to lint_cleanly}
  specify("examples.txt[5649] - MarryAction-166 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MarryAction-166-jsonld.html").to lint_cleanly}
  specify("examples.txt[5673] - eg-0110 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0110-microdata.html").to lint_cleanly}
  specify("examples.txt[5677] - RegisterAction-167 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-167-rdfa.html").to lint_cleanly}
  specify("examples.txt[5681] - RegisterAction-167 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-167-jsonld.html").to lint_cleanly}
  specify("examples.txt[5705] - eg-0111 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0111-microdata.html").to lint_cleanly}
  specify("examples.txt[5709] - RegisterAction-168 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-168-rdfa.html").to lint_cleanly}
  specify("examples.txt[5713] - RegisterAction-168 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-168-jsonld.html").to lint_cleanly}
  specify("examples.txt[5737] - eg-0112 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0112-microdata.html").to lint_cleanly}
  specify("examples.txt[5741] - RegisterAction-169 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-169-rdfa.html").to lint_cleanly}
  specify("examples.txt[5745] - RegisterAction-169 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RegisterAction-169-jsonld.html").to lint_cleanly}
  specify("examples.txt[5769] - eg-0113 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0113-microdata.html").to lint_cleanly}
  specify("examples.txt[5773] - SubscribeAction-170 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SubscribeAction-170-rdfa.html").to lint_cleanly}
  specify("examples.txt[5777] - SubscribeAction-170 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SubscribeAction-170-jsonld.html").to lint_cleanly}
  specify("examples.txt[5801] - eg-0114 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0114-microdata.html").to lint_cleanly}
  specify("examples.txt[5805] - UnRegisterAction-171 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UnRegisterAction-171-rdfa.html").to lint_cleanly}
  specify("examples.txt[5809] - UnRegisterAction-171 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UnRegisterAction-171-jsonld.html").to lint_cleanly}
  specify("examples.txt[5833] - eg-0115 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0115-microdata.html").to lint_cleanly}
  specify("examples.txt[5837] - MoveAction-172 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MoveAction-172-rdfa.html").to lint_cleanly}
  specify("examples.txt[5841] - MoveAction-172 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MoveAction-172-jsonld.html").to lint_cleanly}
  specify("examples.txt[5873] - eg-0116 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0116-microdata.html").to lint_cleanly}
  specify("examples.txt[5877] - ArriveAction-173 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArriveAction-173-rdfa.html").to lint_cleanly}
  specify("examples.txt[5881] - ArriveAction-173 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArriveAction-173-jsonld.html").to lint_cleanly}
  specify("examples.txt[5905] - eg-0117 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0117-microdata.html").to lint_cleanly}
  specify("examples.txt[5909] - DepartAction-174 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepartAction-174-rdfa.html").to lint_cleanly}
  specify("examples.txt[5913] - DepartAction-174 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepartAction-174-jsonld.html").to lint_cleanly}
  specify("examples.txt[5937] - eg-0118 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0118-microdata.html").to lint_cleanly}
  specify("examples.txt[5941] - TravelAction-175 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-175-rdfa.html").to lint_cleanly}
  specify("examples.txt[5945] - TravelAction-175 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-175-jsonld.html").to lint_cleanly}
  specify("examples.txt[5969] - eg-0119 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0119-microdata.html").to lint_cleanly}
  specify("examples.txt[5973] - TravelAction-176 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-176-rdfa.html").to lint_cleanly}
  specify("examples.txt[5977] - TravelAction-176 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TravelAction-176-jsonld.html").to lint_cleanly}
  specify("examples.txt[6009] - eg-0120 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0120-microdata.html").to lint_cleanly}
  specify("examples.txt[6013] - OrganizeAction-177 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-177-rdfa.html").to lint_cleanly}
  specify("examples.txt[6017] - OrganizeAction-177 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-177-jsonld.html").to lint_cleanly}
  specify("examples.txt[6041] - eg-0121 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0121-microdata.html").to lint_cleanly}
  specify("examples.txt[6045] - OrganizeAction-178 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-178-rdfa.html").to lint_cleanly}
  specify("examples.txt[6049] - OrganizeAction-178 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrganizeAction-178-jsonld.html").to lint_cleanly}
  specify("examples.txt[6073] - eg-0122 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0122-microdata.html").to lint_cleanly}
  specify("examples.txt[6077] - AllocateAction-179 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AllocateAction-179-rdfa.html").to lint_cleanly}
  specify("examples.txt[6081] - AllocateAction-179 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AllocateAction-179-jsonld.html").to lint_cleanly}
  specify("examples.txt[6109] - eg-0123 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0123-microdata.html").to lint_cleanly}
  specify("examples.txt[6113] - AcceptAction-180 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AcceptAction-180-rdfa.html").to lint_cleanly}
  specify("examples.txt[6117] - AcceptAction-180 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AcceptAction-180-jsonld.html").to lint_cleanly}
  specify("examples.txt[6145] - eg-0124 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0124-microdata.html").to lint_cleanly}
  specify("examples.txt[6149] - AssignAction-181 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssignAction-181-rdfa.html").to lint_cleanly}
  specify("examples.txt[6153] - AssignAction-181 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AssignAction-181-jsonld.html").to lint_cleanly}
  specify("examples.txt[6185] - eg-0125 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0125-microdata.html").to lint_cleanly}
  specify("examples.txt[6189] - AuthorizeAction-182 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AuthorizeAction-182-rdfa.html").to lint_cleanly}
  specify("examples.txt[6193] - AuthorizeAction-182 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AuthorizeAction-182-jsonld.html").to lint_cleanly}
  specify("examples.txt[6225] - eg-0126 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0126-microdata.html").to lint_cleanly}
  specify("examples.txt[6229] - RejectAction-183 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RejectAction-183-rdfa.html").to lint_cleanly}
  specify("examples.txt[6233] - RejectAction-183 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RejectAction-183-jsonld.html").to lint_cleanly}
  specify("examples.txt[6261] - eg-0127 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0127-microdata.html").to lint_cleanly}
  specify("examples.txt[6265] - ApplyAction-184 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ApplyAction-184-rdfa.html").to lint_cleanly}
  specify("examples.txt[6269] - ApplyAction-184 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ApplyAction-184-jsonld.html").to lint_cleanly}
  specify("examples.txt[6293] - eg-0128 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0128-microdata.html").to lint_cleanly}
  specify("examples.txt[6297] - BookmarkAction-185 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookmarkAction-185-rdfa.html").to lint_cleanly}
  specify("examples.txt[6301] - BookmarkAction-185 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookmarkAction-185-jsonld.html").to lint_cleanly}
  specify("examples.txt[6330] - eg-0129 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0129-microdata.html").to lint_cleanly}
  specify("examples.txt[6334] - PlanAction-186 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-186-rdfa.html").to lint_cleanly}
  specify("examples.txt[6338] - PlanAction-186 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-186-jsonld.html").to lint_cleanly}
  specify("examples.txt[6366] - eg-0130 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0130-microdata.html").to lint_cleanly}
  specify("examples.txt[6370] - PlanAction-187 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-187-rdfa.html").to lint_cleanly}
  specify("examples.txt[6374] - PlanAction-187 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlanAction-187-jsonld.html").to lint_cleanly}
  specify("examples.txt[6402] - eg-0131 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0131-microdata.html").to lint_cleanly}
  specify("examples.txt[6406] - CancelAction-188 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CancelAction-188-rdfa.html").to lint_cleanly}
  specify("examples.txt[6410] - CancelAction-188 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CancelAction-188-jsonld.html").to lint_cleanly}
  specify("examples.txt[6438] - eg-0132 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0132-microdata.html").to lint_cleanly}
  specify("examples.txt[6442] - ReserveAction-189 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-189-rdfa.html").to lint_cleanly}
  specify("examples.txt[6446] - ReserveAction-189 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-189-jsonld.html").to lint_cleanly}
  specify("examples.txt[6471] - eg-0133 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0133-microdata.html").to lint_cleanly}
  specify("examples.txt[6475] - ScheduleAction-190 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScheduleAction-190-rdfa.html").to lint_cleanly}
  specify("examples.txt[6479] - ScheduleAction-190 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScheduleAction-190-jsonld.html").to lint_cleanly}
  specify("examples.txt[6504] - eg-0134 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0134-microdata.html").to lint_cleanly}
  specify("examples.txt[6508] - PlayAction-191 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlayAction-191-rdfa.html").to lint_cleanly}
  specify("examples.txt[6512] - PlayAction-191 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PlayAction-191-jsonld.html").to lint_cleanly}
  specify("examples.txt[6540] - eg-0135 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0135-microdata.html").to lint_cleanly}
  specify("examples.txt[6544] - ExerciseAction-192 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-192-rdfa.html").to lint_cleanly}
  specify("examples.txt[6548] - ExerciseAction-192 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-192-jsonld.html").to lint_cleanly}
  specify("examples.txt[6574] - eg-0136 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0136-microdata.html").to lint_cleanly}
  specify("examples.txt[6578] - ExerciseAction-193 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-193-rdfa.html").to lint_cleanly}
  specify("examples.txt[6582] - ExerciseAction-193 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExerciseAction-193-jsonld.html").to lint_cleanly}
  specify("examples.txt[6607] - eg-0137 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0137-microdata.html").to lint_cleanly}
  specify("examples.txt[6611] - PerformAction-194 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PerformAction-194-rdfa.html").to lint_cleanly}
  specify("examples.txt[6615] - PerformAction-194 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PerformAction-194-jsonld.html").to lint_cleanly}
  specify("examples.txt[6647] - eg-0138 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0138-microdata.html").to lint_cleanly}
  specify("examples.txt[6651] - SearchAction-195 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-195-rdfa.html").to lint_cleanly}
  specify("examples.txt[6655] - SearchAction-195 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-195-jsonld.html").to lint_cleanly}
  specify("examples.txt[6676] - eg-0139 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0139-microdata.html").to lint_cleanly}
  specify("examples.txt[6680] - SearchAction-196 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-196-rdfa.html").to lint_cleanly}
  specify("examples.txt[6684] - SearchAction-196 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-196-jsonld.html").to lint_cleanly}
  specify("examples.txt[6705] - eg-0140 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0140-microdata.html").to lint_cleanly}
  specify("examples.txt[6709] - TradeAction-197 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TradeAction-197-rdfa.html").to lint_cleanly}
  specify("examples.txt[6713] - TradeAction-197 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TradeAction-197-jsonld.html").to lint_cleanly}
  specify("examples.txt[6739] - eg-0141 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0141-microdata.html").to lint_cleanly}
  specify("examples.txt[6743] - BuyAction-198 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BuyAction-198-rdfa.html").to lint_cleanly}
  specify("examples.txt[6747] - BuyAction-198 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BuyAction-198-jsonld.html").to lint_cleanly}
  specify("examples.txt[6775] - eg-0142 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0142-microdata.html").to lint_cleanly}
  specify("examples.txt[6779] - DonateAction-199 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DonateAction-199-rdfa.html").to lint_cleanly}
  specify("examples.txt[6783] - DonateAction-199 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DonateAction-199-jsonld.html").to lint_cleanly}
  specify("examples.txt[6809] - eg-0143 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0143-microdata.html").to lint_cleanly}
  specify("examples.txt[6813] - OrderAction-200 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrderAction-200-rdfa.html").to lint_cleanly}
  specify("examples.txt[6817] - OrderAction-200 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OrderAction-200-jsonld.html").to lint_cleanly}
  specify("examples.txt[6845] - eg-0144 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0144-microdata.html").to lint_cleanly}
  specify("examples.txt[6849] - PayAction-201 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PayAction-201-rdfa.html").to lint_cleanly}
  specify("examples.txt[6853] - PayAction-201 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PayAction-201-jsonld.html").to lint_cleanly}
  specify("examples.txt[6879] - eg-0145 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0145-microdata.html").to lint_cleanly}
  specify("examples.txt[6883] - QuoteAction-202 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/QuoteAction-202-rdfa.html").to lint_cleanly}
  specify("examples.txt[6887] - QuoteAction-202 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/QuoteAction-202-jsonld.html").to lint_cleanly}
  specify("examples.txt[6913] - eg-0146 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0146-microdata.html").to lint_cleanly}
  specify("examples.txt[6917] - RentAction-203 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentAction-203-rdfa.html").to lint_cleanly}
  specify("examples.txt[6921] - RentAction-203 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentAction-203-jsonld.html").to lint_cleanly}
  specify("examples.txt[6949] - eg-0147 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0147-microdata.html").to lint_cleanly}
  specify("examples.txt[6953] - SellAction-204 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SellAction-204-rdfa.html").to lint_cleanly}
  specify("examples.txt[6957] - SellAction-204 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SellAction-204-jsonld.html").to lint_cleanly}
  specify("examples.txt[6986] - eg-0148 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0148-microdata.html").to lint_cleanly}
  specify("examples.txt[6990] - TipAction-205 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TipAction-205-rdfa.html").to lint_cleanly}
  specify("examples.txt[6994] - TipAction-205 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TipAction-205-jsonld.html").to lint_cleanly}
  specify("examples.txt[7023] - eg-0149 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0149-microdata.html").to lint_cleanly}
  specify("examples.txt[7027] - TransferAction-206 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TransferAction-206-rdfa.html").to lint_cleanly}
  specify("examples.txt[7031] - TransferAction-206 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TransferAction-206-jsonld.html").to lint_cleanly}
  specify("examples.txt[7063] - eg-0150 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0150-microdata.html").to lint_cleanly}
  specify("examples.txt[7067] - BorrowAction-207 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BorrowAction-207-rdfa.html").to lint_cleanly}
  specify("examples.txt[7071] - BorrowAction-207 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BorrowAction-207-jsonld.html").to lint_cleanly}
  specify("examples.txt[7099] - eg-0151 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0151-microdata.html").to lint_cleanly}
  specify("examples.txt[7103] - DownloadAction-208 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DownloadAction-208-rdfa.html").to lint_cleanly}
  specify("examples.txt[7107] - DownloadAction-208 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DownloadAction-208-jsonld.html").to lint_cleanly}
  specify("examples.txt[7131] - eg-0152 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0152-microdata.html").to lint_cleanly}
  specify("examples.txt[7135] - GiveAction-209 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-209-rdfa.html").to lint_cleanly}
  specify("examples.txt[7139] - GiveAction-209 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-209-jsonld.html").to lint_cleanly}
  specify("examples.txt[7167] - eg-0153 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0153-microdata.html").to lint_cleanly}
  specify("examples.txt[7171] - LendAction-210 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LendAction-210-rdfa.html").to lint_cleanly}
  specify("examples.txt[7175] - LendAction-210 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LendAction-210-jsonld.html").to lint_cleanly}
  specify("examples.txt[7204] - eg-0154 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0154-microdata.html").to lint_cleanly}
  specify("examples.txt[7208] - ReceiveAction-211 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReceiveAction-211-rdfa.html").to lint_cleanly}
  specify("examples.txt[7212] - ReceiveAction-211 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReceiveAction-211-jsonld.html").to lint_cleanly}
  specify("examples.txt[7252] - eg-0155 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0155-microdata.html").to lint_cleanly}
  specify("examples.txt[7256] - ReturnAction-212 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReturnAction-212-rdfa.html").to lint_cleanly}
  specify("examples.txt[7260] - ReturnAction-212 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReturnAction-212-jsonld.html").to lint_cleanly}
  specify("examples.txt[7288] - eg-0156 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0156-microdata.html").to lint_cleanly}
  specify("examples.txt[7292] - SendAction-213 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SendAction-213-rdfa.html").to lint_cleanly}
  specify("examples.txt[7296] - SendAction-213 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SendAction-213-jsonld.html").to lint_cleanly}
  specify("examples.txt[7336] - eg-0157 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0157-microdata.html").to lint_cleanly}
  specify("examples.txt[7340] - GiveAction-214 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-214-rdfa.html").to lint_cleanly}
  specify("examples.txt[7344] - GiveAction-214 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GiveAction-214-jsonld.html").to lint_cleanly}
  specify("examples.txt[7372] - eg-0158 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0158-microdata.html").to lint_cleanly}
  specify("examples.txt[7376] - UpdateAction-215 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UpdateAction-215-rdfa.html").to lint_cleanly}
  specify("examples.txt[7380] - UpdateAction-215 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/UpdateAction-215-jsonld.html").to lint_cleanly}
  specify("examples.txt[7405] - eg-0159 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0159-microdata.html").to lint_cleanly}
  specify("examples.txt[7409] - AddAction-216 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-216-rdfa.html").to lint_cleanly}
  specify("examples.txt[7413] - AddAction-216 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-216-jsonld.html").to lint_cleanly}
  specify("examples.txt[7442] - eg-0160 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0160-microdata.html").to lint_cleanly}
  specify("examples.txt[7446] - AddAction-217 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-217-rdfa.html").to lint_cleanly}
  specify("examples.txt[7450] - AddAction-217 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AddAction-217-jsonld.html").to lint_cleanly}
  specify("examples.txt[7479] - eg-0161 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0161-microdata.html").to lint_cleanly}
  specify("examples.txt[7483] - InsertAction-218 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InsertAction-218-rdfa.html").to lint_cleanly}
  specify("examples.txt[7487] - InsertAction-218 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InsertAction-218-jsonld.html").to lint_cleanly}
  specify("examples.txt[7516] - eg-0162 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0162-microdata.html").to lint_cleanly}
  specify("examples.txt[7520] - AppendAction-219 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AppendAction-219-rdfa.html").to lint_cleanly}
  specify("examples.txt[7524] - AppendAction-219 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/AppendAction-219-jsonld.html").to lint_cleanly}
  specify("examples.txt[7553] - eg-0163 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0163-microdata.html").to lint_cleanly}
  specify("examples.txt[7557] - PrependAction-220 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PrependAction-220-rdfa.html").to lint_cleanly}
  specify("examples.txt[7561] - PrependAction-220 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PrependAction-220-jsonld.html").to lint_cleanly}
  specify("examples.txt[7590] - eg-0164 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0164-microdata.html").to lint_cleanly}
  specify("examples.txt[7594] - DeleteAction-221 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DeleteAction-221-rdfa.html").to lint_cleanly}
  specify("examples.txt[7598] - DeleteAction-221 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DeleteAction-221-jsonld.html").to lint_cleanly}
  specify("examples.txt[7627] - eg-0165 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0165-microdata.html").to lint_cleanly}
  specify("examples.txt[7631] - ReplaceAction-222 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplaceAction-222-rdfa.html").to lint_cleanly}
  specify("examples.txt[7635] - ReplaceAction-222 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReplaceAction-222-jsonld.html").to lint_cleanly}
  specify("examples.txt[7675] - eg-0166 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0166-microdata.html").to lint_cleanly}
  specify("examples.txt[7707] - TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223-rdfa.html").to lint_cleanly}
  specify("examples.txt[7739] - TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TVSeries-TVSeason-TVEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-223-jsonld.html").to lint_cleanly}
  specify("examples.txt[7787] - eg-0167 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0167-microdata.html").to lint_cleanly}
  specify("examples.txt[7811] - RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224-rdfa.html").to lint_cleanly}
  specify("examples.txt[7835] - RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioSeries-RadioSeason-RadioEpisode-OnDemandEvent-BroadcastEvent-BroadcastService-224-jsonld.html").to lint_cleanly}
  specify("examples.txt[7873] - eg-0168 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0168-microdata.html").to lint_cleanly}
  specify("examples.txt[7889] - GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225-rdfa.html").to lint_cleanly}
  specify("examples.txt[7905] - GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentPermit-GovernmentOrganization-GovernmentService-AdministrativeArea-225-jsonld.html").to lint_cleanly}
  specify("examples.txt[7937] - eg-0169 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0169-microdata.html").to lint_cleanly}
  specify("examples.txt[7941] - GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226-rdfa.html").to lint_cleanly}
  specify("examples.txt[7945] - GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GovernmentService-GovernmentOrganization-AdministrativeArea-CivicAudience-ContactPoint-Language-Hospital-226-jsonld.html").to lint_cleanly}
  specify("examples.txt[8012] - eg-0170 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0170-microdata.html").to lint_cleanly}
  specify("examples.txt[8035] - Event-Place-PostalAddress-Offer-227 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-227-rdfa.html").to lint_cleanly}
  specify("examples.txt[8063] - Event-Place-PostalAddress-Offer-227 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-227-jsonld.html").to lint_cleanly}
  specify("examples.txt[8116] - eg-0171 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0171-microdata.html").to lint_cleanly}
  specify("examples.txt[8141] - Event-Place-PostalAddress-Offer-EventCancelled-228 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-EventCancelled-228-rdfa.html").to lint_cleanly}
  specify("examples.txt[8165] - Event-Place-PostalAddress-Offer-EventCancelled-228 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-EventCancelled-228-jsonld.html").to lint_cleanly}
  specify("examples.txt[8216] - eg-0172 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0172-microdata.html").to lint_cleanly}
  specify("examples.txt[8242] - Event-Place-PostalAddress-Offer-229 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-229-rdfa.html").to lint_cleanly}
  specify("examples.txt[8269] - Event-Place-PostalAddress-Offer-229 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-229-jsonld.html").to lint_cleanly}
  specify("examples.txt[8317] - eg-0173 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0173-microdata.html").to lint_cleanly}
  specify("examples.txt[8341] - Event-Place-PostalAddress-Offer-SoldOut-230 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-SoldOut-230-rdfa.html").to lint_cleanly}
  specify("examples.txt[8370] - Event-Place-PostalAddress-Offer-SoldOut-230 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-Offer-SoldOut-230-jsonld.html").to lint_cleanly}
  specify("examples.txt[8405] - eg-0174 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0174-microdata.html").to lint_cleanly}
  specify("examples.txt[8409] - Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231-rdfa.html").to lint_cleanly}
  specify("examples.txt[8413] - Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Place-PostalAddress-MusicGroup-Offer-LimitedAvailability-231-jsonld.html").to lint_cleanly}
  specify("examples.txt[8501] - eg-0175 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0175-microdata.html").to lint_cleanly}
  specify("examples.txt[8575] - Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232-rdfa.html").to lint_cleanly}
  specify("examples.txt[8649] - Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Book-CreativeWork-accessibilityFeature-accessibilityHazard-accessibilityControl-accessibilityAPI-232-jsonld.html").to lint_cleanly}
  specify("examples.txt[8704] - eg-0176 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0176-microdata.html").to lint_cleanly}
  specify("examples.txt[8716] - accessibilityFeature-accessibilityHazard-encodingFormat-233 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessibilityFeature-accessibilityHazard-encodingFormat-233-rdfa.html").to lint_cleanly}
  specify("examples.txt[8728] - accessibilityFeature-accessibilityHazard-encodingFormat-233 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessibilityFeature-accessibilityHazard-encodingFormat-233-jsonld.html").to lint_cleanly}
  specify("examples.txt[8738] - eg-0177 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0177-microdata.html").to lint_cleanly}
  specify("examples.txt[8759] - encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234-rdfa.html").to lint_cleanly}
  specify("examples.txt[8780] - encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/encodingFormat-accessibilityHazard-accessibilityFeature-accessibilityControl-accessibilityAPI-234-jsonld.html").to lint_cleanly}
  specify("examples.txt[8818] - eg-0178 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0178-microdata.html").to lint_cleanly}
  specify("examples.txt[8822] - TrainReservation-TrainTrip-235 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainReservation-TrainTrip-235-rdfa.html").to lint_cleanly}
  specify("examples.txt[8826] - TrainReservation-TrainTrip-235 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainReservation-TrainTrip-235-jsonld.html").to lint_cleanly}
  specify("examples.txt[8872] - eg-0179 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0179-microdata.html").to lint_cleanly}
  specify("examples.txt[8876] - BusReservation-BusTrip-236 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusReservation-BusTrip-236-rdfa.html").to lint_cleanly}
  specify("examples.txt[8880] - BusReservation-BusTrip-236 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusReservation-BusTrip-236-jsonld.html").to lint_cleanly}
  specify("examples.txt[8931] - eg-0180 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0180-microdata.html").to lint_cleanly}
  specify("examples.txt[8935] - EventReservation-Ticket-Seat-237 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventReservation-Ticket-Seat-237-rdfa.html").to lint_cleanly}
  specify("examples.txt[8939] - EventReservation-Ticket-Seat-237 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventReservation-Ticket-Seat-237-jsonld.html").to lint_cleanly}
  specify("examples.txt[8997] - eg-0181 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0181-microdata.html").to lint_cleanly}
  specify("examples.txt[9001] - Flight-FlightReservation-238 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Flight-FlightReservation-238-rdfa.html").to lint_cleanly}
  specify("examples.txt[9005] - Flight-FlightReservation-238 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Flight-FlightReservation-238-jsonld.html").to lint_cleanly}
  specify("examples.txt[9064] - eg-0182 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0182-microdata.html").to lint_cleanly}
  specify("examples.txt[9068] - FoodEstablishmentReservation-239 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FoodEstablishmentReservation-239-rdfa.html").to lint_cleanly}
  specify("examples.txt[9072] - FoodEstablishmentReservation-239 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FoodEstablishmentReservation-239-jsonld.html").to lint_cleanly}
  specify("examples.txt[9115] - eg-0183 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0183-microdata.html").to lint_cleanly}
  specify("examples.txt[9119] - LodgingReservation-240 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LodgingReservation-240-rdfa.html").to lint_cleanly}
  specify("examples.txt[9123] - LodgingReservation-240 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LodgingReservation-240-jsonld.html").to lint_cleanly}
  specify("examples.txt[9173] - eg-0184 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0184-microdata.html").to lint_cleanly}
  specify("examples.txt[9177] - RentalCarReservation-241 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentalCarReservation-241-rdfa.html").to lint_cleanly}
  specify("examples.txt[9181] - RentalCarReservation-241 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RentalCarReservation-241-jsonld.html").to lint_cleanly}
  specify("examples.txt[9249] - eg-0185 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0185-microdata.html").to lint_cleanly}
  specify("examples.txt[9253] - TaxiReservation-242 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TaxiReservation-242-rdfa.html").to lint_cleanly}
  specify("examples.txt[9257] - TaxiReservation-242 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TaxiReservation-242-jsonld.html").to lint_cleanly}
  specify("examples.txt[9324] - eg-0186 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0186-microdata.html").to lint_cleanly}
  specify("examples.txt[9351] - Question-Answer-243 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Question-Answer-243-rdfa.html").to lint_cleanly}
  specify("examples.txt[9378] - Question-Answer-243 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Question-Answer-243-jsonld.html").to lint_cleanly}
  specify("examples.txt[9427] - eg-0187 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0187-microdata.html").to lint_cleanly}
  specify("examples.txt[9436] - WatchAction-Movie-244 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-Movie-244-rdfa.html").to lint_cleanly}
  specify("examples.txt[9445] - WatchAction-Movie-244 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WatchAction-Movie-244-jsonld.html").to lint_cleanly}
  specify("examples.txt[9469] - eg-0188 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0188-microdata.html").to lint_cleanly}
  specify("examples.txt[9473] - Restaurant-ViewAction-EntryPoint-SoftwareApplication-245 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-ViewAction-EntryPoint-SoftwareApplication-245-rdfa.html").to lint_cleanly}
  specify("examples.txt[9477] - Restaurant-ViewAction-EntryPoint-SoftwareApplication-245 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-ViewAction-EntryPoint-SoftwareApplication-245-jsonld.html").to lint_cleanly}
  specify("examples.txt[9574] - eg-0189 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0189-microdata.html").to lint_cleanly}
  specify("examples.txt[9640] - MusicEvent-Event-CreativeWork-MusicGroup-Person-246 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Event-CreativeWork-MusicGroup-Person-246-rdfa.html").to lint_cleanly}
  specify("examples.txt[9702] - MusicEvent-Event-CreativeWork-MusicGroup-Person-246 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Event-CreativeWork-MusicGroup-Person-246-jsonld.html").to lint_cleanly}
  specify("examples.txt[9762] - eg-0190 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0190-microdata.html").to lint_cleanly}
  specify("examples.txt[9785] - Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247-rdfa.html").to lint_cleanly}
  specify("examples.txt[9808] - Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-TheaterEvent-PerformingArtsTheater-CreativeWork-247-jsonld.html").to lint_cleanly}
  specify("examples.txt[9846] - eg-0191 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0191-microdata.html").to lint_cleanly}
  specify("examples.txt[9850] - SportsEvent-248 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsEvent-248-rdfa.html").to lint_cleanly}
  specify("examples.txt[9854] - SportsEvent-248 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsEvent-248-jsonld.html").to lint_cleanly}
  specify("examples.txt[9881] - eg-0192 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0192-microdata.html").to lint_cleanly}
  specify("examples.txt[9891] - Restaurant-249 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-249-rdfa.html").to lint_cleanly}
  specify("examples.txt[9901] - Restaurant-249 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Restaurant-249-jsonld.html").to lint_cleanly}
  specify("examples.txt[9936] - eg-0193 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0193-microdata.html").to lint_cleanly}
  specify("examples.txt[9956] - Store-OpeningHoursSpecification-250 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-OpeningHoursSpecification-250-rdfa.html").to lint_cleanly}
  specify("examples.txt[9976] - Store-OpeningHoursSpecification-250 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-OpeningHoursSpecification-250-jsonld.html").to lint_cleanly}
  specify("examples.txt[10016] - eg-0194 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0194-microdata.html").to lint_cleanly}
  specify("examples.txt[10026] - Pharmacy-openingHours-telephone-251 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Pharmacy-openingHours-telephone-251-rdfa.html").to lint_cleanly}
  specify("examples.txt[10036] - Pharmacy-openingHours-telephone-251 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Pharmacy-openingHours-telephone-251-jsonld.html").to lint_cleanly}
  specify("examples.txt[10073] - eg-0195 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0195-microdata.html").to lint_cleanly}
  specify("examples.txt[10093] - Store-Pharmacy-252 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-Pharmacy-252-rdfa.html").to lint_cleanly}
  specify("examples.txt[10113] - Store-Pharmacy-252 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-Pharmacy-252-jsonld.html").to lint_cleanly}
  specify("examples.txt[10168] - eg-0196 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0196-microdata.html").to lint_cleanly}
  specify("examples.txt[10198] - Store-DryCleaningOrLaundry-Corporation-Pharmacy-253 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-DryCleaningOrLaundry-Corporation-Pharmacy-253-rdfa.html").to lint_cleanly}
  specify("examples.txt[10227] - Store-DryCleaningOrLaundry-Corporation-Pharmacy-253 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-DryCleaningOrLaundry-Corporation-Pharmacy-253-jsonld.html").to lint_cleanly}
  specify("examples.txt[10291] - eg-0197 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0197-microdata.html").to lint_cleanly}
  specify("examples.txt[10316] - Store-PostalAddress-Pharmacy-254 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-PostalAddress-Pharmacy-254-rdfa.html").to lint_cleanly}
  specify("examples.txt[10341] - Store-PostalAddress-Pharmacy-254 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Store-PostalAddress-Pharmacy-254-jsonld.html").to lint_cleanly}
  specify("examples.txt[10403] - eg-0198 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0198-microdata.html").to lint_cleanly}
  specify("examples.txt[10433] - PostalAddress-Pharmacy-Store-255 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-Pharmacy-Store-255-rdfa.html").to lint_cleanly}
  specify("examples.txt[10463] - PostalAddress-Pharmacy-Store-255 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PostalAddress-Pharmacy-Store-255-jsonld.html").to lint_cleanly}
  specify("examples.txt[10506] - eg-0199 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0199-microdata.html").to lint_cleanly}
  specify("examples.txt[10510] - Organization-ContactPoint-256 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-ContactPoint-256-rdfa.html").to lint_cleanly}
  specify("examples.txt[10514] - Organization-ContactPoint-256 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-ContactPoint-256-jsonld.html").to lint_cleanly}
  specify("examples.txt[10534] - eg-0200 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0200-microdata.html").to lint_cleanly}
  specify("examples.txt[10538] - HearingImpairedSupported-TollFree-ContactPoint-Organization-257 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HearingImpairedSupported-TollFree-ContactPoint-Organization-257-rdfa.html").to lint_cleanly}
  specify("examples.txt[10542] - HearingImpairedSupported-TollFree-ContactPoint-Organization-257 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HearingImpairedSupported-TollFree-ContactPoint-Organization-257-jsonld.html").to lint_cleanly}
  specify("examples.txt[10586] - eg-0201 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0201-microdata.html").to lint_cleanly}
  specify("examples.txt[10590] - MusicEvent-Place-Offer-258 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-Offer-258-rdfa.html").to lint_cleanly}
  specify("examples.txt[10594] - MusicEvent-Place-Offer-258 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-Offer-258-jsonld.html").to lint_cleanly}
  specify("examples.txt[10636] - eg-0202 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0202-microdata.html").to lint_cleanly}
  specify("examples.txt[10640] - MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259-rdfa.html").to lint_cleanly}
  specify("examples.txt[10644] - MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicEvent-Place-PostalAddress-Offer-MusicGroup-EventRescheduled-259-jsonld.html").to lint_cleanly}
  specify("examples.txt[10706] - eg-0203 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0203-microdata.html").to lint_cleanly}
  specify("examples.txt[10720] - Role-OrganizationRole-260 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-260-rdfa.html").to lint_cleanly}
  specify("examples.txt[10732] - Role-OrganizationRole-260 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-260-jsonld.html").to lint_cleanly}
  specify("examples.txt[10760] - eg-0204 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0204-microdata.html").to lint_cleanly}
  specify("examples.txt[10774] - Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261-rdfa.html").to lint_cleanly}
  specify("examples.txt[10788] - Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-CollegeOrUniversity-EducationalOrganization-261-jsonld.html").to lint_cleanly}
  specify("examples.txt[10818] - eg-0205 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0205-microdata.html").to lint_cleanly}
  specify("examples.txt[10833] - Role-PerformanceRole-262 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-PerformanceRole-262-rdfa.html").to lint_cleanly}
  specify("examples.txt[10846] - Role-PerformanceRole-262 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-PerformanceRole-262-jsonld.html").to lint_cleanly}
  specify("examples.txt[10873] - eg-0206 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0206-microdata.html").to lint_cleanly}
  specify("examples.txt[10887] - Role-OrganizationRole-Person-SportsTeam-Organization-263 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-Person-SportsTeam-Organization-263-rdfa.html").to lint_cleanly}
  specify("examples.txt[10901] - Role-OrganizationRole-Person-SportsTeam-Organization-263 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Role-OrganizationRole-Person-SportsTeam-Organization-263-jsonld.html").to lint_cleanly}
  specify("examples.txt[10938] - eg-0207 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0207-microdata.html").to lint_cleanly}
  specify("examples.txt[10953] - WebPage-CollegeOrUniversity-264 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-CollegeOrUniversity-264-rdfa.html").to lint_cleanly}
  specify("examples.txt[10967] - WebPage-CollegeOrUniversity-264 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebPage-CollegeOrUniversity-264-jsonld.html").to lint_cleanly}
  specify("examples.txt[11004] - eg-0208 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0208-microdata.html").to lint_cleanly}
  specify("examples.txt[11019] - ItemList-Product-Offer-265 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-Product-Offer-265-rdfa.html").to lint_cleanly}
  specify("examples.txt[11036] - ItemList-Product-Offer-265 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-Product-Offer-265-jsonld.html").to lint_cleanly}
  specify("examples.txt[11075] - eg-0209 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0209-microdata.html").to lint_cleanly}
  specify("examples.txt[11139] - ItemList-CreativeWork-266 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-CreativeWork-266-rdfa.html").to lint_cleanly}
  specify("examples.txt[11205] - ItemList-CreativeWork-266 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-CreativeWork-266-jsonld.html").to lint_cleanly}
  specify("examples.txt[11303] - eg-0210 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0210-microdata.html").to lint_cleanly}
  specify("examples.txt[11338] - ItemList-267 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-267-rdfa.html").to lint_cleanly}
  specify("examples.txt[11372] - ItemList-267 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-267-jsonld.html").to lint_cleanly}
  specify("examples.txt[11428] - eg-0211 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0211-microdata.html").to lint_cleanly}
  specify("examples.txt[11455] - ItemList-MusicAlbum-268 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-MusicAlbum-268-rdfa.html").to lint_cleanly}
  specify("examples.txt[11483] - ItemList-MusicAlbum-268 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ItemList-MusicAlbum-268-jsonld.html").to lint_cleanly}
  specify("examples.txt[11533] - eg-0212 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0212-microdata.html").to lint_cleanly}
  specify("examples.txt[11545] - Person-disambiguatingDescription-269 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-disambiguatingDescription-269-rdfa.html").to lint_cleanly}
  specify("examples.txt[11557] - Person-disambiguatingDescription-269 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-disambiguatingDescription-269-jsonld.html").to lint_cleanly}
  specify("examples.txt[11581] - eg-0213 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0213-microdata.html").to lint_cleanly}
  specify("examples.txt[11585] - skills-270 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/skills-270-rdfa.html").to lint_cleanly}
  specify("examples.txt[11589] - skills-270 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/skills-270-jsonld.html").to lint_cleanly}

  # Examples from sdo-sports-examples.txt
  specify("sdo-sports-examples.txt[10] - eg-0430 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0430-microdata.html").to lint_cleanly}
  specify("sdo-sports-examples.txt[14] - SportsTeam-SportsOrganization-271 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsTeam-SportsOrganization-271-rdfa.html").to lint_cleanly}
  specify("sdo-sports-examples.txt[18] - SportsTeam-SportsOrganization-271 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SportsTeam-SportsOrganization-271-jsonld.html").to lint_cleanly}

  # Examples from sdo-howto-examples.txt
  specify("sdo-howto-examples.txt[90] - eg-0371 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0371-microdata.html").to lint_cleanly}
  specify("sdo-howto-examples.txt[221] - HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-272 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-272-rdfa.html").to lint_cleanly}
  specify("sdo-howto-examples.txt[352] - HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-272 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HowTo-estimatedCost-totalTime-tool-supply-steps-HowToSection-HowToStep-HowToDirection-HowToTip-afterMedia-beforeMedia-duringMedia-272-jsonld.html").to lint_cleanly}

  # Examples from sdo-identifier-examples.txt
  specify("sdo-identifier-examples.txt[13] - eg-0372 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0372-microdata.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[25] - identifier-273 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-273-rdfa.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[38] - identifier-273 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-273-jsonld.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[65] - eg-0373 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0373-microdata.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[76] - identifier-274 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-274-rdfa.html").to lint_cleanly}
  specify("sdo-identifier-examples.txt[88] - identifier-274 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/identifier-274-jsonld.html").to lint_cleanly}

  # Examples from sdo-service-examples.txt
  specify("sdo-service-examples.txt[7] - eg-0421 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0421-microdata.html").to lint_cleanly}
  specify("sdo-service-examples.txt[25] - Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-275 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-275-rdfa.html").to lint_cleanly}
  specify("sdo-service-examples.txt[43] - Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-275 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Service-TaxiService-GeoCircle-geoMidPoint-geoRadius-providerMobility-275-jsonld.html").to lint_cleanly}

  # Examples from sdo-automobile-examples.txt
  specify("sdo-automobile-examples.txt[22] - eg-0328 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0328-microdata.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[52] - Car-276 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car-276-rdfa.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[82] - Car-276 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car-276-jsonld.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[132] - eg-0329 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0329-microdata.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[162] - Car makesOffer-277 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car makesOffer-277-rdfa.html").to lint_cleanly}
  specify("sdo-automobile-examples.txt[192] - Car makesOffer-277 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Car makesOffer-277-jsonld.html").to lint_cleanly}

  # Examples from sdo-airport-examples.txt
  specify("sdo-airport-examples.txt[7] - eg-0326 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0326-microdata.html").to lint_cleanly}
  specify("sdo-airport-examples.txt[11] - Airport-278 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Airport-278-rdfa.html").to lint_cleanly}
  specify("sdo-airport-examples.txt[15] - Airport-278 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Airport-278-jsonld.html").to lint_cleanly}

  # Examples from issue-1004-examples.txt
  specify("issue-1004-examples.txt[7] - eg-0319 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0319-microdata.html").to lint_cleanly}
  specify("issue-1004-examples.txt[18] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-279 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-279-rdfa.html").to lint_cleanly}
  specify("issue-1004-examples.txt[29] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-279 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-279-jsonld.html").to lint_cleanly}
  specify("issue-1004-examples.txt[51] - eg-0320 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0320-microdata.html").to lint_cleanly}
  specify("issue-1004-examples.txt[62] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-280 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-280-rdfa.html").to lint_cleanly}
  specify("issue-1004-examples.txt[73] - broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-280 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/broadcastFrequency-BroadcastService-BroadcastFrequencySpecification-280-jsonld.html").to lint_cleanly}

  # Examples from sdo-train-station-examples.txt
  specify("sdo-train-station-examples.txt[7] - eg-0440 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0440-microdata.html").to lint_cleanly}
  specify("sdo-train-station-examples.txt[11] - TrainStation-281 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainStation-281-rdfa.html").to lint_cleanly}
  specify("sdo-train-station-examples.txt[15] - TrainStation-281 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TrainStation-281-jsonld.html").to lint_cleanly}

  # Examples from sdo-offer-shipping-details-examples.txt
  specify("sdo-offer-shipping-details-examples.txt[7] - eg-0392 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0392-microdata.html").to lint_cleanly}
  specify("sdo-offer-shipping-details-examples.txt[11] - OfferShippingDetails-deliveryTime-ShippingDeliveryTime-shippingRate-282 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OfferShippingDetails-deliveryTime-ShippingDeliveryTime-shippingRate-282-rdfa.html").to lint_cleanly}
  specify("sdo-offer-shipping-details-examples.txt[15] - OfferShippingDetails-deliveryTime-ShippingDeliveryTime-shippingRate-282 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/OfferShippingDetails-deliveryTime-ShippingDeliveryTime-shippingRate-282-jsonld.html").to lint_cleanly}

  # Examples from sdo-userinteraction-examples.txt
  specify("sdo-userinteraction-examples.txt[12] - eg-0446 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0446-microdata.html").to lint_cleanly}
  specify("sdo-userinteraction-examples.txt[68] - InteractionCounter-VideoObject-283 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-VideoObject-283-rdfa.html").to lint_cleanly}
  specify("sdo-userinteraction-examples.txt[124] - InteractionCounter-VideoObject-283 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InteractionCounter-VideoObject-283-jsonld.html").to lint_cleanly}

  # Examples from sdo-book-series-examples.txt
  specify("sdo-book-series-examples.txt[7] - eg-0330 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0330-microdata.html").to lint_cleanly}
  specify("sdo-book-series-examples.txt[11] - BookSeries-author-284 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookSeries-author-284-rdfa.html").to lint_cleanly}
  specify("sdo-book-series-examples.txt[15] - BookSeries-author-284 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BookSeries-author-284-jsonld.html").to lint_cleanly}

  # Examples from sdo-dentist-examples.txt
  specify("sdo-dentist-examples.txt[7] - eg-0347 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0347-microdata.html").to lint_cleanly}
  specify("sdo-dentist-examples.txt[11] - Dentist-285 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Dentist-285-rdfa.html").to lint_cleanly}
  specify("sdo-dentist-examples.txt[15] - Dentist-285 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Dentist-285-jsonld.html").to lint_cleanly}

  # Examples from sdo-visualartwork-examples.txt
  specify("sdo-visualartwork-examples.txt[41] - eg-0454 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0454-microdata.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[90] - VisualArtwork-Person-286 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-Person-286-rdfa.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[139] - VisualArtwork-Person-286 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-Person-286-jsonld.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[210] - eg-0455 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0455-microdata.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[253] - VisualArtwork-287 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-287-rdfa.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[296] - VisualArtwork-287 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-287-jsonld.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[357] - eg-0456 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0456-microdata.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[399] - VisualArtwork-288 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-288-rdfa.html").to lint_cleanly}
  specify("sdo-visualartwork-examples.txt[441] - VisualArtwork-288 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VisualArtwork-288-jsonld.html").to lint_cleanly}

  # Examples from sdo-police-station-examples.txt
  specify("sdo-police-station-examples.txt[7] - eg-0403 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0403-microdata.html").to lint_cleanly}
  specify("sdo-police-station-examples.txt[11] - PoliceStation-areaServed-289 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PoliceStation-areaServed-289-rdfa.html").to lint_cleanly}
  specify("sdo-police-station-examples.txt[15] - PoliceStation-areaServed-289 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PoliceStation-areaServed-289-jsonld.html").to lint_cleanly}

  # Examples from sdo-apartment-examples.txt
  specify("sdo-apartment-examples.txt[7] - eg-0327 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0327-microdata.html").to lint_cleanly}
  specify("sdo-apartment-examples.txt[11] - Apartment-Accommodation-occupancy-floorSize-290 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Apartment-Accommodation-occupancy-floorSize-290-rdfa.html").to lint_cleanly}
  specify("sdo-apartment-examples.txt[15] - Apartment-Accommodation-occupancy-floorSize-290 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Apartment-Accommodation-occupancy-floorSize-290-jsonld.html").to lint_cleanly}

  # Examples from sdo-screeningevent-examples.txt
  specify("sdo-screeningevent-examples.txt[21] - eg-0419 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0419-microdata.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[39] - ScreeningEvent-Movie-MovieTheater-291 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScreeningEvent-Movie-MovieTheater-291-rdfa.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[63] - ScreeningEvent-Movie-MovieTheater-291 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ScreeningEvent-Movie-MovieTheater-291-jsonld.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[92] - eg-0420 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0420-microdata.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[104] - Movie-countryOfOrigin-292 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-countryOfOrigin-292-rdfa.html").to lint_cleanly}
  specify("sdo-screeningevent-examples.txt[116] - Movie-countryOfOrigin-292 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Movie-countryOfOrigin-292-jsonld.html").to lint_cleanly}

  # Examples from sdo-website-examples.txt
  specify("sdo-website-examples.txt[7] - eg-0457 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0457-microdata.html").to lint_cleanly}
  specify("sdo-website-examples.txt[18] - SearchAction-WebSite-293 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-WebSite-293-rdfa.html").to lint_cleanly}
  specify("sdo-website-examples.txt[29] - SearchAction-WebSite-293 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SearchAction-WebSite-293-jsonld.html").to lint_cleanly}

  # Examples from sdo-creativework-examples.txt
  specify("sdo-creativework-examples.txt[9] - eg-0340 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0340-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[26] - Painting-contentLocation-locationCreated-294 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-contentLocation-locationCreated-294-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[43] - Painting-contentLocation-locationCreated-294 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Painting-contentLocation-locationCreated-294-jsonld.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[75] - eg-0341 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0341-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[106] - Conversation-Message-295 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Conversation-Message-295-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[137] - Conversation-Message-295 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Conversation-Message-295-jsonld.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[188] - eg-0342 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0342-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[207] - Message-296 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Message-296-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[226] - Message-296 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Message-296-jsonld.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[259] - eg-0343 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0343-microdata.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[287] - EmailMessage-toRecipient-bccRecipient-ccRecipient-297 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmailMessage-toRecipient-bccRecipient-ccRecipient-297-rdfa.html").to lint_cleanly}
  specify("sdo-creativework-examples.txt[315] - EmailMessage-toRecipient-bccRecipient-ccRecipient-297 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmailMessage-toRecipient-bccRecipient-ccRecipient-297-jsonld.html").to lint_cleanly}

  # Examples from sdo-fibo-examples.txt
  specify("sdo-fibo-examples.txt[12] - eg-0350 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0350-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[38] - CreditCard-MonetaryAmount-UnitPriceSpecification-298 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-MonetaryAmount-UnitPriceSpecification-298-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[65] - CreditCard-MonetaryAmount-UnitPriceSpecification-298 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreditCard-MonetaryAmount-UnitPriceSpecification-298-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[118] - eg-0351 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0351-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[160] - LoanOrCredit-MonetaryAmount-299 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoanOrCredit-MonetaryAmount-299-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[203] - LoanOrCredit-MonetaryAmount-299 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LoanOrCredit-MonetaryAmount-299-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[280] - eg-0352 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0352-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[361] - BankAccount-300 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankAccount-300-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[443] - BankAccount-300 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankAccount-300-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[583] - eg-0353 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0353-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[619] - DepositAccount-MonetaryAmount-301 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepositAccount-MonetaryAmount-301-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[655] - DepositAccount-MonetaryAmount-301 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DepositAccount-MonetaryAmount-301-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[739] - eg-0354 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0354-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[756] - PaymentCard-302 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentCard-302-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[773] - PaymentCard-302 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentCard-302-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[826] - eg-0355 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0355-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[884] - PaymentService-303 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentService-303-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[939] - PaymentService-303 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PaymentService-303-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1037] - eg-0356 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0356-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1049] - FinancialProduct-304 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FinancialProduct-304-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1061] - FinancialProduct-304 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/FinancialProduct-304-jsonld.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1095] - eg-0357 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0357-microdata.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1106] - InvestmentOrDeposit-305 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentOrDeposit-305-rdfa.html").to lint_cleanly}
  specify("sdo-fibo-examples.txt[1117] - InvestmentOrDeposit-305 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentOrDeposit-305-jsonld.html").to lint_cleanly}

  # Examples from sdo-hotels-examples.txt
  specify("sdo-hotels-examples.txt[21] - eg-0358 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0358-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[42] - Hotel-306 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-306-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[63] - Hotel-306 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-306-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[100] - eg-0359 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0359-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[112] - starRating-307 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-307-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[116] - starRating-307 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-307-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[132] - eg-0360 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0360-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[148] - starRating-308 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-308-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[152] - starRating-308 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/starRating-308-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[168] - eg-0361 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0361-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[179] - Hotel-logo-image-309 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-logo-image-309-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[183] - Hotel-logo-image-309 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Hotel-logo-image-309-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[198] - eg-0362 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0362-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[208] - hasMap-310 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/hasMap-310-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[212] - hasMap-310 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/hasMap-310-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[222] - eg-0363 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0363-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[242] - GeoCoordinates-geo-311 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GeoCoordinates-geo-311-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[246] - GeoCoordinates-geo-311 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/GeoCoordinates-geo-311-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[256] - eg-0364 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0364-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[266] - numberOfRooms-312 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-312-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[270] - numberOfRooms-312 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-312-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[280] - eg-0365 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0365-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[297] - numberOfRooms-313 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-313-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[301] - numberOfRooms-313 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/numberOfRooms-313-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[311] - eg-0366 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0366-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[331] - feature-LocationFeatureSpecification-314 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-314-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[335] - feature-LocationFeatureSpecification-314 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-314-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[345] - eg-0367 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0367-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[366] - feature-LocationFeatureSpecification-hoursAvailable-315 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-hoursAvailable-315-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[370] - feature-LocationFeatureSpecification-hoursAvailable-315 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/feature-LocationFeatureSpecification-hoursAvailable-315-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[380] - eg-0368 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0368-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[392] - checkinTime-checkoutTime-316 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/checkinTime-checkoutTime-316-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[396] - checkinTime-checkoutTime-316 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/checkinTime-checkoutTime-316-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[406] - eg-0369 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0369-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[424] - availableLanguage-Language-317 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/availableLanguage-Language-317-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[428] - availableLanguage-Language-317 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/availableLanguage-Language-317-jsonld.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[438] - eg-0370 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0370-microdata.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[459] - HotelRoom-Hotel-318 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HotelRoom-Hotel-318-rdfa.html").to lint_cleanly}
  specify("sdo-hotels-examples.txt[463] - HotelRoom-Hotel-318 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HotelRoom-Hotel-318-jsonld.html").to lint_cleanly}

  # Examples from issue-1100-examples.txt
  specify("issue-1100-examples.txt[9] - eg-0321 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0321-microdata.html").to lint_cleanly}
  specify("issue-1100-examples.txt[13] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-319 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-319-rdfa.html").to lint_cleanly}
  specify("issue-1100-examples.txt[17] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-319 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-319-jsonld.html").to lint_cleanly}
  specify("issue-1100-examples.txt[49] - eg-0322 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0322-microdata.html").to lint_cleanly}
  specify("issue-1100-examples.txt[53] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-320 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-320-rdfa.html").to lint_cleanly}
  specify("issue-1100-examples.txt[57] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-320 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-320-jsonld.html").to lint_cleanly}
  specify("issue-1100-examples.txt[87] - eg-0323 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0323-microdata.html").to lint_cleanly}
  specify("issue-1100-examples.txt[91] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-321 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-321-rdfa.html").to lint_cleanly}
  specify("issue-1100-examples.txt[95] - accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-321 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/accessMode-accessModeSufficient-accessibilitySummary-accessibilityFeature-321-jsonld.html").to lint_cleanly}

  # Examples from sdo-digital-document-examples.txt
  specify("sdo-digital-document-examples.txt[7] - eg-0348 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0348-microdata.html").to lint_cleanly}
  specify("sdo-digital-document-examples.txt[11] - DigitalDocument-ReadPermission-WritePermission-DigitalDocumentPermission-322 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DigitalDocument-ReadPermission-WritePermission-DigitalDocumentPermission-322-rdfa.html").to lint_cleanly}
  specify("sdo-digital-document-examples.txt[15] - DigitalDocument-ReadPermission-WritePermission-DigitalDocumentPermission-322 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DigitalDocument-ReadPermission-WritePermission-DigitalDocumentPermission-322-jsonld.html").to lint_cleanly}

  # Examples from sdo-videogame-examples.txt
  specify("sdo-videogame-examples.txt[47] - eg-0447 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0447-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[102] - VideoGame-323 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-323-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[155] - VideoGame-323 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-323-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[239] - eg-0448 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0448-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[281] - VideoGame-324 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-324-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[323] - VideoGame-324 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-324-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[423] - eg-0449 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0449-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[484] - VideoGame-325 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-325-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[545] - VideoGame-325 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-325-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[615] - eg-0450 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0450-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[642] - VideoGame-326 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-326-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[669] - VideoGame-326 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-326-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[705] - eg-0451 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0451-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[709] - VideoGame-327 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-327-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[713] - VideoGame-327 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-327-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[756] - eg-0452 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0452-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[772] - Game-328 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Game-328-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[788] - Game-328 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Game-328-jsonld.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[821] - eg-0453 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0453-microdata.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[825] - VideoGame-329 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-329-rdfa.html").to lint_cleanly}
  specify("sdo-videogame-examples.txt[829] - VideoGame-329 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/VideoGame-329-jsonld.html").to lint_cleanly}

  # Examples from sdo-bus-stop-examples.txt
  specify("sdo-bus-stop-examples.txt[7] - eg-0331 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0331-microdata.html").to lint_cleanly}
  specify("sdo-bus-stop-examples.txt[11] - BusStop-330 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusStop-330-rdfa.html").to lint_cleanly}
  specify("sdo-bus-stop-examples.txt[15] - BusStop-330 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BusStop-330-jsonld.html").to lint_cleanly}

  # Examples from sdo-ClaimReview-issue-1061-examples.txt
  specify("sdo-ClaimReview-issue-1061-examples.txt[46] - eg-0324 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0324-microdata.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[93] - ClaimReview-331 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-331-rdfa.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[97] - ClaimReview-331 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-331-jsonld.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[146] - eg-0325 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0325-microdata.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[150] - ClaimReview-332 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-332-rdfa.html").to lint_cleanly}
  specify("sdo-ClaimReview-issue-1061-examples.txt[154] - ClaimReview-332 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ClaimReview-332-jsonld.html").to lint_cleanly}

  # Examples from sdo-exhibitionevent-examples.txt
  specify("sdo-exhibitionevent-examples.txt[13] - eg-0349 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0349-microdata.html").to lint_cleanly}
  specify("sdo-exhibitionevent-examples.txt[26] - ExhibitionEvent-333 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExhibitionEvent-333-rdfa.html").to lint_cleanly}
  specify("sdo-exhibitionevent-examples.txt[39] - ExhibitionEvent-333 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExhibitionEvent-333-jsonld.html").to lint_cleanly}

  # Examples from sdo-social-media-examples.txt
  specify("sdo-social-media-examples.txt[14] - eg-0423 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0423-microdata.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[38] - SocialMediaPosting-sharedContent-334 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SocialMediaPosting-sharedContent-334-rdfa.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[62] - SocialMediaPosting-sharedContent-334 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SocialMediaPosting-sharedContent-334-jsonld.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[104] - eg-0424 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0424-microdata.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[134] - LiveBlog-BlogPosting-335 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LiveBlog-BlogPosting-335-rdfa.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[164] - LiveBlog-BlogPosting-335 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/LiveBlog-BlogPosting-335-jsonld.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[214] - eg-0425 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0425-microdata.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[229] - DiscussionForumPosting-336 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscussionForumPosting-336-rdfa.html").to lint_cleanly}
  specify("sdo-social-media-examples.txt[244] - DiscussionForumPosting-336 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DiscussionForumPosting-336-jsonld.html").to lint_cleanly}

  # Examples from sdo-itemlist-examples.txt
  specify("sdo-itemlist-examples.txt[14] - eg-0377 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0377-microdata.html").to lint_cleanly}
  specify("sdo-itemlist-examples.txt[31] - BreadcrumbList-ItemList-ListItem-itemListElement-item-337 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BreadcrumbList-ItemList-ListItem-itemListElement-item-337-rdfa.html").to lint_cleanly}
  specify("sdo-itemlist-examples.txt[46] - BreadcrumbList-ItemList-ListItem-itemListElement-item-337 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BreadcrumbList-ItemList-ListItem-itemListElement-item-337-jsonld.html").to lint_cleanly}

  # Examples from sdo-music-examples.txt
  specify("sdo-music-examples.txt[7] - eg-0387 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0387-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[11] - MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-338 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-338-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[15] - MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-338 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicAlbum-MusicGroup-MusicRelease-AlbumRelease-StudioAlbum-338-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[82] - eg-0388 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0388-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[86] - Person-MusicComposition-Organization-339 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-MusicComposition-Organization-339-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[90] - Person-MusicComposition-Organization-339 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-MusicComposition-Organization-339-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[133] - eg-0389 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0389-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[137] - MusicGroup-City-MusicAlbum-340 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicGroup-City-MusicAlbum-340-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[141] - MusicGroup-City-MusicAlbum-340 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicGroup-City-MusicAlbum-340-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[215] - eg-0390 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0390-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[219] - MusicRecording-MusicComposition-341 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-341-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[223] - MusicRecording-MusicComposition-341 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-341-jsonld.html").to lint_cleanly}
  specify("sdo-music-examples.txt[252] - eg-0391 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0391-microdata.html").to lint_cleanly}
  specify("sdo-music-examples.txt[256] - MusicRecording-MusicComposition-PublicationEvent-MusicRelease-342 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-PublicationEvent-MusicRelease-342-rdfa.html").to lint_cleanly}
  specify("sdo-music-examples.txt[260] - MusicRecording-MusicComposition-PublicationEvent-MusicRelease-342 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MusicRecording-MusicComposition-PublicationEvent-MusicRelease-342-jsonld.html").to lint_cleanly}

  # Examples from sdo-offeredby-examples.txt
  specify("sdo-offeredby-examples.txt[35] - eg-0393 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0393-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[71] - Offer-offeredBy-Book-additionalType-343 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-offeredBy-Book-additionalType-343-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[116] - Offer-offeredBy-Book-additionalType-343 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-offeredBy-Book-additionalType-343-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[174] - eg-0394 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0394-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[178] - Offer-makesOffer-344 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-makesOffer-344-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[218] - Offer-makesOffer-344 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-makesOffer-344-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[286] - eg-0395 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0395-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[321] - offeredBy-Book-345 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offeredBy-Book-345-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[352] - offeredBy-Book-345 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/offeredBy-Book-345-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[415] - eg-0396 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0396-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[469] - Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-346 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-346-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[523] - Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-346 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-OfferCatalog-Service-LocalBusiness-hasOfferCatalog-346-jsonld.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[610] - eg-0397 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0397-microdata.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[643] - Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-347 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-347-rdfa.html").to lint_cleanly}
  specify("sdo-offeredby-examples.txt[674] - Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-347 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Offer-FoodEstablishment-GeoCircle-DeliveryChargeSpecification-PriceSpecification-347-jsonld.html").to lint_cleanly}

  # Examples from sdo-single-family-residence-examples.txt
  specify("sdo-single-family-residence-examples.txt[7] - eg-0422 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0422-microdata.html").to lint_cleanly}
  specify("sdo-single-family-residence-examples.txt[11] - SingleFamilyResidence-Accommodation-occupancy-floorSize-leaseLength-348 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SingleFamilyResidence-Accommodation-occupancy-floorSize-leaseLength-348-rdfa.html").to lint_cleanly}
  specify("sdo-single-family-residence-examples.txt[15] - SingleFamilyResidence-Accommodation-occupancy-floorSize-leaseLength-348 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SingleFamilyResidence-Accommodation-occupancy-floorSize-leaseLength-348-jsonld.html").to lint_cleanly}

  # Examples from sdo-library-examples.txt
  specify("sdo-library-examples.txt[43] - eg-0378 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0378-microdata.html").to lint_cleanly}
  specify("sdo-library-examples.txt[99] - Library-OpeningHoursSpecification-openingHoursSpecification-349 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Library-OpeningHoursSpecification-openingHoursSpecification-349-rdfa.html").to lint_cleanly}
  specify("sdo-library-examples.txt[155] - Library-OpeningHoursSpecification-openingHoursSpecification-349 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Library-OpeningHoursSpecification-openingHoursSpecification-349-jsonld.html").to lint_cleanly}

  # Examples from sdo-trip-examples.txt
  specify("sdo-trip-examples.txt[92] - eg-0441 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0441-microdata.html").to lint_cleanly}
  specify("sdo-trip-examples.txt[181] - Trip-TouristTrip-itinerary-350 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Trip-TouristTrip-itinerary-350-rdfa.html").to lint_cleanly}
  specify("sdo-trip-examples.txt[270] - Trip-TouristTrip-itinerary-350 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Trip-TouristTrip-itinerary-350-jsonld.html").to lint_cleanly}

  # Examples from sdo-defined-region-examples.txt
  specify("sdo-defined-region-examples.txt[7] - eg-0346 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0346-microdata.html").to lint_cleanly}
  specify("sdo-defined-region-examples.txt[11] - DefinedRegion-351 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedRegion-351-rdfa.html").to lint_cleanly}
  specify("sdo-defined-region-examples.txt[15] - DefinedRegion-351 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedRegion-351-jsonld.html").to lint_cleanly}

  # Examples from MedicalScholarlyArticle-examples.txt
  specify("MedicalScholarlyArticle-examples.txt[20] - eg-0222 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0222-microdata.html").to lint_cleanly}
  specify("MedicalScholarlyArticle-examples.txt[71] - MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-352 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-352-rdfa.html").to lint_cleanly}
  specify("MedicalScholarlyArticle-examples.txt[121] - MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-352 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalScholarlyArticle-MedicalGuideline-MedicalGuidelineRecommendation-352-jsonld.html").to lint_cleanly}

  # Examples from medicalGuideline-examples.txt
  specify("medicalGuideline-examples.txt[14] - eg-0224 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0224-microdata.html").to lint_cleanly}
  specify("medicalGuideline-examples.txt[46] - MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-353 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-353-rdfa.html").to lint_cleanly}
  specify("medicalGuideline-examples.txt[79] - MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-353 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalGuideline-MedicalGuidelineRecommendation-MedicalGuidelineContraindication-353-jsonld.html").to lint_cleanly}

  # Examples from medicalCondition-examples.txt
  specify("medicalCondition-examples.txt[34] - eg-0223 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0223-microdata.html").to lint_cleanly}
  specify("medicalCondition-examples.txt[136] - MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-354 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-354-rdfa.html").to lint_cleanly}
  specify("medicalCondition-examples.txt[238] - MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-354 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalCondition-MedicalCause-MedicalRiskFactor-DDxElement-MedicalSymptom-MedicalSignOrSymptom-354-jsonld.html").to lint_cleanly}

  # Examples from medicalWebpage-examples.txt
  specify("medicalWebpage-examples.txt[15] - eg-0225 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0225-microdata.html").to lint_cleanly}
  specify("medicalWebpage-examples.txt[47] - MedicalWebPage-DrugClass-355 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalWebPage-DrugClass-355-rdfa.html").to lint_cleanly}
  specify("medicalWebpage-examples.txt[79] - MedicalWebPage-DrugClass-355 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MedicalWebPage-DrugClass-355-jsonld.html").to lint_cleanly}

  # Examples from bsdo-newspaper-examples.txt
  specify("bsdo-newspaper-examples.txt[14] - eg-0218 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0218-microdata.html").to lint_cleanly}
  specify("bsdo-newspaper-examples.txt[23] - Newspaper-356 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Newspaper-356-rdfa.html").to lint_cleanly}
  specify("bsdo-newspaper-examples.txt[32] - Newspaper-356 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Newspaper-356-jsonld.html").to lint_cleanly}

  # Examples from bsdo-thesis-examples.txt
  specify("bsdo-thesis-examples.txt[15] - eg-0219 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0219-microdata.html").to lint_cleanly}
  specify("bsdo-thesis-examples.txt[25] - Thesis-inSupportOf-357 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Thesis-inSupportOf-357-rdfa.html").to lint_cleanly}
  specify("bsdo-thesis-examples.txt[35] - Thesis-inSupportOf-357 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Thesis-inSupportOf-357-jsonld.html").to lint_cleanly}

  # Examples from comics-examples.txt
  specify("comics-examples.txt[33] - eg-0221 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0221-microdata.html").to lint_cleanly}
  specify("comics-examples.txt[82] - ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-358 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-358-rdfa.html").to lint_cleanly}
  specify("comics-examples.txt[131] - ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-358 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ComicIssue-ComicSeries-ComicCoverArt-CoverArt-artist-colorist-letterer-358-jsonld.html").to lint_cleanly}

  # Examples from bsdo-chapter-examples.txt
  specify("bsdo-chapter-examples.txt[18] - eg-0216 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0216-microdata.html").to lint_cleanly}
  specify("bsdo-chapter-examples.txt[34] - Chapter-359 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Chapter-359-rdfa.html").to lint_cleanly}
  specify("bsdo-chapter-examples.txt[50] - Chapter-359 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Chapter-359-jsonld.html").to lint_cleanly}

  # Examples from bsdo-atlas-examples.txt
  specify("bsdo-atlas-examples.txt[15] - eg-0214 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0214-microdata.html").to lint_cleanly}
  specify("bsdo-atlas-examples.txt[25] - Atlas-360 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Atlas-360-rdfa.html").to lint_cleanly}
  specify("bsdo-atlas-examples.txt[35] - Atlas-360 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Atlas-360-jsonld.html").to lint_cleanly}

  # Examples from bsdo-collection-examples.txt
  specify("bsdo-collection-examples.txt[27] - eg-0217 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0217-microdata.html").to lint_cleanly}
  specify("bsdo-collection-examples.txt[59] - Collection-361 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Collection-361-rdfa.html").to lint_cleanly}
  specify("bsdo-collection-examples.txt[91] - Collection-361 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Collection-361-jsonld.html").to lint_cleanly}

  # Examples from bsdo-audiobook-examples.txt
  specify("bsdo-audiobook-examples.txt[19] - eg-0215 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0215-microdata.html").to lint_cleanly}
  specify("bsdo-audiobook-examples.txt[37] - Audiobook-readBy-362 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-readBy-362-rdfa.html").to lint_cleanly}
  specify("bsdo-audiobook-examples.txt[55] - Audiobook-readBy-362 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-readBy-362-jsonld.html").to lint_cleanly}

  # Examples from bsdo-translation-examples.txt
  specify("bsdo-translation-examples.txt[25] - eg-0220 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0220-microdata.html").to lint_cleanly}
  specify("bsdo-translation-examples.txt[44] - CreativeWork-Book-translator-translationOfWork-workTranslation-363 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Book-translator-translationOfWork-workTranslation-363-rdfa.html").to lint_cleanly}
  specify("bsdo-translation-examples.txt[63] - CreativeWork-Book-translator-translationOfWork-workTranslation-363 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Book-translator-translationOfWork-workTranslation-363-jsonld.html").to lint_cleanly}

  # Examples from issue-1779-examples.txt
  specify("issue-1779-examples.txt[18] - eg-0259 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0259-microdata.html").to lint_cleanly}
  specify("issue-1779-examples.txt[51] - EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-364 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-364-rdfa.html").to lint_cleanly}
  specify("issue-1779-examples.txt[81] - EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-364 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-educationalLevel-competencyRequired-364-jsonld.html").to lint_cleanly}
  specify("issue-1779-examples.txt[121] - eg-0260 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0260-microdata.html").to lint_cleanly}
  specify("issue-1779-examples.txt[145] - EducationalOccupationalCredential-credentialCategory-365 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-365-rdfa.html").to lint_cleanly}
  specify("issue-1779-examples.txt[167] - EducationalOccupationalCredential-credentialCategory-365 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-credentialCategory-365-jsonld.html").to lint_cleanly}
  specify("issue-1779-examples.txt[199] - eg-0261 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0261-microdata.html").to lint_cleanly}
  specify("issue-1779-examples.txt[210] - EducationalOccupationalCredential-Occupation-educationRequirements-366 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-Occupation-educationRequirements-366-rdfa.html").to lint_cleanly}
  specify("issue-1779-examples.txt[221] - EducationalOccupationalCredential-Occupation-educationRequirements-366 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalCredential-Occupation-educationRequirements-366-jsonld.html").to lint_cleanly}

  # Examples from issue-2396-examples.txt
  specify("issue-2396-examples.txt[9] - eg-0285 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0285-microdata.html").to lint_cleanly}
  specify("issue-2396-examples.txt[13] - applicationContact-367 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/applicationContact-367-rdfa.html").to lint_cleanly}
  specify("issue-2396-examples.txt[17] - applicationContact-367 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/applicationContact-367-jsonld.html").to lint_cleanly}
  specify("issue-2396-examples.txt[42] - eg-0286 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0286-microdata.html").to lint_cleanly}
  specify("issue-2396-examples.txt[46] - employerOverview-368 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/employerOverview-368-rdfa.html").to lint_cleanly}
  specify("issue-2396-examples.txt[50] - employerOverview-368 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/employerOverview-368-jsonld.html").to lint_cleanly}
  specify("issue-2396-examples.txt[69] - eg-0287 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0287-microdata.html").to lint_cleanly}
  specify("issue-2396-examples.txt[73] - industry-DefinedTerm-369 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/industry-DefinedTerm-369-rdfa.html").to lint_cleanly}
  specify("issue-2396-examples.txt[77] - industry-DefinedTerm-369 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/industry-DefinedTerm-369-jsonld.html").to lint_cleanly}

  # Examples from issue-2384-examples.txt
  specify("issue-2384-examples.txt[7] - eg-0283 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0283-microdata.html").to lint_cleanly}
  specify("issue-2384-examples.txt[11] - sensoryRequirement-370 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sensoryRequirement-370-rdfa.html").to lint_cleanly}
  specify("issue-2384-examples.txt[15] - sensoryRequirement-370 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/sensoryRequirement-370-jsonld.html").to lint_cleanly}
  specify("issue-2384-examples.txt[38] - eg-0284 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0284-microdata.html").to lint_cleanly}
  specify("issue-2384-examples.txt[42] - physicalRequirement-371 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/physicalRequirement-371-rdfa.html").to lint_cleanly}
  specify("issue-2384-examples.txt[46] - physicalRequirement-371 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/physicalRequirement-371-jsonld.html").to lint_cleanly}

  # Examples from issue-2490-examples.txt
  specify("issue-2490-examples.txt[8] - eg-0297 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0297-microdata.html").to lint_cleanly}
  specify("issue-2490-examples.txt[12] - SpecialAnnouncement-CovidTestingFacility-372 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-CovidTestingFacility-372-rdfa.html").to lint_cleanly}
  specify("issue-2490-examples.txt[16] - SpecialAnnouncement-CovidTestingFacility-372 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-CovidTestingFacility-372-jsonld.html").to lint_cleanly}
  specify("issue-2490-examples.txt[41] - eg-0298 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0298-microdata.html").to lint_cleanly}
  specify("issue-2490-examples.txt[45] - SpecialAnnouncement-373 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-373-rdfa.html").to lint_cleanly}
  specify("issue-2490-examples.txt[49] - SpecialAnnouncement-373 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-373-jsonld.html").to lint_cleanly}
  specify("issue-2490-examples.txt[81] - eg-0299 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0299-microdata.html").to lint_cleanly}
  specify("issue-2490-examples.txt[85] - SpecialAnnouncement-374 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-374-rdfa.html").to lint_cleanly}
  specify("issue-2490-examples.txt[89] - SpecialAnnouncement-374 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-374-jsonld.html").to lint_cleanly}

  # Examples from issue-2296-examples.txt
  specify("issue-2296-examples.txt[8] - eg-0281 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0281-microdata.html").to lint_cleanly}
  specify("issue-2296-examples.txt[12] - employmentUnit-375 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/employmentUnit-375-rdfa.html").to lint_cleanly}
  specify("issue-2296-examples.txt[16] - employmentUnit-375 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/employmentUnit-375-jsonld.html").to lint_cleanly}

  # Examples from issue-1457-examples.txt
  specify("issue-1457-examples.txt[7] - eg-0240 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0240-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[11] - Event-Schedule-eventSchedule-376 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-376-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[15] - Event-Schedule-eventSchedule-376 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-376-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[44] - eg-0241 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0241-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[48] - Event-Schedule-eventSchedule-377 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-377-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[52] - Event-Schedule-eventSchedule-377 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-377-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[76] - eg-0242 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0242-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[80] - Event-Schedule-eventSchedule-378 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-378-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[84] - Event-Schedule-eventSchedule-378 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-378-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[110] - eg-0243 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0243-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[114] - Event-Schedule-eventSchedule-379 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-379-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[118] - Event-Schedule-eventSchedule-379 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-379-jsonld.html").to lint_cleanly}
  specify("issue-1457-examples.txt[164] - eg-0244 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0244-microdata.html").to lint_cleanly}
  specify("issue-1457-examples.txt[168] - Event-Schedule-eventSchedule-380 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-380-rdfa.html").to lint_cleanly}
  specify("issue-1457-examples.txt[172] - Event-Schedule-eventSchedule-380 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Event-Schedule-eventSchedule-380-jsonld.html").to lint_cleanly}

  # Examples from issue-2419-examples.txt
  specify("issue-2419-examples.txt[7] - eg-0294 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0294-microdata.html").to lint_cleanly}
  specify("issue-2419-examples.txt[11] - EducationalOccupationalProgram-381 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalProgram-381-rdfa.html").to lint_cleanly}
  specify("issue-2419-examples.txt[15] - EducationalOccupationalProgram-381 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalProgram-381-jsonld.html").to lint_cleanly}

  # Examples from issue-1950-examples.txt
  specify("issue-1950-examples.txt[7] - eg-0266 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0266-microdata.html").to lint_cleanly}
  specify("issue-1950-examples.txt[11] - CorrectionComment-correction-382 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CorrectionComment-correction-382-rdfa.html").to lint_cleanly}
  specify("issue-1950-examples.txt[15] - CorrectionComment-correction-382 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CorrectionComment-correction-382-jsonld.html").to lint_cleanly}

  # Examples from issue-2083-examples.txt
  specify("issue-2083-examples.txt[7] - eg-0268 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0268-microdata.html").to lint_cleanly}
  specify("issue-2083-examples.txt[11] - JobPosting-applicantLocationRequirements-383 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-applicantLocationRequirements-383-rdfa.html").to lint_cleanly}
  specify("issue-2083-examples.txt[15] - JobPosting-applicantLocationRequirements-383 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-applicantLocationRequirements-383-jsonld.html").to lint_cleanly}

  # Examples from issue-2289-examples.txt
  specify("issue-2289-examples.txt[7] - eg-0277 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0277-microdata.html").to lint_cleanly}
  specify("issue-2289-examples.txt[11] - CollegeOrUniversity-384 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CollegeOrUniversity-384-rdfa.html").to lint_cleanly}
  specify("issue-2289-examples.txt[15] - CollegeOrUniversity-384 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CollegeOrUniversity-384-jsonld.html").to lint_cleanly}
  specify("issue-2289-examples.txt[39] - eg-0278 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0278-microdata.html").to lint_cleanly}
  specify("issue-2289-examples.txt[43] - EducationalOccupationalProgram-385 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalProgram-385-rdfa.html").to lint_cleanly}
  specify("issue-2289-examples.txt[47] - EducationalOccupationalProgram-385 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EducationalOccupationalProgram-385-jsonld.html").to lint_cleanly}
  specify("issue-2289-examples.txt[123] - eg-0279 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0279-microdata.html").to lint_cleanly}
  specify("issue-2289-examples.txt[127] - WorkBasedProgram-386 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WorkBasedProgram-386-rdfa.html").to lint_cleanly}
  specify("issue-2289-examples.txt[131] - WorkBasedProgram-386 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WorkBasedProgram-386-jsonld.html").to lint_cleanly}

  # Examples from issue-373-examples.txt
  specify("issue-373-examples.txt[23] - eg-0306 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0306-microdata.html").to lint_cleanly}
  specify("issue-373-examples.txt[48] - PodcastSeries-387 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PodcastSeries-387-rdfa.html").to lint_cleanly}
  specify("issue-373-examples.txt[52] - PodcastSeries-387 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PodcastSeries-387-jsonld.html").to lint_cleanly}
  specify("issue-373-examples.txt[94] - eg-0307 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0307-microdata.html").to lint_cleanly}
  specify("issue-373-examples.txt[117] - PodcastEpisode-388 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PodcastEpisode-388-rdfa.html").to lint_cleanly}
  specify("issue-373-examples.txt[121] - PodcastEpisode-388 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PodcastEpisode-388-jsonld.html").to lint_cleanly}
  specify("issue-373-examples.txt[160] - eg-0308 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0308-microdata.html").to lint_cleanly}
  specify("issue-373-examples.txt[174] - PodcastSeason-389 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PodcastSeason-389-rdfa.html").to lint_cleanly}
  specify("issue-373-examples.txt[178] - PodcastSeason-389 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PodcastSeason-389-jsonld.html").to lint_cleanly}

  # Examples from issue-1156-examples.txt
  specify("issue-1156-examples.txt[57] - eg-0230 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0230-microdata.html").to lint_cleanly}
  specify("issue-1156-examples.txt[112] - Legislation-390 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-390-rdfa.html").to lint_cleanly}
  specify("issue-1156-examples.txt[167] - Legislation-390 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-390-jsonld.html").to lint_cleanly}
  specify("issue-1156-examples.txt[257] - eg-0231 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0231-microdata.html").to lint_cleanly}
  specify("issue-1156-examples.txt[302] - Legislation-LegislationObject-391 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-LegislationObject-391-rdfa.html").to lint_cleanly}
  specify("issue-1156-examples.txt[347] - Legislation-LegislationObject-391 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Legislation-LegislationObject-391-jsonld.html").to lint_cleanly}

  # Examples from issue-1698-examples.txt
  specify("issue-1698-examples.txt[7] - eg-0249 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0249-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[11] - Person-Occupation-392 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-392-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[15] - Person-Occupation-392 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-392-jsonld.html").to lint_cleanly}
  specify("issue-1698-examples.txt[36] - eg-0250 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0250-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[40] - Person-Occupation-Role-occupationalCategory-393 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-Role-occupationalCategory-393-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[44] - Person-Occupation-Role-occupationalCategory-393 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-Occupation-Role-occupationalCategory-393-jsonld.html").to lint_cleanly}
  specify("issue-1698-examples.txt[77] - eg-0251 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0251-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[81] - JobPosting-Occupation-occupationalCategory-394 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-Occupation-occupationalCategory-394-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[85] - JobPosting-Occupation-occupationalCategory-394 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-Occupation-occupationalCategory-394-jsonld.html").to lint_cleanly}
  specify("issue-1698-examples.txt[121] - eg-0252 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0252-microdata.html").to lint_cleanly}
  specify("issue-1698-examples.txt[125] - Occupation-MonetaryAmountDistribution-395 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-MonetaryAmountDistribution-395-rdfa.html").to lint_cleanly}
  specify("issue-1698-examples.txt[129] - Occupation-MonetaryAmountDistribution-395 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-MonetaryAmountDistribution-395-jsonld.html").to lint_cleanly}

  # Examples from issue-894-examples.txt
  specify("issue-894-examples.txt[10] - eg-0314 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0314-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[18] - DefinedTerm-termCode-396 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-termCode-396-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[26] - DefinedTerm-termCode-396 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-termCode-396-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[57] - eg-0315 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0315-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[83] - DefinedTerm-DefinedTermSet-inDefinedTermSet-397 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-DefinedTermSet-inDefinedTermSet-397-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[107] - DefinedTerm-DefinedTermSet-inDefinedTermSet-397 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-DefinedTermSet-inDefinedTermSet-397-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[144] - eg-0316 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0316-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[152] - DefinedTerm-inDefinedTermSet-termCode-398 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-inDefinedTermSet-termCode-398-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[160] - DefinedTerm-inDefinedTermSet-termCode-398 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/DefinedTerm-inDefinedTermSet-termCode-398-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[182] - eg-0317 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0317-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[194] - CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-399 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-399-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[206] - CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-399 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-hasCategoryCode-inCodeSet-399-jsonld.html").to lint_cleanly}
  specify("issue-894-examples.txt[242] - eg-0318 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0318-microdata.html").to lint_cleanly}
  specify("issue-894-examples.txt[263] - CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-400 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-400-rdfa.html").to lint_cleanly}
  specify("issue-894-examples.txt[284] - CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-400 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CategoryCode-CategoryCodeSet-inCodeSet-codeValue-hasCategoryCode-400-jsonld.html").to lint_cleanly}

  # Examples from issue-1050-examples.txt
  specify("issue-1050-examples.txt[7] - eg-0228 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0228-microdata.html").to lint_cleanly}
  specify("issue-1050-examples.txt[11] - contentReferenceTime-Event-Article-about-401 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/contentReferenceTime-Event-Article-about-401-rdfa.html").to lint_cleanly}
  specify("issue-1050-examples.txt[15] - contentReferenceTime-Event-Article-about-401 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/contentReferenceTime-Event-Article-about-401-jsonld.html").to lint_cleanly}

  # Examples from issue-1810-examples.txt
  specify("issue-1810-examples.txt[67] - eg-0262 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0262-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[117] - TouristDestination-402 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristDestination-402-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[179] - TouristDestination-402 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristDestination-402-jsonld.html").to lint_cleanly}
  specify("issue-1810-examples.txt[283] - eg-0263 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0263-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[315] - TouristTrip-itinerary-403 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-itinerary-403-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[359] - TouristTrip-itinerary-403 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-itinerary-403-jsonld.html").to lint_cleanly}
  specify("issue-1810-examples.txt[434] - eg-0264 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0264-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[451] - TouristTrip-Trip-itinerary-404 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-Trip-itinerary-404-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[472] - TouristTrip-Trip-itinerary-404 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-Trip-itinerary-404-jsonld.html").to lint_cleanly}
  specify("issue-1810-examples.txt[631] - eg-0265 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0265-microdata.html").to lint_cleanly}
  specify("issue-1810-examples.txt[726] - TouristTrip-405 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-405-rdfa.html").to lint_cleanly}
  specify("issue-1810-examples.txt[858] - TouristTrip-405 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/TouristTrip-405-jsonld.html").to lint_cleanly}

  # Examples from issue-1045-examples.txt
  specify("issue-1045-examples.txt[7] - eg-0226 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0226-microdata.html").to lint_cleanly}
  specify("issue-1045-examples.txt[11] - ReserveAction-LinkRole-406 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-406-rdfa.html").to lint_cleanly}
  specify("issue-1045-examples.txt[15] - ReserveAction-LinkRole-406 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-406-jsonld.html").to lint_cleanly}
  specify("issue-1045-examples.txt[42] - eg-0227 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0227-microdata.html").to lint_cleanly}
  specify("issue-1045-examples.txt[46] - ReserveAction-LinkRole-407 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-407-rdfa.html").to lint_cleanly}
  specify("issue-1045-examples.txt[50] - ReserveAction-LinkRole-407 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ReserveAction-LinkRole-407-jsonld.html").to lint_cleanly}

  # Examples from issue-2085-examples.txt
  specify("issue-2085-examples.txt[7] - eg-0269 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0269-microdata.html").to lint_cleanly}
  specify("issue-2085-examples.txt[11] - ProgramMembership-membershipPointsEarned-408 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProgramMembership-membershipPointsEarned-408-rdfa.html").to lint_cleanly}
  specify("issue-2085-examples.txt[15] - ProgramMembership-membershipPointsEarned-408 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ProgramMembership-membershipPointsEarned-408-jsonld.html").to lint_cleanly}

  # Examples from issue-2514-examples.txt
  specify("issue-2514-examples.txt[7] - eg-0300 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0300-microdata.html").to lint_cleanly}
  specify("issue-2514-examples.txt[11] - SpecialAnnouncement-409 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-409-rdfa.html").to lint_cleanly}
  specify("issue-2514-examples.txt[15] - SpecialAnnouncement-409 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-409-jsonld.html").to lint_cleanly}

  # Examples from issue-2405-examples.txt
  specify("issue-2405-examples.txt[10] - eg-0288 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0288-microdata.html").to lint_cleanly}
  specify("issue-2405-examples.txt[14] - Guide-410 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-410-rdfa.html").to lint_cleanly}
  specify("issue-2405-examples.txt[18] - Guide-410 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-410-jsonld.html").to lint_cleanly}
  specify("issue-2405-examples.txt[43] - eg-0289 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0289-microdata.html").to lint_cleanly}
  specify("issue-2405-examples.txt[47] - Guide-411 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-411-rdfa.html").to lint_cleanly}
  specify("issue-2405-examples.txt[51] - Guide-411 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-411-jsonld.html").to lint_cleanly}
  specify("issue-2405-examples.txt[110] - eg-0290 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0290-microdata.html").to lint_cleanly}
  specify("issue-2405-examples.txt[114] - Guide-412 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-412-rdfa.html").to lint_cleanly}
  specify("issue-2405-examples.txt[118] - Guide-412 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-412-jsonld.html").to lint_cleanly}
  specify("issue-2405-examples.txt[203] - eg-0291 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0291-microdata.html").to lint_cleanly}
  specify("issue-2405-examples.txt[207] - Guide-413 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-413-rdfa.html").to lint_cleanly}
  specify("issue-2405-examples.txt[211] - Guide-413 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Guide-413-jsonld.html").to lint_cleanly}
  specify("issue-2405-examples.txt[278] - eg-0292 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0292-microdata.html").to lint_cleanly}
  specify("issue-2405-examples.txt[282] - Recommendation-414 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recommendation-414-rdfa.html").to lint_cleanly}
  specify("issue-2405-examples.txt[286] - Recommendation-414 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recommendation-414-jsonld.html").to lint_cleanly}
  specify("issue-2405-examples.txt[371] - eg-0293 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0293-microdata.html").to lint_cleanly}
  specify("issue-2405-examples.txt[375] - Recommendation-415 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recommendation-415-rdfa.html").to lint_cleanly}
  specify("issue-2405-examples.txt[379] - Recommendation-415 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Recommendation-415-jsonld.html").to lint_cleanly}

  # Examples from issue-271-examples.txt
  specify("issue-271-examples.txt[7] - eg-0304 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0304-microdata.html").to lint_cleanly}
  specify("issue-271-examples.txt[11] - Quotation-spokenByCharacter-416 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-416-rdfa.html").to lint_cleanly}
  specify("issue-271-examples.txt[15] - Quotation-spokenByCharacter-416 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-416-jsonld.html").to lint_cleanly}
  specify("issue-271-examples.txt[39] - eg-0305 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0305-microdata.html").to lint_cleanly}
  specify("issue-271-examples.txt[43] - Quotation-spokenByCharacter-417 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-417-rdfa.html").to lint_cleanly}
  specify("issue-271-examples.txt[47] - Quotation-spokenByCharacter-417 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Quotation-spokenByCharacter-417-jsonld.html").to lint_cleanly}

  # Examples from issue-1670-examples.txt
  specify("issue-1670-examples.txt[7] - eg-0246 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0246-microdata.html").to lint_cleanly}
  specify("issue-1670-examples.txt[11] - CreativeWork-Thing-418 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Thing-418-rdfa.html").to lint_cleanly}
  specify("issue-1670-examples.txt[15] - CreativeWork-Thing-418 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/CreativeWork-Thing-418-jsonld.html").to lint_cleanly}

  # Examples from issue-2366-examples.txt
  specify("issue-2366-examples.txt[14] - eg-0282 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0282-microdata.html").to lint_cleanly}
  specify("issue-2366-examples.txt[18] - Audiobook-419 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-419-rdfa.html").to lint_cleanly}
  specify("issue-2366-examples.txt[22] - Audiobook-419 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Audiobook-419-jsonld.html").to lint_cleanly}

  # Examples from issue-2421-examples.txt
  specify("issue-2421-examples.txt[7] - eg-0295 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0295-microdata.html").to lint_cleanly}
  specify("issue-2421-examples.txt[11] - Person-InteractionCounter-420 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-InteractionCounter-420-rdfa.html").to lint_cleanly}
  specify("issue-2421-examples.txt[15] - Person-InteractionCounter-420 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-InteractionCounter-420-jsonld.html").to lint_cleanly}
  specify("issue-2421-examples.txt[43] - eg-0296 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0296-microdata.html").to lint_cleanly}
  specify("issue-2421-examples.txt[47] - Organization-InteractionCounter-421 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-InteractionCounter-421-rdfa.html").to lint_cleanly}
  specify("issue-2421-examples.txt[51] - Organization-InteractionCounter-421 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Organization-InteractionCounter-421-jsonld.html").to lint_cleanly}

  # Examples from issue-2543-examples.txt
  specify("issue-2543-examples.txt[7] - eg-0302 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0302-microdata.html").to lint_cleanly}
  specify("issue-2543-examples.txt[11] - NonprofitType-nonprofitStatus-422 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NonprofitType-nonprofitStatus-422-rdfa.html").to lint_cleanly}
  specify("issue-2543-examples.txt[15] - NonprofitType-nonprofitStatus-422 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NonprofitType-nonprofitStatus-422-jsonld.html").to lint_cleanly}

  # Examples from issue-2108-examples.txt
  specify("issue-2108-examples.txt[7] - eg-0270 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0270-microdata.html").to lint_cleanly}
  specify("issue-2108-examples.txt[11] - PronounceableText-phoneticText-423 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PronounceableText-phoneticText-423-rdfa.html").to lint_cleanly}
  specify("issue-2108-examples.txt[15] - PronounceableText-phoneticText-423 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PronounceableText-phoneticText-423-jsonld.html").to lint_cleanly}
  specify("issue-2108-examples.txt[37] - eg-0271 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0271-microdata.html").to lint_cleanly}
  specify("issue-2108-examples.txt[41] - PronounceableText-phoneticText-424 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PronounceableText-phoneticText-424-rdfa.html").to lint_cleanly}
  specify("issue-2108-examples.txt[45] - PronounceableText-phoneticText-424 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/PronounceableText-phoneticText-424-jsonld.html").to lint_cleanly}

  # Examples from issue-2599-examples.txt
  specify("issue-2599-examples.txt[7] - eg-0303 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0303-microdata.html").to lint_cleanly}
  specify("issue-2599-examples.txt[11] - Schedule-LiteraryEvent-425 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Schedule-LiteraryEvent-425-rdfa.html").to lint_cleanly}
  specify("issue-2599-examples.txt[15] - Schedule-LiteraryEvent-425 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Schedule-LiteraryEvent-425-jsonld.html").to lint_cleanly}

  # Examples from issue-2534-examples.txt
  specify("issue-2534-examples.txt[7] - eg-0301 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0301-microdata.html").to lint_cleanly}
  specify("issue-2534-examples.txt[11] - SpecialAnnouncement-governmentBenefitsInfo-GovernmentService-jurisdiction-serviceType-audience-Audience-426 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-governmentBenefitsInfo-GovernmentService-jurisdiction-serviceType-audience-Audience-426-rdfa.html").to lint_cleanly}
  specify("issue-2534-examples.txt[15] - SpecialAnnouncement-governmentBenefitsInfo-GovernmentService-jurisdiction-serviceType-audience-Audience-426 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/SpecialAnnouncement-governmentBenefitsInfo-GovernmentService-jurisdiction-serviceType-audience-Audience-426-jsonld.html").to lint_cleanly}

  # Examples from issue-1741-examples.txt
  specify("issue-1741-examples.txt[7] - eg-0253 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0253-microdata.html").to lint_cleanly}
  specify("issue-1741-examples.txt[11] - ActionAccessSpecification-MediaSubscription-ListenAction-427 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ActionAccessSpecification-MediaSubscription-ListenAction-427-rdfa.html").to lint_cleanly}
  specify("issue-1741-examples.txt[15] - ActionAccessSpecification-MediaSubscription-ListenAction-427 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ActionAccessSpecification-MediaSubscription-ListenAction-427-jsonld.html").to lint_cleanly}

  # Examples from issue-1062-examples.txt
  specify("issue-1062-examples.txt[9] - eg-0229 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0229-microdata.html").to lint_cleanly}
  specify("issue-1062-examples.txt[13] - HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-428 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-428-rdfa.html").to lint_cleanly}
  specify("issue-1062-examples.txt[17] - HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-428 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/HealthInsurancePlan-PreferredNetwork-NonPreferredNetwork. HealthPlanFormulary-HealthPlanCostSharingSpecification-428-jsonld.html").to lint_cleanly}

  # Examples from issue-template-examples.txt
  specify("issue-template-examples.txt[7] - @@@@comma-separated-list-here@@@@ replace @@@@ with content.-429 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/@@@@comma-separated-list-here@@@@ replace @@@@ with content.-429-microdata.html").to lint_cleanly}
  specify("issue-template-examples.txt[11] - @@@@comma-separated-list-here@@@@ replace @@@@ with content.-429 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/@@@@comma-separated-list-here@@@@ replace @@@@ with content.-429-rdfa.html").to lint_cleanly}
  specify("issue-template-examples.txt[15] - @@@@comma-separated-list-here@@@@ replace @@@@ with content.-429 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/@@@@comma-separated-list-here@@@@ replace @@@@ with content.-429-jsonld.html").to lint_cleanly}

  # Examples from issue-1689-examples.txt
  specify("issue-1689-examples.txt[7] - eg-0247 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0247-microdata.html").to lint_cleanly}
  specify("issue-1689-examples.txt[11] - EmployerAggregateRating-430 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmployerAggregateRating-430-rdfa.html").to lint_cleanly}
  specify("issue-1689-examples.txt[15] - EmployerAggregateRating-430 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EmployerAggregateRating-430-jsonld.html").to lint_cleanly}
  specify("issue-1689-examples.txt[39] - eg-0248 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0248-microdata.html").to lint_cleanly}
  specify("issue-1689-examples.txt[43] - Review-Rating-reviewAspect-431 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Review-Rating-reviewAspect-431-rdfa.html").to lint_cleanly}
  specify("issue-1689-examples.txt[47] - Review-Rating-reviewAspect-431 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Review-Rating-reviewAspect-431-jsonld.html").to lint_cleanly}

  # Examples from issue-2192-examples.txt
  specify("issue-2192-examples.txt[8] - eg-0275 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0275-microdata.html").to lint_cleanly}
  specify("issue-2192-examples.txt[12] - Occupation-occupationalCategory-432 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-occupationalCategory-432-rdfa.html").to lint_cleanly}
  specify("issue-2192-examples.txt[16] - Occupation-occupationalCategory-432 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Occupation-occupationalCategory-432-jsonld.html").to lint_cleanly}
  specify("issue-2192-examples.txt[46] - eg-0276 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0276-microdata.html").to lint_cleanly}
  specify("issue-2192-examples.txt[50] - Person-jobTitle-433 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-jobTitle-433-rdfa.html").to lint_cleanly}
  specify("issue-2192-examples.txt[54] - Person-jobTitle-433 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Person-jobTitle-433-jsonld.html").to lint_cleanly}

  # Examples from issue-447-examples.txt
  specify("issue-447-examples.txt[7] - eg-0313 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0313-microdata.html").to lint_cleanly}
  specify("issue-447-examples.txt[11] - EventSeries-434 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventSeries-434-rdfa.html").to lint_cleanly}
  specify("issue-447-examples.txt[15] - EventSeries-434 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/EventSeries-434-jsonld.html").to lint_cleanly}

  # Examples from issue-2109-examples.txt
  specify("issue-2109-examples.txt[7] - eg-0272 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0272-microdata.html").to lint_cleanly}
  specify("issue-2109-examples.txt[11] - RadioBroadcastService-callSign-435 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioBroadcastService-callSign-435-rdfa.html").to lint_cleanly}
  specify("issue-2109-examples.txt[15] - RadioBroadcastService-callSign-435 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/RadioBroadcastService-callSign-435-jsonld.html").to lint_cleanly}

  # Examples from issue-383-examples.txt
  specify("issue-383-examples.txt[7] - eg-0309 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0309-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[11] - Grant-436 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-436-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[15] - Grant-436 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-436-jsonld.html").to lint_cleanly}
  specify("issue-383-examples.txt[40] - eg-0310 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0310-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[44] - Grant-437 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-437-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[48] - Grant-437 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-437-jsonld.html").to lint_cleanly}
  specify("issue-383-examples.txt[69] - eg-0311 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0311-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[73] - MonetaryGrant-438 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MonetaryGrant-438-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[77] - MonetaryGrant-438 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MonetaryGrant-438-jsonld.html").to lint_cleanly}
  specify("issue-383-examples.txt[107] - eg-0312 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0312-microdata.html").to lint_cleanly}
  specify("issue-383-examples.txt[111] - Grant-439 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-439-rdfa.html").to lint_cleanly}
  specify("issue-383-examples.txt[115] - Grant-439 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Grant-439-jsonld.html").to lint_cleanly}

  # Examples from issue-1253-examples.txt
  specify("issue-1253-examples.txt[13] - eg-0232 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0232-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[23] - BrokerageAccount-440 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BrokerageAccount-440-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[33] - BrokerageAccount-440 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BrokerageAccount-440-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[67] - eg-0233 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0233-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[78] - InvestmentFund-441 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentFund-441-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[89] - InvestmentFund-441 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/InvestmentFund-441-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[135] - eg-0234 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0234-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[169] - MortgageLoan-RepaymentSpecification-442 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MortgageLoan-RepaymentSpecification-442-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[203] - MortgageLoan-RepaymentSpecification-442 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/MortgageLoan-RepaymentSpecification-442-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[262] - eg-0235 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0235-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[294] - ExchangeRateSpecification-443 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExchangeRateSpecification-443-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[326] - ExchangeRateSpecification-443 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ExchangeRateSpecification-443-jsonld.html").to lint_cleanly}
  specify("issue-1253-examples.txt[370] - eg-0236 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0236-microdata.html").to lint_cleanly}
  specify("issue-1253-examples.txt[379] - BankTransfer-444 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankTransfer-444-rdfa.html").to lint_cleanly}
  specify("issue-1253-examples.txt[388] - BankTransfer-444 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/BankTransfer-444-jsonld.html").to lint_cleanly}

  # Examples from issue-1525-examples.txt
  specify("issue-1525-examples.txt[7] - eg-0245 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0245-microdata.html").to lint_cleanly}
  specify("issue-1525-examples.txt[11] - NewsArticle-445 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NewsArticle-445-rdfa.html").to lint_cleanly}
  specify("issue-1525-examples.txt[15] - NewsArticle-445 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/NewsArticle-445-jsonld.html").to lint_cleanly}

  # Examples from issue-2294-examples.txt
  specify("issue-2294-examples.txt[9] - eg-0280 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0280-microdata.html").to lint_cleanly}
  specify("issue-2294-examples.txt[13] - JobPosting-qualifications-446 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-qualifications-446-rdfa.html").to lint_cleanly}
  specify("issue-2294-examples.txt[17] - JobPosting-qualifications-446 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/JobPosting-qualifications-446-jsonld.html").to lint_cleanly}

  # Examples from issue-1389-examples.txt
  specify("issue-1389-examples.txt[7] - eg-0237 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0237-microdata.html").to lint_cleanly}
  specify("issue-1389-examples.txt[11] - speakable-cssSelector-SpeakableSpecification-447 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-447-rdfa.html").to lint_cleanly}
  specify("issue-1389-examples.txt[15] - speakable-cssSelector-SpeakableSpecification-447 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-447-jsonld.html").to lint_cleanly}
  specify("issue-1389-examples.txt[59] - eg-0238 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0238-microdata.html").to lint_cleanly}
  specify("issue-1389-examples.txt[74] - speakable-cssSelector-SpeakableSpecification-448 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-448-rdfa.html").to lint_cleanly}
  specify("issue-1389-examples.txt[78] - speakable-cssSelector-SpeakableSpecification-448 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/speakable-cssSelector-SpeakableSpecification-448-jsonld.html").to lint_cleanly}

  # Examples from issue-2021-examples.txt
  specify("issue-2021-examples.txt[7] - eg-0267 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0267-microdata.html").to lint_cleanly}
  specify("issue-2021-examples.txt[11] - Clip-endOffset-startOffset-449 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Clip-endOffset-startOffset-449-rdfa.html").to lint_cleanly}
  specify("issue-2021-examples.txt[15] - Clip-endOffset-startOffset-449 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/Clip-endOffset-startOffset-449-jsonld.html").to lint_cleanly}

  # Examples from issue-1759-examples.txt
  specify("issue-1759-examples.txt[10] - eg-0257 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0257-microdata.html").to lint_cleanly}
  specify("issue-1759-examples.txt[18] - materialExtent-CreativeWork-450 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-450-rdfa.html").to lint_cleanly}
  specify("issue-1759-examples.txt[25] - materialExtent-CreativeWork-450 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-450-jsonld.html").to lint_cleanly}
  specify("issue-1759-examples.txt[45] - eg-0258 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0258-microdata.html").to lint_cleanly}
  specify("issue-1759-examples.txt[61] - materialExtent-CreativeWork-451 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-451-rdfa.html").to lint_cleanly}
  specify("issue-1759-examples.txt[76] - materialExtent-CreativeWork-451 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/materialExtent-CreativeWork-451-jsonld.html").to lint_cleanly}

  # Examples from issue-1423-examples.txt
  specify("issue-1423-examples.txt[7] - eg-0239 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0239-microdata.html").to lint_cleanly}
  specify("issue-1423-examples.txt[11] - WebAPI-documentation-termsOfService-452 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebAPI-documentation-termsOfService-452-rdfa.html").to lint_cleanly}
  specify("issue-1423-examples.txt[15] - WebAPI-documentation-termsOfService-452 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/WebAPI-documentation-termsOfService-452-jsonld.html").to lint_cleanly}

  # Examples from issue-2173-examples.txt
  specify("issue-2173-examples.txt[7] - eg-0273 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0273-microdata.html").to lint_cleanly}
  specify("issue-2173-examples.txt[12] - conditionsOfAccess-453 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/conditionsOfAccess-453-rdfa.html").to lint_cleanly}
  specify("issue-2173-examples.txt[17] - conditionsOfAccess-453 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/conditionsOfAccess-453-jsonld.html").to lint_cleanly}
  specify("issue-2173-examples.txt[36] - eg-0274 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0274-microdata.html").to lint_cleanly}
  specify("issue-2173-examples.txt[41] - conditionsOfAccess-ArchiveComponent-454 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/conditionsOfAccess-ArchiveComponent-454-rdfa.html").to lint_cleanly}
  specify("issue-2173-examples.txt[46] - conditionsOfAccess-ArchiveComponent-454 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/conditionsOfAccess-ArchiveComponent-454-jsonld.html").to lint_cleanly}

  # Examples from issue-1758-examples.txt
  specify("issue-1758-examples.txt[16] - eg-0254 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0254-microdata.html").to lint_cleanly}
  specify("issue-1758-examples.txt[28] - ArchiveOrganization-archiveHeld-455 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveOrganization-archiveHeld-455-rdfa.html").to lint_cleanly}
  specify("issue-1758-examples.txt[41] - ArchiveOrganization-archiveHeld-455 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveOrganization-archiveHeld-455-jsonld.html").to lint_cleanly}
  specify("issue-1758-examples.txt[87] - eg-0255 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0255-microdata.html").to lint_cleanly}
  specify("issue-1758-examples.txt[114] - ArchiveComponent-holdingArchive-456 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-holdingArchive-456-rdfa.html").to lint_cleanly}
  specify("issue-1758-examples.txt[141] - ArchiveComponent-holdingArchive-456 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-holdingArchive-456-jsonld.html").to lint_cleanly}
  specify("issue-1758-examples.txt[198] - eg-0256 (microdata)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/eg-0256-microdata.html").to lint_cleanly}
  specify("issue-1758-examples.txt[228] - ArchiveComponent-457 (rdfa)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-457-rdfa.html").to lint_cleanly}
  specify("issue-1758-examples.txt[255] - ArchiveComponent-457 (jsonld)") {expect("/Users/gregg/Projects/schemaorg/scripts/spec/data/ArchiveComponent-457-jsonld.html").to lint_cleanly}
end
