require 'rubygems'
require 'linkeddata'
begin
  require 'rspec/core/rake_task'
  RSpec::Core::RakeTask.new(:spec)
rescue LoadError
end

task :default => [:examples, :vocab, :context, :spec]
desc "Create schema example index"
task :examples  do
  %x{rm -rf #{File.expand_path("../spec/data", __FILE__)}}
  %x{mkdir #{File.expand_path("../spec/data", __FILE__)}}
  number = 0
  Dir.glob(File.expand_path("../data/*examples.txt", __FILE__)).each do |file|
    s = StringScanner.new(File.read(file))
    types = body = format = nil

    while !s.eos?
      # Scan each format until TYPES is found again, or EOF
      body = s.scan_until(/^(TYPES|PRE-MARKUP|MICRODATA|RDFA|JSON|JSONLD):/)
      if body.nil?
        body = s.rest
        s.terminate
      end

      # Trim body
      body = body[0..-(s.matched.to_s.length+1)].gsub("\r", '').strip + "\n"
      case format
      when :microdata, :rdfa, :jsonld
        unless types.include?("FakeEntryNeeded")
          name = nil
          if types.to_s.start_with?('#')
            # In some cases, a more specific name is used.
            name, types = types.split(/\s+/, 2)
            name = name[1..-1]  # Remove initial '#'
          end
          name ||= "#{types.split(/,\s*/).join('-')}-#{number}"
        end
        # Write example out for reading later
        path = "#{name}-#{format}.html"
        File.open(File.expand_path("../spec/data/#{path}", __FILE__), "w") {|f| f.write(body)}
      end

      case s.matched
      when "TYPES:"
        types = s.scan_until(/$/).strip
        number += 1 unless types.include?("FakeEntryNeeded")
        format = :types
      when "PRE-MARKUP:"  then format = :pre
      when "MICRODATA:"   then format = :microdata
      when "RDFA:"        then format = :rdfa
      when "JSON:"        then format = :jsonld
      when "JSONLD:"      then format = :jsonld
      end
    end
  end
end

desc "Create custom pre-compiled vocabulary"
task vocab: "spec/schema.rb"

file "spec/schema.rb" => :do_build do
  rel = Dir.glob(File.expand_path("../data/releases/*", __FILE__)).last
  puts "Generate spec/schema.rb"
  cmd = "bundle exec rdf"
  cmd += " serialize --uri http://schema.org/ --output-format vocabulary"
  cmd += " --module-name RDF::Vocab"
  cmd += " --class-name SCHEMA"
  cmd += " --strict"
  cmd += " -o spec/schema.rb_t"
  cmd += " #{rel}/all-layers.nq"
  puts "  #{cmd}"
  begin
    %x{#{cmd} && mv spec/schema.rb_t spec/schema.rb}
  rescue
    puts "Failed to load schema: #{$!.message}"
  ensure
    %x{rm -f spec/schema.rb_t}
  end
end

desc "Create pre-compiled context"
task context: "spec/schema_context.rb"
file "spec/schema_context.rb" => :do_build do
  puts "Generate spec/schema_context.rb"
  require 'json/ld'
  File.open("spec/schema_context.rb", "w") do |f|
    # FIXME: you would think this would be someplace in the data directory
    # schema_base + '/releases/' + schema_version + '/schema.jsonld'
    c = JSON::LD::Context.new().parse("http://schema.org/")
    f.write c.to_rb
  end
end

task :do_build
