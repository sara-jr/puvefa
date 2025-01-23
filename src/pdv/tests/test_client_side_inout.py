import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from pdv.models import *
from pdv.settings import CONTROLLED_CATEGORY_NAME


class ArticleInOutClientSideTests(TestCase):
    def setUp(self):
        self.dummy_category = Category.objects.create(name='Dummy', description='Dummy category used for testing')
        self.dummy_article = Article.objects.create(name='Dummy article', barcode='zbc123456789', purchase_price=10, price=20, quantity=10, min_quantity=1, has_iva=True, category=self.dummy_category)
        self.dummy_controlled_article = Article.objects.create(name='Dummy controlled article', barcode='ybc123456789', purchase_price=10, price=20, quantity=10, min_quantity=1, has_iva=True, category=self.dummy_category, controlled=True)
        

    def test_article_inout(self):
        """
        Test the article inout page
        """
        data ={
            'id':self.dummy_article.id,
            'add':'on',
            'delta':1,
        }
        quantity = self.dummy_article.quantity
        response = self.client.post(reverse('pdv:ARTICLE_ALTER_QUANTITY'), data)
        self.dummy_article.refresh_from_db()
        self.assertEqual(self.dummy_article.quantity, quantity + 1, 'Article quantity was not incremented correctly')
        del data['add']
        quantity = self.dummy_article.quantity
        response = self.client.post(reverse('pdv:ARTICLE_ALTER_QUANTITY'), data)
        self.dummy_article.refresh_from_db()
        self.assertEqual(self.dummy_article.quantity, quantity - 1, 'Article quantity was not decremented correctly')


    def test_controlled_article_inout(self):
        """
        Test the article inout page
        """
        data ={
            'id':self.dummy_controlled_article.id,
            'add':'on',
            'delta':1,
        }
        quantity = self.dummy_controlled_article.quantity
        response = self.client.post(reverse('pdv:ARTICLE_ALTER_QUANTITY'), data)
        self.dummy_controlled_article.refresh_from_db()
        self.assertEqual(self.dummy_controlled_article.quantity, quantity + 1, 'Article quantity was not incremented correctly')
        self.assertEqual(ControlledArticleInOut.objects.count(), 1, 'ControlledInOut was not created')
        inout = ControlledArticleInOut.objects.all()[0]
        self.assertEqual(inout.delta, 1, 'ControlledInOut delta was not registered correctly')
        del data['add']
        quantity = self.dummy_controlled_article.quantity
        response = self.client.post(reverse('pdv:ARTICLE_ALTER_QUANTITY'), data)
        self.dummy_controlled_article.refresh_from_db()
        self.assertEqual(self.dummy_controlled_article.quantity, quantity - 1, 'Article quantity was not decremented correctly')
        self.assertEqual(ControlledArticleInOut.objects.count(), 2, 'ControlledInOut was not created')
        inout = ControlledArticleInOut.objects.all()[1]
        self.assertEqual(inout.delta, -1, 'ControlledInOut delta was not registered correctly')
