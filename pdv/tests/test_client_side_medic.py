import decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from pdv.models import *


class MedicClientSideTests(TestCase):
    def test_post_medic(self):
        medic_data = {
            'name': 'Dummy',
            'sur_name_a': 'Dummy',
            'sur_name_b': 'Dummy',
            'address': 'Dummy #123',
            'cedula': 1234567890,
            'ssa': 1234567890,
        }
        response = self.client.post(reverse('pdv:medics'), medic_data)
        self.assertEqual(200, response.status_code, 'Server did not accepted the data')
        medic: Medic = None
        try:
            medic = Medic.objects.get(name='Dummy')
        except ObjectDoesNotExist:
            self.fail('Medic was not created in the database')
        
        self.assertEqual(medic.name, medic_data['name'], f"Field name does not match")
        self.assertEqual(medic.sur_name_a, medic_data['sur_name_a'], f"Field sur_name_a does not match")
        self.assertEqual(medic.sur_name_b, medic_data['sur_name_b'], f"Field sur_name_b does not match")
        self.assertEqual(medic.address, medic_data['address'], f"Field address does not match")
        self.assertEqual(medic.cedula, medic_data['cedula'], f"Field cedula does not match")
        self.assertEqual(medic.ssa, medic_data['ssa'], f"Field ssa does not match")


    def test_empty_medic(self):
        medic_data = {
            'name': '',
            'sur_name_a': '',
            'sur_name_b': '',
            'address': '',
            'cedula': '',
            'ssa': '',
        }
        response = self.client.post(reverse('pdv:medics'), medic_data)
        self.assertNotEqual(200, response.status_code, 'Server did accepted the data')
        self.assertEqual(0, Medic.objects.count(), 'Medic object was created in the database')
