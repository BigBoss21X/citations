#-*- coding: utf-8 -*-
"""Contient les classes pour évaluer les résultats
de l'identification d'appels dans les fichiers.

Les fichiers de résultats doivent être stockés dans 
un fichier xml ayant la syntaxe suivante:
>>> markup = "<document>\
        <page>\
        <titre>page1</titre>\
        <appel>\
        <indice>1</indice>\
        <terme>allo</terme>\
        </appel>\
        </page>\
        </document>"

Les resultats sont stockés dans un dictionnaire
>>> fr = FichierResultats(markup)
>>> fr.resultats
{u'page1': {u'1': u'allo'}}

Les fichiers peuvent être comparés:

>>> fr2 = FichierResultats(markup)
>>> fr == fr2
True

Pour être égaux, les fichiers soivent avoir le même nombre
de résultats:

>>> fr2.resultats['page1']['2'] = 'bonjour'
>>> fr == fr2
False

Les fichiers peuvent être comparés. Lors d'une comparaison,
il y a un fichier de référence et un fichier comparé.

Le fichier sur lequel la méthode est appellée est le référent.
Deux fichiers égaux n'ont pas d'appels superflus ni d'appels manquants:

>>> import copy
>>> fr2 = copy.deepcopy(fr)
>>> resultats = fr.compare(fr2)
>>> len(resultats.manquants)
0
>>> len(resultats.superflus)
0

Les appels superflus sont ceux qui sont présents dans le comparés
et absent dans le référent.

>>> fr2.resultats[u'page1']['2'] = 'bonjour'
>>> resultats = fr.compare(fr2)
>>> resultats.nb_superflus
1
>>> resultats.superflus
{u'page1': {'2': 'bonjour'}}

Les appels manquants sont ceux qui sont présents dans le référent et absents
dans le comparé. 

>>> fr.resultats[u'page1']['3'] = 'allo le monde'
>>> fr.resultats[u'page1']['4'] = 'bonsoir le monde'
>>> fr.resultats[u'page2'] = {'15': 'allo'}
>>> resultats = fr.compare(fr2)
>>> resultats.nb_manquants
3
>>> len(resultats.manquants)
2
>>> u'page1' in resultats.manquants
True
>>> u'page2' in resultats.manquants
True
>>> '3' in resultats.manquants[u'page1']
True
>>> '4' in resultats.manquants[u'page1']
True
>>> '15' in resultats.manquants[u'page2']
True
"""


from BeautifulSoup import BeautifulStoneSoup
import copy

class FichierResultats(object):
    def __init__(self, markup):
        self.xml = BeautifulStoneSoup(markup)
        self.resultats = {}
        for p in self.xml.findAll('page'):
            appels = p.findAll('appel')
            if appels:
                app = {}
                for a in appels:
                    app[a.indice.string] = a.terme.string
                self.resultats[p.titre.string] = app

        self.nb_appels = sum([len(self.resultats[r]) for r in self.resultats.keys()])

    def __eq__(self, fr):
        """Détermine si un fichier de résultats est équivalent à un autre
        """
        #Doit être un fichier de résultats
        if not isinstance(fr, FichierResultats):
            return False

        #Doit avoir le même nombre d'appels
        if not fr.nb_appels == self.nb_appels:
            return False

        #Les appels doivent être dans les mêmes pages
        for k in self.resultats.keys():
            if k not in fr.resultats:
                return False

            if not len(self.resultats[k]) == len(fr.resultats[k]):
                return False

            for indice in self.resultats[k].keys():
                if indice not in fr.resultats[k]:
                    return False
                if not self.resultats[k][indice] == fr.resultats[k][indice]:
                    return False
        return True

    def compare(self, fr):
        return ComparateurResultats(self, fr)

class ComparateurResultats(object):
    """Compare deux fichiers de résultats"""
    def __init__(self, reference, compare):
        self.ref = copy.deepcopy(reference)
        self.aut = copy.deepcopy(compare)

        #Appels présents dans la référence mais manquants dans l'autre
        self.manquants = {}

        #Appels présents dans l'autre mais manquants dans la référence
        self.superflus = {}

        for p in self.ref.resultats:
            #la page est manquante: tous les appels le sonut
            if p not in self.aut.resultats:
                self.manquants[p] = self.ref.resultats[p]
            else:
                #On regarde sinon chacun des appels
                for a in self.ref.resultats[p]:
                    if a not in self.aut.resultats[p]:
                        #On crée l'entrée pour les appels manquants de cette page la première fois
                        if p not in self.manquants:
                            self.manquants[p] = {}
                        self.manquants[p][a] = self.ref.resultats[p][a]
                    else:
                        #On l'enlève: tous les appels qui resteront dans
                        #l'autre fichier seront les appels superflus.
                        self.aut.resultats[p].pop(a)
                #On enlève la page si elle ne contient pas d'appels
                if len(self.aut.resultats[p]) == 0:
                    self.aut.resultats.pop(p)

        self.superflus = self.aut.resultats

        self.nb_manquants = sum([len(p) for p in self.manquants.values()])
        self.nb_superflus = sum([len(p) for p in self.superflus.values()])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
