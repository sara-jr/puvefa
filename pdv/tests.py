import decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Article, Category


class BasicTestCases(TestCase):
    def setUp(self):
        self.dummy_category = Category.objects.create(name='Dummy', description='Dummy category used for testing')

    def test_create_article(self):
        """
        Test if an article can be created from a web request whit the correct data      
        """
        data = {
            'name':'Test Article 1',
            'description':'A dummy article made for testing',
            'barcode':'1234567890',
            'purchase_price':'100',
            'price':'200',
            'quantity':'10',
            'min_quantity':'5',
            'has_iva':'1',
            'category':'1',
        }
        response = self.client.post(reverse('pdv:article'), data)
        self.assertEqual(response.status_code, 200, 'Could not create an article')
        article: Article = None
        try:
            article = Article.objects.get(barcode=data['barcode'])
        except ObjectDoesNotExist:
            self.fail('Article data was posted but it was not created in the database')
        self.assertEqual(article.name, data['name'], 'Name does not match')
        self.assertEqual(article.description, data['description'], 'Description does not match')
        self.assertEqual(article.barcode, data['barcode'], 'Barcode does not match')
        self.assertEqual(article.purchase_price, decimal.Decimal(data['purchase_price']), 'Purchase price does not match')
        self.assertEqual(article.price, decimal.Decimal(data['price']), 'Price does not match')
        self.assertEqual(article.quantity, int(data['quantity']), 'Quantity does not match')
        self.assertEqual(article.min_quantity, int(data['min_quantity']), 'Min Quantity does not match')
        self.assertEqual(article.has_iva, bool(data['has_iva']), 'Has IVA does not match')
        self.assertEqual(article.category, self.dummy_category, 'Category does not match')


    def test_create_invalid_article(self):
        """
        Test if an article with invalid data can be created from a web request 
        """
        valid_data = {
            'name':'Test Article 1',
            'description':'A dummy article made for testing',
            'barcode':'a very very very very very long barcode that should not be valid in the database<',
            'purchase_price':'100',
            'price':'200',
            'quantity':'10',
            'min_quantity':'5',
            'has_iva':'1',
            'category':'1',
        }
        invalid_data = {
            'name':'',
            'description':'This article should not be in the database',
            'barcode':'1234567890',
            'purchase_price':'-100',
            'price':'0',
            'quantity':'-10',
            'min_quantity':'-5',
            'has_iva':'',
            'category':'-1',
        }
        for field, value in invalid_data.items():
            data = valid_data
            data[field] = value
            response = self.client.post(reverse('pdv:article'), data)
            self.assertNotEqual(response.status_code, 200, 'Invalid data for an Article was acepted created')
            self.assertEqual(Article.objects.count(), 0, f"Article with invalid data for field {field} was created")


