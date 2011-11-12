#-*- coding:utf-8 -*-
#!/usr/bin/python

import os
import sys
import argparse
import logging
import subprocess, shlex
import codecs

from datetime import datetime

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('tessfiles', 'templates'))

class Charactere(object):
    """Caractère d'une ligne"""
    def __init__(self, char, ligne):
        self.char = char
        self.ligne = ligne

    @property
    def aire_boite(self):
        """Aire de la boîte dans laquelle le caractère a été identifié"""
        return (self.char['x2'] - self.char['x1']) * (self.char['y2'] - self.char['y1'])

    @property
    def distance_baseline(self):
        return  self.char['y2'] - self.ligne.y2

    def is_indice(self):
        d_y1 = ((self.char['y1'] - self.ligne.moy_y1) ** 2) ** .5
        d_y2 = ((self.char['y2'] - self.ligne.moy_y2) ** 2) ** .5
      
        return (d_y1 / self.ligne.moy_d_y1, d_y2 / self.ligne.moy_d_y2)
        

class Ligne(object):
    """Ligne d'une page"""
    def __init__(self,ligne, chars):
        #On trouve le X le plus à "gauche"
        self.ligne = ligne
        if chars:
            x1 = sorted(chars, key=lambda a: a['x1'])[0]['x1']
            x2 = sorted(chars, key=lambda a: a['x2'], reverse=True)[0]['x2']
            y1 = sorted(chars, key=lambda a: a['y1'])[0]['y1']
            y2 = sorted(chars, key=lambda a: a['y2'], reverse=True)[0]['y2']

            self.longueur = x2-x1
            self.hauteur = y2-y1

            self.chars = [Charactere(c, self) for c in chars]
    
            self.moy_y1 = sum([c['y1'] for c in chars]) / len(chars)
            self.moy_y2 = sum([c['y2'] for c in chars]) / len(chars)

            self.moy_d_y1 = sum([((c['y1'] - self.moy_y1) ** 2) ** .5 for c in chars])
            self.moy_d_y2 = sum([((c['y2'] - self.moy_y2) ** 2) ** .5 for c in chars])


    def __str__(self):
        return str(self.chars)

class Page(object):
    """Page d'un livre numérisé"""
    def __init__(self, txt, box):
        """Initialise une page à partir de son boxfile et de son
           fichier tesseract"""
        self.txt = txt
        self.filename = os.path.splitext(txt)[0]
        self.lignes = []
        boxes = [{'char':b.split(' ')[0],
                    'x1':int(b.split(' ')[1]),
                    'y1':int(b.split(' ')[2]),
                    'x2':int(b.split(' ')[3]),
                    'y2':int(b.split(' ')[4])}
                  for b in open(box)]
        offset = 0
        with open(self.txt) as f:
            for ligne in f:
                line = ligne.rstrip('\n').decode('utf-8')
                length = len(line.replace(' ', ''))
                self.lignes.append(Ligne(line, boxes[offset:length+offset]))
                offset += length

    def as_html(self):
        with codecs.open("%s.html" % self.filename, 'w', encoding='utf-8') as f:
            template = env.get_template('page.html')
            f.write(template.render(lignes=self.lignes))

if __name__ == '__main__':
    #Configure le logger
    now = datetime.now()
    filename = "tessfiles-%02d%02d%02d-%02d%02d%02d.log" % (now.day, now.month, now.year, now.hour, now.minute, now.second)

    logging.basicConfig(filename=filename)
    parser = argparse.ArgumentParser(description="Numérise un ensemble d'images")
    parser.add_argument('--conversion-tif', action='store_true',
        help="Convertit les images contenues dans les répertoires en format tif")
    parser.add_argument('racine')
    parametres = parser.parse_args(sys.argv[1:len(sys.argv)])
  
    ## Fichiers initialement présents dans la racine.
    fichiers_racine = [f for f in os.listdir(parametres.racine)]

    tess_line = '/usr/bin/tesseract "%s/%s.tif" "%s/%s" -l fra'
    tess_box = "%s makebox" % tess_line

    commandes = [(tess_line % (parametres.racine, os.path.splitext(f)[0], parametres.racine, os.path.splitext(f)[0]),
                  tess_box % (parametres.racine, os.path.splitext(f)[0], parametres.racine, os.path.splitext(f)[0]))
                 for f in os.listdir(parametres.racine)]

    #1 Appeler mogrify pour convertir les png en tif
    if parametres.conversion_tif:
        cmd_mogrify = "mogrify -format tif %s/*.png" % parametres.racine
        print cmd_mogrify
        args_mogrify = shlex.split(cmd_mogrify)
        print args_mogrify
        p = subprocess.call(args_mogrify)
    
    for tess_cmd, box_cmd in commandes:
        subprocess.call(shlex.split(tess_cmd))
        subprocess.call(shlex.split(box_cmd))
