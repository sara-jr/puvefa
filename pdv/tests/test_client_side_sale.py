import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from pdv.models import *
from pdv.settings import CONTROLLED_CATEGORY_NAME


class SaleClientSideTests(TestCase):
    def setUp(self):
        self.dummy_category = Category.objects.create(name='Dummy', description='Dummy category used for testing')
        self.dummy_controlled_category = Category.objects.create(name=CONTROLLED_CATEGORY_NAME, description='Dummy category used for testing')
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
        self.controlled_article = Article.objects.create(
            name='Dummy controlled article',
            description='Dummy article used for tests',
            barcode='0000000000004',
            price=decimal.Decimal(30),
            purchase_price=decimal.Decimal(20),
            quantity=1,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_controlled_category,
        )


    def test_make_sale(self):
        """
          Test if client can make a valid sale  
        """
        sale_data = {
            'payed': 100,
            'print': 0
        }
        total = self.article_a.price + self.article_b.price
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        quantity_a_afther_sale = self.article_a.quantity - 1
        quantity_b_afther_sale = self.article_b.quantity - 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        sale: Sale = None
        try:
            sale = Sale.objects.get(id=1)
        except ObjectDoesNotExist:
            self.fail('Could not create a sale in the database')
        self.assertEqual(sale.amount_payed, sale_data['payed'], 'Payment in the database does not match payment sent by the client')        

        sale_article_a: SingleSale = None
        sale_article_b: SingleSale = None

        try:
            sale_article_a = SingleSale.objects.get(article=self.article_a.id)
            sale_article_b = SingleSale.objects.get(article=self.article_b.id)
        except ObjectDoesNotExist:
            self.fail('Sale did not create a SingleSale object for each article sold')

        self.assertEqual(sale_article_a.quantity*sale_article_a.article.price \
            + sale_article_b.quantity*sale_article_b.article.price , total, 'Sale totals do not match')
        self.assertGreaterEqual(sale_data['payed'], total, 'A sale with not enough payment was created')
        self.assertEqual(timezone.localdate(sale.date), date.today(), 'Date does not match')
        self.article_a.refresh_from_db(None, ['quantity'])
        self.article_b.refresh_from_db(None, ['quantity'])
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
        quantity_a = self.article_a.quantity
        quantity_b = self.article_b.quantity
        quantity_c = self.article_c.quantity
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertEqual(Sale.objects.count(), 0, 'A sale was created in the database')
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale was created from empty data')
        self.article_a.refresh_from_db(None, ['quantity'])
        self.article_b.refresh_from_db(None, ['quantity'])
        self.article_c.refresh_from_db(None, ['quantity'])
        self.assertEqual(quantity_a, self.article_a.quantity, 'Article quantity was altered from an empty sale')
        self.assertEqual(quantity_b, self.article_b.quantity, 'Article quantity was altered from an empty sale')
        self.assertEqual(quantity_c, self.article_c.quantity, 'Article quantity was altered from an empty sale')

    
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
        self.assertEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale object was created in the database')        
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
        self.assertEqual(Sale.objects.count(), 0, 'A sale object was created in the database')
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale object was created in the database')
        self.assertEqual(self.article_a.quantity, quantity_before_sell, 'The quantity for the oversell article was changed after a sale')


    def test_make_unpayed_sale(self):
        """
          Test if the client can make a sale with not enough payment  
        """
        total = self.article_a.price + self.article_b.price
        sale_data = {'print':0, 'payed':0.0}
        quantity_a_before_sale = self.article_a.quantity
        quantity_b_before_sale = self.article_b.quantity        
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale object was created in the database')        
        self.assertEqual(self.article_a.quantity, quantity_a_before_sale, 'Article quantity was altered')
        self.assertEqual(self.article_b.quantity, quantity_b_before_sale, 'Article quantity was altered')


    def test_make_negative_payment_sale(self):
        """
          Test if the client can make a sale with negative payment  
        """
        total = self.article_a.price + self.article_b.price
        sale_data = {'print':0, 'payed':-1_000.0}
        quantity_a_before_sale = self.article_a.quantity
        quantity_b_before_sale = self.article_b.quantity        
        sale_data[self.article_a.id] = 1
        sale_data[self.article_b.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale object was created in the database')        
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
        self.assertEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale object was created in the database')        


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
        self.assertEqual(Sale.objects.count(), 0, 'A sale object was created in the database')        
        self.assertEqual(SingleSale.objects.count(), 0, 'A single sale object was created in the database')        
        self.assertEqual(quantity_a_before_sale, self.article_a.quantity, 'Article quantity was altered')
        self.assertEqual(quantity_b_before_sale, self.article_b.quantity, 'Article quantity was altered')


    def test_controlled_inout_sale(self):
        sale_data = {'print':0, 'payed':30}
        sale_data[self.controlled_article.id] = 1
        response = self.client.post(reverse('pdv:MAKESALE'), sale_data)
        self.assertEqual(Sale.objects.count(), 1, 'A sale object was not created')
        self.assertEqual(ControlledArticleInOut.objects.count(), 1, 'The controlled article out was not created')
        controlled_inout = ControlledArticleInOut.objects.all()[0]
        self.assertEqual(controlled_inout.delta, -1, 'The inout delta was not registered correctly')
        self.controlled_article.refresh_from_db()
        self.assertEqual(self.controlled_article.quantity, 0, 'The sale did not decrement the article quantity')
