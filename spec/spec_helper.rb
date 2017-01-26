$:.unshift File.dirname(__FILE__)

require "bundler/setup"
require 'rubygems'
require 'rspec'
require 'linkeddata'
require 'rdf/vocab'
load    'schema.rb'
require 'json/ld/preloaded'
load    'schema_context.rb'

::RSpec.configure do |c|
  c.filter_run focus: true
  c.run_all_when_everything_filtered = true
  c.example_status_persistence_file_path = "rspec-failures.txt"
end

EXAMPLES = Dir.glob File.expand_path("../data/*", __FILE__)

RSpec::Matchers.define :lint_cleanly do
  match do |example|
    example = example
    begin
      g = RDF::Graph.load(example)
      @messages = g.lint
      expect(@messages).to be_empty
    rescue
      @messages = {exception: {message: [$!.message]}}
      false
    end
  end

  failure_message do
    str = StringIO.new
    str.puts "Source: #{File.read(@actual)}\n\nResults:"
    @messages.each do |kind, term_messages|
      term_messages.each do |term, messages|
        str.puts "#{kind}  #{term}"
        messages.each {|m| str.puts "  #{m}"}
      end
    end
    str.rewind
    str.read
  end
end

RSpec::Matchers.define :have_errors do |errors|
  match do |actual|
    return false unless actual.keys == errors.keys
    actual.each do |area_key, area_values|
      return false unless area_values.length == errors[area_key].length
      area_values.each do |term, values|
        return false unless values.length == errors[area_key][term].length
        values.each_with_index do |v, i|
          return false unless case m = errors[area_key][term][i]
          when Regexp then m.match v
          else  m == v
          end
        end
      end
    end
    true
  end

  failure_message do |actual|
    "expected errors to match #{errors.to_json(JSON::LD::JSON_STATE)}\nwas #{actual.to_json(JSON::LD::JSON_STATE)}"
  end

  failure_message_when_negated do |actual|
    "expected errors not to match #{errors.to_json(JSON::LD::JSON_STATE)}"
  end
end
