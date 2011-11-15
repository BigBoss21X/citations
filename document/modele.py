#-*- coding: utf-8 -*-
import copy
import os
import codecs
import re
from jinja2 import Environment, PackageLoader
import numpy as np
env = Environment(loader=PackageLoader(u'document', u'templates'))

class Charactere(object):
    """Caractère d'une ligne"""
    def __init__(self, char, ligne):
        self.char = char
        self.ligne = ligne

    @property
    def aire(self):
        """Aire de la boîte dans laquelle le caractère a été identifié"""
        return (self.char['x2'] - self.char['x1']) * (self.char['y2'] - self.char['y1'])

    @property
    def distance_baseline(self):
        return self.char['y2'] - self.ligne.y2

    @property
    def hauteur(self):
        return self.char['y2'] - self.char['y1']

    @property
    def centroide_vertical(self):
        """Calcule le centroide vertical du caractère"""
        return self.char['y1'] + self.hauteur / 2 

    @property
    def is_indice(self):
        if (self.aire < self.ligne.aire_moyenne) and\
           (self.centroide_vertical > self.ligne.centroide_vertical):
                return True
        return False

    @property
    def is_appel(self):
        if self.is_indice and\
           (self.char['char'].isalpha() or self.char['char'].isalnum()):
                    return True
        return False
        d_y1 = ((self.char['y1'] - self.ligne.moy_y1) ** 2) ** .5
        d_y2 = ((self.char['y2'] - self.ligne.moy_y2) ** 2) ** .5
      
        return (d_y1 / self.ligne.moy_d_y1, d_y2 / self.ligne.moy_d_y2)

    def __unicode__(self):
         return str(self).decode('utf-8')

    def __str__(self):
        return str(self.char['char'])

    def __repr__(self):
        return self.__str__()
    

class Mot(object):
    """Mot sur une ligne d'une page"""
    def __init__(self, chars):
        self.chars = chars

    def __repr__(self):
        return self.__str__()

    @property
    def contient_appel(self):
        for i in range(len(self.chars))[::-1]:
            c = self.chars[i]
            #On saute les ponctuations.
            if not (c.char['char'].isalnum() or c.char['char'].isalpha()):
                 pass
            else:
                return c.is_appel
    
    @property
    def mot_appel(self):
        appel = []
        for i in range(len(self.chars))[::-1]:
            c = self.chars[i]
            print c
            if c.is_appel:
                appel.insert(0, c)
            else:
                break
        len_mot = len(self.chars) - len(appel)
        return (self.chars[:len_mot], self.chars[len_mot:])

    def __unicode__(self):
         return str(self).decode('utf-8')

    def __str__(self):
       return "".join([str(c) for c in self.chars])

class Ligne(object):
    """Ligne d'une page"""
    def __init__(self,ligne, chars):
        #On trouve le X le plus à "gauche"
        self.ligne = ligne
        self.mots = []
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.moy_y1 = 0
        self.moy_y2 = 0
        if chars:
            #
            # Calcul des métriques de la ligne
            #
            self.chars = [Charactere(c, self) for c in chars]
            self.x1 = sorted(chars, key=lambda a: a['x1'])[0]['x1']
            self.x2 = sorted(chars, key=lambda a: a['x2'], reverse=True)[0]['x2']
            self.y1 = sorted(chars, key=lambda a: a['y1'])[0]['y1']
            self.y2 = sorted(chars, key=lambda a: a['y2'], reverse=True)[0]['y2']
            self.longueur = self.x2 - self.x1
            self.hauteur = self.y2 - self.y1

            self.moy_y1 = sum([c['y1'] for c in chars]) / len(chars)
            self.moy_y2 = sum([c['y2'] for c in chars]) / len(chars)

            self.moy_hauteur = self.moy_y2 - self.moy_y1

            self.aire_moyenne = sum([c.aire for c in self.chars]) / len(self.chars) 

            self.centroide_vertical = self.moy_y1 + self.moy_hauteur

            self.moy_d_y1 = sum([((c['y1'] - self.moy_y1) ** 2) ** .5 for c in chars])
            self.moy_d_y2 = sum([((c['y2'] - self.moy_y2) ** 2) ** .5 for c in chars])
            #
            # Création des mots
            #
            m_index = 0
            for mot in ligne.split(' '):
                self.mots.append(Mot(self.chars[m_index:m_index + len(mot)]))
                m_index = m_index + len(mot)

    
    def __sub__(self, ligne):
        """Retourne la soustraction d'une ligne et d'une
        autre ligne"""
        if not isinstance(ligne, Ligne):
            raise ValueError("on peut uniquement soustraire\
                              une ligne d'une autre")

        if isinstance(ligne, Separation):
            return 0

        if self.moy_y1 > ligne.moy_y2:
            return self.moy_y1 - ligne.moy_y2
        else:
            return ligne.moy_y1 - self.moy_y2

        
    @property
    def appels(self):
        return [mot.mot_appel for mot in self.mots if mot.contient_appel] 
    

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.mots)

class Separation(Ligne):
    def __init__(self):
        self.mots = []
        pass

class PetiteSeparation(Separation):
    def __init__(self):
        self.mots = []
        pass

class MoyenneSeparation(Separation):
    def __init__(self):
        self.mots = []
        pass

class GrandeSeparation(Separation):
    def __init__(self):
        self.mots = []
        pass

class Page(object):
    """Page d'un livre numérisé"""

    m = re.compile('(?P<nom>\w*)-(?P<page>\d+).*')

    def __init__(self, nom):
        """Initialise une page à partir de son boxfile et de son
           fichier tesseract"""

        self.txt = "%s.txt" % nom
        self.filename = os.path.splitext(self.txt)[0]
        self.lignes = []
        print self.filename 
        path, filename = os.path.split(self.filename)
        groups = Page.m.match(filename)
        self.page_suivante = None
        self.page_precedente = None
        if groups:
            self.no_page = int(groups.groupdict()['page'])
            self.page_suivante = filename.replace('{0:03d}'.format(self.no_page),
                                                       '{0:03d}'.format(self.no_page+1))

            self.page_precedente = filename.replace('{0:03d}'.format(self.no_page),
                                                       '{0:03d}'.format(self.no_page-1))

        boxes = []
        try:
            boxes = [{'char':b.split(' ')[0],
                        'x1':int(b.split(' ')[1]),
                        'y1':int(b.split(' ')[2]),
                        'x2':int(b.split(' ')[3]),
                        'y2':int(b.split(' ')[4])}
                      for b in open("%s.box" % nom)]
        except IndexError, e:
            """ Quelque chose est arrivé: par exemple on bute
            sur une page de couverture, ou une page mal formattée"""
            return
        except IOError, e:
            """ Un fichier ne doit pas être là """
            return
        offset = 0
        with open(self.txt) as f:
            for ligne in f:
                line = ligne.rstrip('\n').decode('utf-8')
                length = len(line.replace(' ', ''))
                self.lignes.append(Ligne(line, boxes[offset:length+offset]))
                offset += length
   
        #Calcul des distances entre les lignes
        #avec une copie "décalé" de la liste de lignes
        lignes2 = copy.deepcopy(self.lignes)
        self.lignes_orig = copy.deepcopy(self.lignes)
        lignes2.pop(0)
        self.distances = [l - l2 for (l,l2) in zip(self.lignes, lignes2)]
        self.moy_espaces = np.mean(self.distances)
        self.std_espaces = np.std(self.distances)


        #insérer des espaces "manuels" entre les lignes
        nb_espaces = 1
        for i in range(len(self.distances)):
            espace = self.get_espace(self.distances[i])
            if espace:
                self.lignes.insert(nb_espaces, espace)
                nb_espaces += 1

    def debug_distances(self):
        lignes2 = copy.deepcopy(self.lignes_orig)
        lignes2.pop(0)
        for (l, l2) in zip(self.lignes_orig, lignes2):
            print "LIGNE 1: %s" % l
            print "LIGNE 2: %s" % l2
            print "DISTANCE: %s" % (l - l2)
            espace = self.get_espace(l - l2)
            if espace: print "INSERTION: %s" % espace

    def get_espace(self, distance):
        """ Retourne le type d'espace requis pour une
        distance entre deux lignes """
        if abs(distance - self.moy_espaces) > self.std_espaces * 3:
            return GrandeSeparation()

        if abs(distance - self.moy_espaces) > self.std_espaces * .5:
            return PetiteSeparation()
        return None

    @property
    def appels(self):
        appels = []
        for l in self.lignes:
            appels.extend(l.appels)
        return appels
    def as_html(self):
        with codecs.open("%s.html" % self.filename, 'w', encoding='utf-8') as f:
            template = env.get_template('page.html')
            f.write(template.render(page=self, lignes=self.lignes))

class Document(object):
    """Document numérisé"""
    def __init__(self, path):
        #Avoir uniquement les noms de fichiers
        fichiers = sorted(list(set([os.path.splitext(f)[0] for f in os.listdir(path)])))
        self.pages = [Page("%s/%s" % (path, f)) for f in fichiers]

    def as_html(self):
        for p in self.pages:
            print p.filename
            p.as_html()
