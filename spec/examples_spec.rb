$:.unshift "."
require 'spec_helper'

describe "Examples" do
  before(:all) {RDF::Reasoner.apply(:rdfs, :owl, :schema)}

  EXAMPLES.each do |example|
    specify(example.split('/').last) {expect(example).to lint_cleanly}
  end
end
