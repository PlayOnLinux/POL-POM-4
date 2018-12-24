import threading
import urllib

class Downloader(threading.Thread):
    def __init__(self, url, local):
        threading.Thread.__init__(self)
        self.url = url
        self.local = local
        self.taille_fichier = 0
        self.taille_bloc = 0
        self.nb_blocs = 0
        self.finished = False
        self.start()
        self.failed = False

    def onHook(self, nb_blocs, taille_bloc, taille_fichier):
        self.nb_blocs = nb_blocs
        self.taille_bloc = taille_bloc
        self.taille_fichier = taille_fichier

    def download(self):
        try:
            urllib.urlretrieve(self.url, self.local, reporthook = self.onHook)
        except Exception as e:
            self.failed = True
        self.finished = True

    def run(self):
        self.download()