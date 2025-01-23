import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from pdv.models import *


class ArticleClientSideTests(TestCase):
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
        response = self.client.post(reverse('pdv:CREATE_ARTICLE'), data)
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
            response = self.client.post(reverse('pdv:CREATE_ARTICLE'), data)
            self.assertEqual(Article.objects.count(), 0, f"Article with invalid data for field {field} was created")


    def test_empty_article_data(self):
        """
        Test if an article can be created from a web request whit empty data
        """
        data = {
            'name': '',
            'description': '',
            'barcode': '',
            'purchase_price': '',
            'price': '',
            'quantity': '',
            'min_quantity': '',
            'has_iva': '',
            'category': '',
        }
        response = self.client.post(reverse('pdv:CREATE_ARTICLE'), data)
        self.assertEqual(Article.objects.count(), 0, 'Article with empty data was created in database')


    def test_long_string_article_data(self):
        """
        Test client sending long strings as article data
        """
        long_garbage_string = \
            10*'°ad6af76874ñ+42ñ+ad+ñ"!°0jad9fu8a9dfyhq0efy024e8fqwocdæđæøðđøæßðđſæer\'0q()=)(DF)A(DF\'?={}//)?(/=QEW)"#°!#"!4e8h2084yh10ih13#$"!"$#ASGAqERQWERfadfa9dfa9v9aa\'!$#!$Ñ"P#%R ?¡"QEFPWEF0qw0fv¿\'wq¿v0dfi'
        data = {
            'name': long_garbage_string,
            'description': long_garbage_string,
            'barcode': long_garbage_string,
            'purchase_price': long_garbage_string,
            'price': long_garbage_string,
            'quantity': long_garbage_string,
            'min_quantity': long_garbage_string,
            'has_iva': long_garbage_string,
            'category': long_garbage_string,
        }
        response = self.client.post(reverse('pdv:CREATE_ARTICLE'), data)
        self.assertEqual(Article.objects.count(), 0, 'Article with empty data was created in database')

    
    def test_blank_article_data(self):
        """
        Test if an article can be created from a web request with witespase as data
        """
        data = {
            'name': ' \t\n  \r ',
            'description': ' \t\n  \r ',
            'barcode': ' \t\n  \r ',
            'purchase_price': ' \t\n  \r ',
            'price': ' \t\n  \r ',
            'quantity': ' \t\n  \r ',
            'min_quantity': ' \t\n  \r ',
            'has_iva': ' \t\n  \r ',
            'category': ' \t\n  \r ',
        }
        response = self.client.post(reverse('pdv:CREATE_ARTICLE'), data)
        self.assertEqual(Article.objects.count(), 0, 'Article with whitespace as data was created in database')

