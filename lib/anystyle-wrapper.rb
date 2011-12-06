require 'rubygems'
require 'anystyle/parser'

ARGV.each do|x|
    puts Anystyle.parse(x, :bibtex).to_s
end

