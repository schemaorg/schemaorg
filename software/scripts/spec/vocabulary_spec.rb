$:.unshift File.expand_path("..", __FILE__)
require 'spec_helper'
require 'rdf/turtle'

describe "Vocabulary" do
  before(:all) {RDF::Reasoner.apply(:rdfs, :owl, :schema)}

  it "defines RDF::Vocab::SCHEMA" do
    expect { RDF::Vocab.const_get(:SCHEMA) }.not_to raise_error
  end

  %w(domainIncludes rangeIncludes inverseOf).each do |prop|
    it "defines schema:#{prop}" do
      expect {RDF::Vocab::SCHEMA[prop]}.not_to raise_error
    end
  end

  context "detects superseded terms" do
    {
      "members superseded by member" => [
        %(
          @prefix schema: <http://schema.org/> .
          <http://example.com/foo> a schema:Organization; schema:members "Manny" .
        ),
        {
          property: {"schema:members" => ["Term is superseded by schema:member"]},
        }
      ],
    }.each do |name, (input, errors)|
      it name do
        graph = RDF::Graph.new << RDF::Turtle::Reader.new(input)
        expect(graph.lint).to have_errors errors
      end
    end
  end

  context "entailments" do
    RDF::Vocab::SCHEMA.each do |term|
      if term.type.to_s =~ /Class/
        context term.pname do
          it "subClassOf" do
            expect {term.subClassOf.map(&:pname)}.not_to raise_error
          end
          it "equivalentClass" do
            expect {term.equivalentClass.map(&:pname)}.not_to raise_error
          end
        end
      elsif term.type.to_s =~ /Property/
        context term.pname do
          it "subPropertyOf" do
            expect {term.subPropertyOf.map(&:pname)}.not_to raise_error
          end
          it "domain" do
            expect {term.domain.map(&:pname)}.not_to raise_error
          end
          it "range" do
            expect {term.range.map(&:pname)}.not_to raise_error
          end
          it "equivalentProperty" do
            expect {term.equivalentProperty.map(&:pname)}.not_to raise_error
          end
        end
      end
    end
  end

end
