class MetriquesLigne(object):
    """Classe utilitaire qui calcule certaines métriques
    de la ligne, comme par exemple le centroïde vertical,
    l'aire moyenne des boîtes entourant les caractères,
    etc."""
    pass

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
        evaluateurs.append(evaluateur)

    def is_appel(self, char):
        """Retourne True uniquement si tous les évaluateurs contenus
        retournent True"""
        for e in evaluateurs:
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

class EvaluateurAppelPositionLigneRegression(object):
    """Calcule une droite de régression à partir des
    centroïdes des caractères de la ligne.

    Cette droite est ensuite utilisée pour déterminer
    si un caractère est un indice ou non"""

    def __init__(self, ligne):
        centroides = [c.centroide_vertical for c in ligne.chars]



class EvaluateurAppelAlphaNum(object):
    """Règle qui détermine qu'un caractère est utilisé comme
    appel s'il est un nombre ou une lettre"""

    def is_appel(self, char):
        return char.isalpha() or char.isalnum()

class EvaluateurAireMoyenne(object):
    """Règle qui détermine qu'un caractère est utilisé comme
    appel si son aire moyenne est plus petite que l'aire
    moyenne de la ligne"""

    def __init__(self, ligne):
        self.ligne = ligne

    def is_appel(self, char):
        return char.aire_moyenne < self.ligne.aire_moyenne
