import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import *


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
        response = self.client.post(reverse('pdv:article'), data)
        self.assertNotEqual(response.status_code, 200, 'Could create an article with empty data')
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
        response = self.client.post(reverse('pdv:article'), data)
        self.assertNotEqual(response.status_code, 200, 'Long string of data accepted as article data')
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
        response = self.client.post(reverse('pdv:article'), data)
        self.assertNotEqual(response.status_code, 200, 'Could create an article with whitespace as data')
        self.assertEqual(Article.objects.count(), 0, 'Article with whitespace as data was created in database')


    def test_acces_invalid_method(self):
        """
        Test if the client can make an invalid method request to the article creation url  
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
        response = self.client.get(reverse('pdv:article'), data)
        self.assertNotEqual(response.status_code, 200, 'A get request was acepted for an url only for post')
        self.assertEqual(Aritcle.objects.count(), 0, 'An article was created from a get http request')


class SaleClientSideTests(TestCase):
    def setUp(self):
        self.dummy_category = Category.objects.create(name='Dummy', description='Dummy category used for testing')
        self.article_a = Article.objects.create(
            name='Dummy article A',
            description='Dummy article used for tests',
            barcode='0000000000001',
            price=decimal.Decimal(10),
            purchase_price=decimal.Decimal(5),
            quantity=1,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_category,
        )
        self.article_b = Article.objects.create(
            name='Dummy article B',
            description='Dummy article used for tests',
            barcode='0000000000002',
            price=decimal.Decimal(20),
            purchase_price=decimal.Decimal(10),
            quantity=5,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_category,
        )
        self.article_c = Article.objects.create(
            name='Dummy article C',
            description='Dummy article used for tests',
            barcode='0000000000003',
            price=decimal.Decimal(30),
            purchase_price=decimal.Decimal(20),
            quantity=0,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_category,
        )
        

    def test_make_sale(self):
        """
          Test if client can make a valid sale  
        """
        sale_data = {'print':0}
        payment = 100
        total = self.article_a.price + self.article_b.price
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        sale_data['payed'] = payment
        response = self.client.post(reverse('pdv:makesale'), sale_data)
        self.assertEqual(response.status_code, 200, 'Could not make a valid sale')
        sale: Sale = None
        try:
            sale = Sale.objects.get(id=1)
        except ObjectDoesNotExist:
            self.fail('Could not create a sale in the database')
        self.assertEqual(sale.amount_payed, payment, 'Payment in the database does not match payment sent by the client')        

        sale_article_a: SingleSale = None
        sale_article_b: SingleSale = None

        try:
            sale_article_a = SingleSale.objects.get(article=self.article_a.id)
            sale_article_b = SingleSale.objects.get(article=self.article_b.id)
        except ObjectDoesNotExist:
            self.fail('Sale did not create a SingleSale object for each article sold')

        self.assertEqual(sale_article_a.quantity*sale_article_a.article.price \
            + sale_article_b.quantity*sale_article_b.article.price , total, 'Sale totals do not match')
        self.assertGreaterEqual(payment, total, 'A sale with not enough payment was created')
        self.assertEqual(sale.date, date.today(), 'Date does not match')
