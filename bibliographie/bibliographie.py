#-*- coding: utf-8 -*-
import sys
import shlex
import StringIO
from subprocess import Popen, PIPE
from pybtex.database.input import bibtex
import os
import urllib
from BeautifulSoup import BeautifulSoup

class MyUrlOpener(urllib.FancyURLopener):
    version = "Lynx/2.8.8dev.3 libwww-FM/2.14 SSL-MM/1.4.1"

def get_bibtex(citation):
    """Retourne l'entrée bibtex pour une citation"""
    abspath = os.path.abspath('./lib/anystyle-wrapper.rb')
    cmd_anystyle = ["ruby", "%s" % abspath, "%s" % citation]
    p = Popen(cmd_anystyle, stdout=PIPE)
    strio = StringIO.StringIO(p.communicate()[0])
    parser = bibtex.Parser()
    return parser.parse_stream(strio)

class ChercheurRessource(object):
    """ classe qui permet de chercher les ressources"""
    def __init__(self, engins):
        self.engins = engins
        urllib._urlopener = MyUrlOpener()
        self.fichier = 1
    def chercher(self, entree):
        for engin in self.engins:
            url_requete = engin.url_recherche(entree)
            raw_res = urllib.urlopen(url_requete).read()
            html = BeautifulSoup(raw_res)
            gs_rt = html.find('div', { 'class' : 'gs_rt' })
            if gs_rt:
                link = gs_rt.find('a')
                if link:
                    return link.attrs[0][1]


class EnginGoogle(object):
    def __init__(self, url_base):
        self.url_base = url_base
    def url_recherche(self, entree):
        url = self.url_base
        if 'title' in entree.fields:
            url = "%sintitle:%s" % (url, urllib.quote(entree.fields['title']))
        if 'author' in entree.persons:
            url = "%s+inauthor:%s" % (url, urllib.quote(entree.persons['author'][0].last()[0]))

        return url

if __name__ == '__main__':
    pass
