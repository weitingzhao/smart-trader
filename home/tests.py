from django.test import TestCase
from home.tests import test_api


# Create your tests here.
class ProductTestCase(TestCase):

    def test_create_product(self):
        test_api.pull_and_save_symbol_history('AAPL', '2023-01-01', '2023-12-31')
        self.assertTrue(True)

    # def test_create_product(self):
    #     product = Product.objects.create(name="Test Product", price=10.99)
    #     self.assertEqual(product.name, "Test Product")
    #     self.assertEqual(product.price, 10.99)
    #     self.assertTrue(product.is_available)
    #
    # def test_update_product(self):
    #     product = Product.objects.create(name="Test Product", price=10.99)
    #     product.price = 15.99
    #     product.save()
    #     updated_product = Product.objects.get(pk=product.pk)
    #     self.assertEqual(updated_product.price, 15.99)
    #
    # def test_delete_product(self):
    #     product = Product.objects.create(name="Test Product", price=10.99)
    #     product.delete()
    #     with self.assertRaises(Product.DoesNotExist):
    #         Product.objects.get(pk=product.pk)



