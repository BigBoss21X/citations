require 'rubygems'
require 'anystyle/parser'

Anystyle.parser.train 'train.txt', false

citations = Array ['Karl Marx, l\'idéologie allemande, Paris, La Pléiade, 1982, p. 1085.',
                   "Fini le règne des idéologies, place aux acteurs sociaux, Le Devoir, mercredi le 7 janvier 1987.",
                   "Nicole Gagnon, La réforme scolaire au Québec, Université Laval, 1986.",
                   'Les emplois en 1990: les options gagnantes, Ministère de l\'Éducation, cité par Paul Bemard, "Imaginer le réel pour réaliser Pimaginaire", La sociologie et Panthropologie au Québec, Cahiers de l\'ACFAS, 1985, p. 112.',
                   'Broch, Hermann. La mort de Virgile , Gallimard, Coll. "L\'imaginaire", Paris, 1955, p.56.']

citations.each {
    |x| puts Anystyle.parse(x, :bibtex).to_s
}
