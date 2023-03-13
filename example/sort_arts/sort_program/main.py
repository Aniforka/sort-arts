import os
import sys
import glob
import configparser
from PIL import Image

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PIL.ImageQt import ImageQt
from PyQt6 import QtWidgets, QtCore, QtGui, uic

class Ui(QtWidgets.QMainWindow, QtWidgets.QWidget): #класс основого интерфейса программы
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/MainWindow.ui', self)
        #self.resize(self.minimumSize())

        config = configparser.ConfigParser()
        config.read("settings.ini", encoding="utf-8")

        path = config["Default"]["path"]
        path.replace('\\\\', '/')
        path.replace('\\', '/')

        if path.endswith('/'): path = path[:-1]

        self.PATH = path

        self.authorBox.setEnabled(False)
        self.animeBox.setEnabled(False)
        self.characterBox.setEnabled(False)

        self.show()

        self.load_image()

        #self.picture.clicked.connect(self.show_picture)
        self.picture.mousePressEvent = self.show_picture

        self.sortBox.currentIndexChanged.connect(self.choose_sort)
        self.animeBox.currentIndexChanged.connect(self.choose_anime)

        self.nextButton.clicked.connect(self.next_picture)
        self.resized.connect(self.resize_window)
         

    def resizeEvent(self, event):
        self.resized.emit()

        return super(Ui, self).resizeEvent(event)

    def resize_window(self):
        self.load_image()

    def show_picture(self, event):
        img = Image.open(self.cur_image)
        img.show() 

    def load_image(self):
        images = update_images(self.PATH)

        self.cur_image = images[0]

        size = self.picture.size()
        pixmap = QtGui.QPixmap.fromImage(ImageQt(self.cur_image)).scaled(size)
        self.picture.setPixmap(pixmap)

        name = self.cur_image.split('/')[-1].split('.')[0]
        self.nameLabel.setText(name)

    def choose_sort(self, index):
        if index == 0:
            self.clear_box(self.authorBox)
            self.clear_box(self.animeBox)
            self.clear_box(self.characterBox)
            self.authorBox.setEnabled(False)
            self.animeBox.setEnabled(False)
            self.characterBox.setEnabled(False)
        elif index == 1:
            self.clear_box(self.authorBox)
            self.clear_box(self.characterBox)
            self.authorBox.setEnabled(False)
            self.animeBox.setEnabled(True)
            self.characterBox.setEnabled(False)

            animes = update_anime_folders(self.PATH)
            self.animeBox.addItems(animes)
        elif index == 2:
            self.clear_box(self.animeBox)
            self.clear_box(self.characterBox)
            self.authorBox.setEnabled(True)
            self.animeBox.setEnabled(False)
            self.characterBox.setEnabled(False)

            authors = update_authors_folders(self.PATH)
            self.authorBox.addItems(authors)
    
    def choose_anime(self, index):
        self.clear_box(self.authorBox)
        self.clear_box(self.characterBox)
        self.authorBox.setEnabled(False)
        self.animeBox.setEnabled(True)
        self.characterBox.setEnabled(True)

        animes = update_anime_folders(self.PATH)
        characters = list()
        
        for anime in animes:
            if self.animeBox.itemText(index) == anime:
                characters = update_specified_folder('/'.join((self.PATH, "sorted", anime, '/')))
                break

        self.characterBox.addItems(characters)

    def clear_box(self, box):
        box.clear()
        box.addItem("None")

    def next_picture(self):
        sort = self.sortBox.currentText()
        author = self.authorBox.currentText()
        anime = self.animeBox.currentText()
        character = self.characterBox.currentText()
        name = self.nameLabel.text() + '.' + self.cur_image.split('.')[-1]
        new_path = self.cur_image

        if sort == "authors":
            new_path = '/'.join((self.PATH, "authors", name))

            if author != "None":
                new_path = '/'.join((self.PATH, "authors", author, name))

        elif sort == "sorted":
            new_path = '/'.join((self.PATH, "sorted", name))

            if anime != "None":
                new_path = '/'.join((self.PATH, "sorted", anime, name))

                if character != "None":
                    new_path = '/'.join((self.PATH, "sorted", anime, character, name))

        os.replace(self.cur_image, new_path)
        self.clear_box(self.authorBox)
        self.clear_box(self.animeBox)
        self.clear_box(self.characterBox)
        self.authorBox.setEnabled(False)
        self.animeBox.setEnabled(False)
        self.characterBox.setEnabled(False)

        self.sortBox.setCurrentIndex(0)

        self.load_image()

def update_anime_folders(path):
    path = path + "/sorted/"
    return [file for file in os.listdir(path) if os.path.isdir(path + file)]

def update_authors_folders(path):
    path = path + "/authors/"
    return [file for file in os.listdir(path) if os.path.isdir(path + file)]

def update_specified_folder(path):
    return [file for file in os.listdir(path) if os.path.isdir(path + file)]

def update_images(path):
    root = path + "/unsorted/"
    os.chdir(root)
    types = ("*.png", "*.jpg", "*.jpeg") # the tuple of file types
    files_grabbed = []

    for files in types:
        raw_files = glob.glob(files)

        for file in raw_files:
            files_grabbed.append(root + file)

    return files_grabbed

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) #создание приложения
    window = Ui() #получение экземпляра основного интерфейса
    app.exec() #запуск основого интерфейса
    #print(update_images("T:/Programming/Python/sort_arts"))