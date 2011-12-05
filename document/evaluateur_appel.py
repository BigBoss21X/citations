#-*- coding: utf-8 -*-
"""
>>> from modele import Ligne, Document
>>> print "allo"
allo
>>> d = Document("../test/")
>>> len(d.pages)
1
>>> p = d.pages[0]
>>> p.txt
'./test/revuesociete01-100t.txt'
>>> p.lignes[25]
[loi, de, la, Cité19,, ils, ne, peuvent, pas, non, plus, reconnaître, aux, lois, de, la, nature, le]
>>> l = p.lignes[25]
>>> l.mots[3]
Cité19,
>>> m = l.mots[3]
>>> [{'x1': c.x1, 'x2': c.x2, 'y1': c.y1, 'y2': c.y2, 'char': c.char} for c in m.chars]
>>> print allo
allo
"""
import ConfigParser
import numpy as np

class EvaluateurAppelFactory(object):
    """Classe utilitaire qui calcule certaines métriques
    de la ligne, comme par exemple le centroïde vertical,
    l'aire moyenne des boîtes entourant les caractères,
    etc."""
    def __init__(self, no_page, config=None):
        self.config = config
        self.section = None
        if config:
            self.cp = ConfigParser.ConfigParser()
            self.cp.read(self.config)
            for i in range(1, len(self.cp.sections())+1):
                limite = self.cp.getint(str(i), 'page-limite')
                if no_page < limite:
                    self.section = str(i)
                    break
            if not self.section: self.section = '1'
            print self.section

    def get_evaluateur_appel(self, ligne):
        e = EvaluateurAppelComposite()
        if not self.config:
            e.add_evaluateur(EvaluateurAppelPositionLigne(ligne))
            e.add_evaluateur(EvaluateurAppelTailleCaractere(ligne))
            e.add_evaluateur(EvaluateurAppelNum())
            return e
        else:
            try:
                position = self.cp.get(self.section, 'position')
            except:
                position = 'decalage'
            try:
                classe = self.cp.get(self.section, 'classe-caract')
            except:
                classe = 'numerique'
            try:
                taille = self.cp.get(self.section, 'taille-carac-appel')#, vars={'taille-carac-appel': 'a'})
            except:
                taille = None
            print "=======[ section %s ]========" % self.section
            if position == 'lineaire':
                print "lineaire"
                e.add_evaluateur(EvaluateurAppelPositionLigne(ligne))
            if position == 'regression':
                print "regression"
                e.add_evaluateur(EvaluateurAppelPositionLigneRegression(ligne))
            if position == 'decalage':
                print "decalage"
                e.add_evaluateur(EvaluateurAppelDecalageLigneRegression(ligne))
            if classe == 'numerique':
                print "numerique"
                e.add_evaluateur(EvaluateurAppelNum())
            if taille:
                print "taille"
                e.add_evaluateur(EvaluateurAppelTailleCaractere(ligne))
            print "==================="
            return e



class EvaluateurAppelComposite(object):
    """L'évaluateur d'appel composite encapsule plusieurs
    évaluateurs d'appels afin de créer des règles d'évaluation complexes"""
    def __init__(self, evaluateurs=None):
        if not evaluateurs:
            self.evaluateurs = []
        else:
            self.evaluateurs = evaluateurs

    def add_evaluateur(self, evaluateur):
        """Ajoute un évaluateur à la liste d'évaluateurs"""
        self.evaluateurs.append(evaluateur)

    def is_appel(self, char):
        """Retourne True uniquement si tous les évaluateurs contenus
        retournent True"""
        for e in self.evaluateurs:
            if not e.is_appel(char):
                return False
        return True


class EvaluateurAppel(object):
    """Classe abstraite qui évalue si le Caractère
       d'une ligne est un appel de note de bas de
       page ou non"""
    def __init__(self, ligne):
        """Ne nécessite que la ligne pour la configuration
        initiale"""
        self.ligne = ligne

    def is_appel(self, char):
        """Retourne True si le caractère est un appel
        dans le contexte de la ligne"""
        pass


class EvaluateurAppelPositionLigne(object):
    """Détermine si un caractère est utilisé comme appel
    à partir de l'écart entre son centroïde vertical
    et le centroïde vertical de la ligne.

    Le centroïde vertical de la ligne est calculé à partir
    de la moyenne des positions y1 et y2 de chacun des
    caractères contenus dans celle-ci.

    Cette méthode est rapide, mais elle est inefficace dans
    le cas où le document a été numérisé avec un biais et
    que la ligne n'est pas droite"""

    def __init__(self, ligne):
        self.ligne = ligne

    def is_appel(self, char):
        """Retourne True si le centroide vertical du caractères
        est plus élevé que celui de la ligne"""
        return char.centroide_vertical > self.ligne.centroide_vertical


class EvaluateurAppelTailleCaractere(object):
    """Evalue la taille du caractere par rapport
    à celle des autres caractères de la ligne"""
    def __init__(self, ligne, seuil=0.6):
        tailles = [c.aire for c in ligne.chars]
        self.taille_moyenne = 0 if len(ligne.chars) == 0\
                else float(sum(tailles) / len(ligne.chars))
        self.seuil = seuil

    def is_appel(self, char):
        is_appel = (char.aire < self.seuil * self.taille_moyenne)
        return is_appel

class EvaluateurAppelDecalageLigneRegression(object):
    """Calcule deux droites de régression pour les positions
    en y1 et en y2 des caractères.

    Un caractère est considéré comme appel si:
        y1 > moyenne y1
        y2 > moyenne y2
    """
    
    def __init__(self, ligne):
        self.is_init = False
        x = np.array([np.float64(c.centroide_horizontal) for c in ligne.chars])
        y1 = np.array([np.float64(c.y1) for c in ligne.chars])
        y2 = np.array([np.float64(c.y2) for c in ligne.chars])

        self.p_y1 = None
        self.p_y2 = None
        if len(x) and len(y1) and len(y2):
            self.z_y1 = np.polyfit(x, y1, 1)
            self.z_y2 = np.polyfit(x, y2, 1)
            self.p_y1 = np.poly1d(self.z_y1)
            self.p_y2 = np.poly1d(self.z_y2)
            self.is_init = True

    def is_appel(self, char):
        if self.is_init:
            return char.y1 > self.p_y1(char.centroide_horizontal) and\
                char.y2 > self.p_y2(char.centroide_horizontal)

class EvaluateurAppelPositionLigneRegression(object):
    """Calcule une droite de régression à partir des
    centroïdes des caractères de la ligne.

    Cette droite est ensuite utilisée pour déterminer
    si un caractère est un indice ou non"""

    def __init__(self, ligne):
        x = np.array([np.float64(c.centroide_horizontal) for c in ligne.chars])
        y = np.array([np.float64(c.centroide_vertical) for c in ligne.chars])
        self.p = None
        if len(x) > 0 and len(y) > 0:
            z = np.polyfit(x, y, 1)
            self.p = np.poly1d(z)

    def is_appel(self, char):
        if not self.p:
            return False
        return char.centroide_vertical > (self.p(char.centroide_horizontal))


class EvaluateurAppelNum(object):
    """Règle qui détermine qu'un caractère est utilisé
    comme appel s'il est un nombre uniquement"""
    def is_appel(self, char):
        try:
            int(char.char)
            return True
        except ValueError:
            return False

class EvaluateurAppelAlphaNum(object):
    """Règle qui détermine qu'un caractère est utilisé comme
    appel s'il est un nombre ou une lettre"""

    def is_appel(self, char):
        return char.char.isalnum()


class EvaluateurAireMoyenne(object):
    """Règle qui détermine qu'un caractère est utilisé comme
    appel si son aire moyenne est plus petite que l'aire
    moyenne de la ligne"""

    def __init__(self, ligne):
        self.ligne = ligne

    def is_appel(self, char):
        return char.aire_moyenne < self.ligne.aire_moyenne

if __name__ == "__main__":
    import doctest
    doctest.testmod()
