require "goo"
require "pry"

ARGV[0]
if ARGV[0].nil?
  puts "use write_ontology.rb <sparql_endpoint>"
  puts "use write_ontology.rb localhost:9000"
  exit
end

epr = ARGV[0]
Goo.configure do |conf|
  conf.add_sparql_backend(:main, query: "http://#{epr}/sparql/",
                          data: "http://#{epr}/data/",
                          update: "http://#{epr}/update/",
                          options: { rules: :NONE })
  conf.add_redis_backend(:host => "localhost")
  conf.add_namespace(:owl, RDF::Vocabulary.new("http://www.w3.org/2002/07/owl#"))
  conf.add_namespace(:rdfs, RDF::Vocabulary.new("http://www.w3.org/2000/01/rdf-schema#"))
  conf.add_namespace(:foaf, RDF::Vocabulary.new("http://xmlns.com/foaf/0.1/"),default=true)
  conf.add_namespace(:rdf, RDF::Vocabulary.new("http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
end

puts "using ... #{Goo.sparql_data_client.url}"

5.times do |i|
  puts "#{i} asserting data ..."
  graph = "http://test.bioontology.org/test/nemo"
  ntriples_file_path = "../../data/nemo_ontology.ntriples"
  result = Goo.sparql_data_client.put_triples(
                        graph,
                        ntriples_file_path,
                        mime_type="application/x-turtle")
  puts "#{i} deleting data ..."
  Goo.sparql_data_client.delete_graph(graph)
  puts "#{i} iteration done"
end
