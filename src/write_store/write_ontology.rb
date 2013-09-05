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
end

puts "using ... #{Goo.sparql_data_client.url}"

5.time do |i|
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
