from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from pdv.models import Article, Category


class ImportExportTests(TestCase):
    """
    Pruebas para la importacion y exportacion de datos a formatos como json
    """
    def setUp(self):
        self.category = Category.objects.create(name='Dummy', description='')
        self.article_1 = Article.objects.create(
                name='Dummy Article 1', barcode='00000000001', category=self.category,
                controlled=False, has_iva=False,
                price=Decimal('10.0'), purchase_price=Decimal('5.0'),
                quantity=10, min_quantity=4
        )
        self.article_2 = Article.objects.create(
                name='Dummy Article 2', barcode='00000000002', category=self.category,
                controlled=False, has_iva=False,
                price=Decimal('20.0'), purchase_price=Decimal('10.0'),
                quantity=20, min_quantity=6
        )


    def test_export_article(self):
        """
        Probar que no se produzcan errores al exportar los articulos
        """
        response = self.client.get(reverse('pdv:ARTICLE_EXPORT_JSON_FILE'))
        self.assertEquals(response.status_code, 200, 'No se pudieron exportar los articulos a JSON')


    def test_import_duplicated_articles(self):
        """
        Probar que no se creen articulos duplicados al importar
        """
        response = self.client.get(reverse('pdv:ARTICLE_EXPORT_JSON_FILE'))
        self.assertEquals(response.status_code, 200, 'No se pudieron exportar los articulos a JSON')
        json_file = SimpleUploadedFile('json_articles.json', response.content, content_type='application/json')
        response = self.client.post(reverse('pdv:ARTICLE_IMPORT_JSON_FILE'), data={'json_file': json_file})
        self.assertEquals(response.status_code, 302, 'No se pudieron importar los articulos a JSON')
        self.assertEquals(Article.objects.count(), 2, 'Cantidad de articulos alterada')


    def test_import_new_article(self):
        """
        Probar que se cree un articulo nuevo correctamente
        """
        jsonstring = b"""
        [
            {
                "name": "New article",
                "barcode": "0000003",
                "price": "20.00",
                "purchase_price": "15.00",
                "quantity": 2,
                "min_quantity": 1,
                "has_iva": false,
                "controlled": false,
                "category": "Dummy"
            }
        ]
        """
        json_file = SimpleUploadedFile('json_articles.json', jsonstring, content_type='application/json')
        response = self.client.post(reverse('pdv:ARTICLE_IMPORT_JSON_FILE'), data={'json_file': json_file})
        self.assertEquals(response.status_code, 302, 'No se pudieron importar los articulos a JSON')
        self.assertEquals(Article.objects.count(), 3, 'No se creó el artículo nuevo')
        article = Article.objects.get(name='New article')
        self.assertEquals(article.barcode, '0000003', 'No coinicide el código de barras')
        self.assertEquals(article.quantity, 2, 'No coinicide la cantidad')
        self.assertEquals(article.min_quantity, 1, 'No coinicide la cantidad minima')
        self.assertEquals(article.category, self.category, 'No coinicide la categoria')
        self.assertEquals(article.controlled, False, 'No coinicide controlado')
        self.assertEquals(article.has_iva, False, 'No coinicide el iva')
        self.assertEquals(article.price, 20, 'No coinicide el precio de venta')
        self.assertEquals(article.purchase_price, 15, 'No coinicide el precio de compra')



    def test_import_new_category(self):
        """
        Probar que se cree una categoria cuando la categoria del nuevo articulo no existe
        """
        jsonstring = b"""
        [
            {
                "name": "New article",
                "barcode": "0000003",
                "price": "20.00",
                "purchase_price": "15.00",
                "quantity": 2,
                "min_quantity": 1,
                "has_iva": false,
                "controlled": false,
                "category": "New Category"
            }
        ]
        """
        json_file = SimpleUploadedFile('json_articles.json', jsonstring, content_type='application/json')
        response = self.client.post(reverse('pdv:ARTICLE_IMPORT_JSON_FILE'), data={'json_file': json_file})
        self.assertEquals(response.status_code, 302, 'No se pudieron importar los articulos a JSON')
        self.assertEquals(Article.objects.count(), 3, 'No se creó el artículo nuevo')
        self.assertEquals(Category.objects.count(), 2, 'No se creó la categoria')
        category = Category.objects.get(name='New Category')
        article = Article.objects.get(name='New article')
        self.assertEquals(category, article.category, 'No coinicide la categoria')


    def test_import_bad_article(self):
        """
        Probar que no se cree un articulo nuevo si los datos no son correctos
        """
        jsonstring = b"""
        [
            {
                "name": "New article",
                "barcode": 12351,
                "price": "-20.00",
                "quantity": 2,
                "min_quantity": 1,
                "has_iva":  "asdf",
                "controlled": false
            }
        ]
        """
        json_file = SimpleUploadedFile('json_articles.json', jsonstring, content_type='application/json')
        response = self.client.post(reverse('pdv:ARTICLE_IMPORT_JSON_FILE'), data={'json_file': json_file})
        self.assertEquals(Article.objects.count(), 2, 'Se creó un artículo invalido')
