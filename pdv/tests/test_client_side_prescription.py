import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from pdv.models import *


class PrescriptionClientSideTests(TestCase):
    def setUp(self):
        self.dummy_category = Category.objects.create(name='Dummy', description='Dummy category used for testing')
        self.dummy_controlled_category = Category.objects.create(name='Dummy Controlled', description='Dummy category used for testing controlled products')
        self.dummy_article = Article.objects.create(
            name='Dummy article',
            description='Dummy article used for tests',
            barcode='0000000000001',
            price=decimal.Decimal(10),
            purchase_price=decimal.Decimal(5),
            quantity=1,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_category,
        )
        self.dummy_controlled_article = Article.objects.create(
            name='Dummy controlled article',
            description='Dummy article used for tests, it must be registered when sold',
            barcode='0000000000002',
            price=decimal.Decimal(20),
            purchase_price=decimal.Decimal(10),
            quantity=5,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_controlled_category,
        )
        self.dummy_soldout_article = Article.objects.create(
            name='Dummy soldout article',
            description='Dummy article used for tests, quantity is zero',
            barcode='0000000000003',
            price=decimal.Decimal(30),
            purchase_price=decimal.Decimal(20),
            quantity=0,
            min_quantity=1,
            has_iva=False,
            category=self.dummy_category,
        )
        self.dummy_controlled_sale = Sale.objects.create(date=date.today(), amount_payed=self.dummy_controlled_article.price)
        self.dummy_single_sale = SingleSale.objects.create(quantity=1, article=self.dummy_controlled_article, sale=self.dummy_controlled_sale)
        self.dummy_medic = Medic.objects.create(name='Dummy', sur_name_a='Dummy', sur_name_b='Dummy', address='#123 Calle falsa', cedula='1234567890', ssa='1234567890')


    def test_make_prescription_total(self):
        """
          Test if the client can register a total prescription from a sale  
        """
        prescription_data = {
            'type': 'total',
            'sale': self.dummy_controlled_sale.id,
            'medic': self.dummy_medic.id,
        }
        response = self.client.post(reverse('pdv:prescriptions'), prescription_data)
        self.assertEqual(response.status_code, 200, 'Could not create a prescription')
        self.assertEqual(PrescriptionTotal.objects.count(), 1, 'Object was not created')
        prescription: PrescriptionTotal = None
        try:
            prescription = PrescriptionTotal.objects.get(pk=1)
        except ObjectDoesNotExist:
            self.fail('Could not create a PrescriptionTotal object in the database')
        self.assertEqual(prescription.sale, self.dummy_controlled_sale, 'Sales do not match')
        self.assertEqual(prescription.date, self.dummy_controlled_sale.date, 'Dates do not match')
        self.assertEqual(prescription.medic, self.dummy_medic, 'Medics do not match')


    def test_make_prescription_partial(self):
        """
          Test if the client can register a partial prescription from a sale  
        """
        prescription_data = {
            'type': 'partial',
            'sale': self.dummy_controlled_sale.id,
            'medic': self.dummy_medic.id,
        }
        response = self.client.post(reverse('pdv:prescriptions'), prescription_data)
        self.assertEqual(response.status_code, 200, 'Could not create a prescription')
        self.assertEqual(PrescriptionPartial.objects.count(), 1, 'Object was not created')
        prescription: PrescriptionPartial = None
        try:
            prescription = PrescriptionPartial.objects.get(pk=1)
        except ObjectDoesNotExist:
            self.fail('Could not create a PrescriptionTotal object in the database')
        self.assertEqual(prescription.sale, self.dummy_controlled_sale, 'Sales do not match')
        self.assertEqual(prescription.date, self.dummy_controlled_sale.date, 'Dates do not match')
        self.assertEqual(prescription.medic, self.dummy_medic, 'Medics do not match')
