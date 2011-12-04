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



"""


from BeautifulSoup import BeautifulStoneSoup

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
