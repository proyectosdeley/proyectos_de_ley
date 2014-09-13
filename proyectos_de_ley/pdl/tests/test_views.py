# -*- encoding: utf-8 -*-
import json
import os
import re

from bs4 import BeautifulSoup

from django.test import Client
from django.test import TestCase

from pdl import views
from pdl.models import Proyecto, Slug


class SimpleTest(TestCase):
    def setUp(self):
        this_folder = os.path.abspath(os.path.dirname(__file__))
        dummy_db_json = os.path.join(this_folder, 'dummy_db.json')
        self.dummy_items = json.loads(open(dummy_db_json, 'r').read())
        self.maxDiff = None

    def test_index(self):
        c = Client()
        response = c.get('/')
        soup = BeautifulSoup(response.content)
        result = soup.find_all('h1')[0].get_text()
        self.assertEqual('Proyectos de Ley', result)

    def test_get_last_items(self):
        for i in self.dummy_items:
            b = Proyecto(**i)
            b.save()

        expected = '03774'
        item = views.get_last_items()[0]
        result = re.search("<b>([0-9]{5})/[0-9]{4}-CR</b>", item).groups()[0]
        self.assertEqual(expected, result)

    def test_prettify_item1(self):
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder, 'prettified_03774.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[0]

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        item = Proyecto.objects.get(codigo='03774')
        result = views.prettify_item(item)
        self.assertEqual(prettified_item, result)

    def test_prettify_item2(self):
        """Test when no pdf_url and no expediente are Blank in object."""
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder, 'prettified_03774_2.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[0]
        item['pdf_url'] = ''
        item['expediente'] = ''
        item['seguimiento_page'] = ''

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        item = Proyecto.objects.get(codigo='03774')
        result = views.prettify_item(item)
        self.assertEqual(prettified_item, result)

    def test_prettify_item_small(self):
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder,
                                       'prettified_03774_small.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[0]

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        item = Proyecto.objects.get(codigo='03774')
        result = views.prettify_item_small(item)
        self.assertEqual(prettified_item, result)

        # no PDF
        item.pdf_url = ''
        result = views.prettify_item_small(item)
        self.assertTrue('sin PDF' in result)

        # no expediente
        item.expediente = ''
        result = views.prettify_item_small(item)
        self.assertTrue('sin Expediente' in result)

        # no seguimiento_page
        item.seguimiento_page = ''
        result = views.prettify_item_small(item)
        self.assertTrue('sin Seguimiento' in result)

    def test_hiperlink_congre(self):
        expected = "<a href='/congresista/dammert_ego_aguirre/' title='ver " \
                   "todos sus proyectos'>Dammert Ego Aguirre, Manuel " \
                   "Enrique Ernesto</a>;\n" \
                   "<a href='/congresista/lescano_ancieta_yonhy/' " \
                   "title='ver todos sus proyectos'>Lescano Ancieta, " \
                   "Yonhy</a>"
        congresistas = "Dammert Ego Aguirre, Manuel Enrique Ernesto; " \
                       "Lescano Ancieta, Yonhy"
        result = views.hiperlink_congre(congresistas)
        self.assertEqual(expected, result)

    def test_convert_name_to_slug(self):
        name = 'Eguren Neuenschwander, Juan Carlos'
        expected = 'eguren_neuenschwander_juan/'
        result = views.convert_name_to_slug(name)
        self.assertEqual(expected, result)

    def test_proyecto_view(self):
        i = self.dummy_items[0]
        b = Proyecto(**i)
        b.save()

        c = Client()
        response = c.get('/p/4aw8ym/')
        soup = BeautifulSoup(response.content)
        result = soup.title.get_text().strip()
        expected = 'Proyectos de ley emitidos por el Congreso | 03774/2014-CR'
        self.assertEqual(expected, result)

    def test_about_view(self):
        c = Client()
        response = c.get('/about/')
        soup = BeautifulSoup(response.content)
        result = soup.title.get_text().strip()
        expected = 'Proyectos de ley emitidos por el Congreso de la ' \
                   'República del Perú | About'
        self.assertEqual(expected, result)

    def test_sanitize(self):
        mystring = "'/\\*%"
        expected = ''
        result = views.sanitize(mystring)
        self.assertEqual(expected, result)

    def test_find_in_db(self):
        this_folder = os.path.abspath(os.path.dirname(__file__))
        prettified_file = os.path.join(this_folder,
                                       'prettified_03774_small.txt')
        with open(prettified_file, "r") as f:
            prettified_item = f.read()
        item = self.dummy_items[0]

        # save it to test database
        b = Proyecto(**item)
        b.save()
        # now get it as QuerySet object
        items = views.find_in_db(query='03774')
        result = items[0]
        self.assertEqual(prettified_item, result)

        # find elements not in our database
        result = views.find_in_db(query='037741111111111111111111111111111')
        self.assertEqual("No se encontraron resultados.", result)

    def test_find_slug_in_db(self):
        item = self.dummy_items[0]

        slugs = []
        for i in item['congresistas'].split(';'):
            congre_slug = views.convert_name_to_slug(i)
            obj = dict(nombre=i.strip(), slug=congre_slug)
            if obj not in slugs:
                slugs.append(obj)
        for i in slugs:
            b = Slug(**i)
            b.save()

        # save it to test database
        b = Proyecto(**item)
        b.save()

        # now get it as QuerySet object
        slug = 'dammert_ego_aguirre'
        expected = 'Dammert Ego Aguirre, Manuel Enrique Ernesto'
        result = views.find_slug_in_db(slug)
        self.assertEqual(expected, result)

        # find elements not in our database
        slug = 'dammert_ego_aguirre/'
        result = views.find_slug_in_db(slug)
        self.assertEqual(expected, result)

        slug = 'dammert_ego_aguirreaaaaaaaa'
        result = views.find_slug_in_db(slug)
        self.assertEqual(None, result)

    def test_find_congresista_in_db1(self):
        item = self.dummy_items[0]
        # save it to test database
        b = Proyecto(**item)
        b.save()
        nombre = 'Dammert Ego Aguirre, Manuel Enrique Ernesto'
        result = views.find_congresista_in_db(nombre)
        self.assertTrue('03774/2014-CR' in result[0])

    def test_find_congresista_in_db2(self):
        item = self.dummy_items[0]
        # save it to test database
        b = Proyecto(**item)
        b.save()
        nombre = 'Pachecho, Yoni'
        result = views.find_congresista_in_db(nombre)
        expected = 'No se encontraron resultados.'
        self.assertEqual(expected, result)

    def test_search1(self):
        """Search attempt is redirected to index."""
        c = Client()
        response = c.get('/search/')
        self.assertEqual(302, response.status_code)

    def test_search2(self):
        """Search attempt is redirected to index."""
        query = "'*;/"
        c = Client()
        response = c.get('/search/?q=' + query)
        self.assertEqual(302, response.status_code)

    def test_search3(self):
        """Search attempt is redirected to index."""
        query = "propone"
        c = Client()
        response = c.get('/search/?q=' + query)
        self.assertEqual(200, response.status_code)
