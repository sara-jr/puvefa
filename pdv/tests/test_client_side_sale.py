import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from pdv.models import *


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
        quantity_a_afther_sale = self.article_a.quantity - 1
        quantity_b_afther_sale = self.article_b.quantity - 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
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
        self.assertEqual(self.article_a.quantity, quantity_a_afther_sale, 'Article quantity did not change afther sale')
        self.assertEqual(self.article_b.quantity, quantity_b_afther_sale, 'Article quantity did not change afther sale')


    def test_make_sale_no_items(self):
        """
          Test if client can make a sale with no items
        """
        sale_data = {
            'print': 0,
            'payed': 0,
        }        
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'Could not make a valid sale')

        self.assertEqual(Article.objects.count(), 0, 'A sale was created from empty data')
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale was created from empty data')

    
    def test_make_soldout_sale(self):
        """
          Test if client can make a sale with soldout articles
        """
        sale_data = {
            'print': 0,
            'payed': 200.0,
        }        
        sale_data[self.article_a.id] = 1
        sale_data[self.article_c.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'Could make a sale with soldout items')
        self.assertNotEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertNotEqual(SaleSingleSale.objects.count(), 0, 'A single sale object was created in the database')        
        self.assertEqual(self.article_c.quantity, 0, 'The quantity for a soldout article was changed after a sale')

    
    def test_make_oversell_sale(self):
        """
          Test if client can make a sale with an article oversold
        """
        sale_data = {
            'print': 0,
            'payed': 200.0,
        }        
        sale_data[self.article_a.id] = 2
        quantity_before_sell = self.article_a.quantity
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'Could make a sale with an article oversold')
        self.assertNotEqual(Sale.objects.count(), 0, 'A sale object was created in the database')
        self.assertNotEqual(SaleSingleSale.objects.count(), 0, 'A single sale object was created in the database')
        self.assertEqual(self.article_a.quantity, quantity_before_sell, 'The quantity for the oversell article was changed after a sale')


    def test_make_unpayed_sale(self):
        """
          Test if the client can make a sale with not enough payment  
        """
        total = self.article_a.price + self.article_b.price
        sale_data = {'print':0, 'payment':0.0}
        quantity_a_before_sale = self.article_a.quantity
        quantity_b_before_sale = self.article_b.quantity        
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'Sale data without payment was accepted')
        self.assertNotEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertNotEqual(SaleSingleSale.objects.count(), 0, 'A single sale object was created in the database')        
        self.assertEqual(self.article_a.quantity, quantity_a_before_sale, 'Article quantity was altered')
        self.assertEqual(self.article_b.quantity, quantity_b_before_sale, 'Article quantity was altered')


    def test_make_negative_payment_sale(self):
        """
          Test if the client can make a sale with negative payment  
        """
        total = self.article_a.price + self.article_b.price
        sale_data = {'print':0, 'payment':-1_000.0}
        quantity_a_before_sale = self.article_a.quantity
        quantity_b_before_sale = self.article_b.quantity        
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'Sale data without payment was accepted')
        self.assertNotEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertNotEqual(SaleSingleSale.objects.count(), 0, 'A single sale object was created in the database')        
        self.assertEqual(self.article_a.quantity, quantity_a_before_sale, 'Article quantity was altered')
        self.assertEqual(self.article_b.quantity, quantity_b_before_sale, 'Article quantity was altered')


    def test_make_invalid_sale(self):
        """
            Test if the clien can make a sale with invalid data  
        """
        sale_data = {
            'print': '2',
            'payed': '',
            39: 4, # Articulo inexistente
        }        
        sale_data[self.article_a.id] = -1 # Cantidad invalida para un articulo
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'Server procesed invalid data for a sale')
        self.assertEqual(Sale.objects.count(), 0, 'Sale was created in the database')
        self.assertEqual(SingleSale.objects.count(), 0, 'SingleSale object was created in the database')


    def test_payment_overflow_sale(self):
        """
          Test if the client can make a sale with a big quantity as payment  
        """
        total = self.article_a.price + self.article_b.price
        sale_data = {'print':0, 'payed':999_999_999_999_999_999_999_999_999}
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'A very large payment was accepted from the server')
        self.assertNotEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertNotEqual(SaleSingleSale.objects.count(), 0, 'A single sale object was created in the database')        


    def test_quantity_overflow_sale(self):
        """
          Test if the client can make a sale with a big article quantity
        """
        total = self.article_a.price + self.article_b.price
        sale_data = {'print':0, 'payed':1000.00}
        quantity_a_before_sale = self.article_a.quantity
        quantity_b_before_sale = self.article_b.quantity
        sale_data[self.article_a.id] = 999_999_999_999_999_999_999_999_999
        sale_data[self.article_b.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertNotEqual(response.status_code, 200, 'A very large payment was accepted from the server')
        self.assertNotEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertNotEqual(SaleSingleSale.objects.count(), 0, 'A single sale object was created in the database')        
        self.assertEqual(quantity_a_before_sale, self.article_a.quantity, 'Article quantity was altered')
        self.assertEqual(quantity_b_before_sale, self.article_b.quantity, 'Article quantity was altered')
