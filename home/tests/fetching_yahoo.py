from django.test import TestCase

from logic.logic import Logic


class FetchingYahooTestCase(TestCase):


    def setUp(self):
        # Set up any initial data here, like creating stock tickers, etc.
        logic = Logic()
        self.stock_hist_bars_yahoo =  logic.service.fetching().stock_hist_bars_yahoo()

    def test_stock_hist_bars_yahoo(self):

        meta = {"initial": "true", "leftover": [], "done": []}

        # Call the StockHistBarsYahoo function.
        error_list, meta = self.stock_hist_bars_yahoo.run(meta, None, True)

        # Perform assertions based on what you expect the function to return.
        self.assertEqual(len(error_list) <= 0, True)
        self.assertTrue(True)
        # self.assertEqual(0 <= 0, True)

    def tearDown(self):
        # Clean up any necessary data after the test.
        pass

# Create your tests here.
# class ProductTestCase(TestCase):

    # def setUp(self):
    #     # Set up any initial data here, like creating stock tickers, etc.
    #     # instance = Logic()
    #     # self.stock_hist_bars_yahoo =  instance.service.fetching().stock_hist_bars_yahoo()
    #     pass

    # def test_create_product(self):
    #     StockHistBarsYahooTestCase.pull_and_save_symbol_history('AAPL', '2023-01-01', '2023-12-31')
    #     self.assertTrue(True)

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