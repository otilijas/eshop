from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import Product, ProductRating, Order, CartItem


class ProductGetTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.product = baker.make(Product, category="other", _quantity=3)
        self.ratings = baker.make(ProductRating, product=self.product[1], _quantity=5)
        self.url = reverse("product-list")

    def test_get_products_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertIsInstance(response.data, object)

    def test_get_product_detail(self):
        url = reverse("product-detail", kwargs={"pk": self.product[1].id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.product[1].name)
        self.assertEqual(len(response.data["ratings"]), 5)

    def test_get_nonexistent_product(self):
        url = reverse("product-detail", kwargs={"pk": 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_filter_category(self):
        response = self.client.get(reverse("product-list"), {"category": "other"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), 3)

    def test_get_filter_category_not_found(self):
        response = self.client.get(reverse("product-list"), {"category": "hair"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), 0)

    def test_get_filter_name(self):
        response = self.client.get(reverse("product-list"), {"name": self.product[0].name})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), 1)

    def test_get_search_name(self):
        response = self.client.get(reverse("product-list"), {"search": self.product[0].name[:3]})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), 1)

    def test_ratings(self):
        product_2 = baker.make(Product)
        baker.make(ProductRating, product=product_2, rating=5)
        baker.make(ProductRating, product=product_2, rating=3)
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.data[-1]["rating"], 4)


class ProductRatingPostTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.user = User(email="foo@bar.com")
        password = "some_password"  # noqa: S105
        self.user.set_password(password)
        self.user.save()
        self.product = baker.make(Product)
        self.productrating = baker.make(ProductRating)

        self.url = reverse("rating-list")

    def _get_data(self, rating=5):
        data = {
            "product": self.product.id,
            "rating": rating,
            "comment": "Nice"
        }
        return data

    def test_successful_product_rating_create(self):
        self.client.force_authenticate(self.user)
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductRating.objects.count(), 2)
        self.assertEqual(response.data["user"], self.user.id)

    def test_unauthorized_product_rating_create(self):
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_rating_greater_than_max_allowed_value(self):
        data = self._get_data(rating=10)
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ensure this value is less than or equal to 5", response.data["rating"][0])

    def test_invalid_rating_less_than_min_allowed_value(self):
        data = self._get_data(rating=0)
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ensure this value is greater than or equal to 1", response.data["rating"][0])

    def test_already_existing_product_rating_create(self):
        self.client.force_authenticate(self.user)
        baker.make(ProductRating, product=self.product, user=self.user)
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Product already has been rated!", response.data["non_field_errors"][0])


class OrdersGetTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("username", "password")
        self.order = baker.make(Order, user=self.user, _quantity=3)
        self.order_2 = baker.make(Order)
        self.url = reverse("order-list")

    def test_get_not_authenticated_user_orders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_orders(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        orders_count = Order.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["user"], self.user.id)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(orders_count, 4)


class OrderPostTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = User(email="foo@bar.com", first_name="Test")
        password = "some_password"  # noqa: S105
        self.user.set_password(password)
        self.user.save()
        self.product = baker.make(Product)
        self.cartitems = baker.make(CartItem, product=self.product, price=10, quantity=2, user=self.user)

        self.url = reverse("order-list")

    def _get_data(self):
        data = {
            "paid": True,
        }
        return data

    def test_successful_order_create(self):
        self.client.force_authenticate(self.user)
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], self.user.first_name)
        self.assertEqual(len(response.data["ordered_items"]), 1)
        self.assertEqual(response.data["total_amount"], 20.00)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_unauthorized_order_create(self):
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CartItemGetTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.user = User(email="foo@bar.com", first_name="Test")
        password = "some_password"  # noqa: S105
        self.user.set_password(password)
        self.user.save()
        self.cart = baker.make(CartItem, user=self.user, _quantity=5)

        self.url = reverse("cart-list")

    def test_get_user_cart_items(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 5)


class CartItemPostTests(APITestCase):

    def setUp(self):
        super().setUp()
        self.user = User(email="foo@bar.com", first_name="Test")
        password = "some_password"  # noqa: S105
        self.user.set_password(password)
        self.user.save()
        self.product = baker.make(Product, price=10)

        self.url = reverse("cart-list")

    def _get_data(self):
        data = {
            "product": self.product.id,
            "quantity": 2,
        }
        return data

    def test_successful_add_to_cart(self):
        self.client.force_authenticate(self.user)
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["price"], self.product.price)

    def test_item_quantity_updated(self):
        self.client.force_authenticate(self.user)
        self.cart = baker.make(CartItem, user=self.user, product=self.product, price=10, quantity=2)
        data = self._get_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.data["quantity"], 4)
