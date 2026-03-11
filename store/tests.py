from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from store.models import Product, Cart, CartItem, Order, OrderItem
from store.services.account import register_user, login_user
from store.services.cart import (
    add_product_to_cart,
    decrease_product_from_cart,
    increase_product_from_cart,
    remove_product_from_cart,
    update_product_quantity,
)
from store.services.order import checkout


# ══════════════════════════════════════════════════════════════
# HELPERS
# Funções auxiliares reutilizadas em vários testes.
# São como ingredientes pré-preparados na cozinha — você não
# corta a cebola do zero toda vez que precisar dela.
# ══════════════════════════════════════════════════════════════

def make_product(name="Camiseta", price=Decimal("49.90"), stock=10):
    """Creates and returns a Product for use in tests."""
    return Product.objects.create(
        name=name,
        description="Descrição do produto",
        price=price,
        stock=stock,
    )


def make_user(username="testuser", password="senha123"):
    """Creates and returns a regular User for use in tests."""
    return User.objects.create_user(username=username, password=password)


def make_cart(session_key="test-session-key"):
    """Creates and returns a Cart for use in tests."""
    return Cart.objects.create(session_key=session_key)


# ══════════════════════════════════════════════════════════════
# ACCOUNT SERVICES
# Testa as regras de negócio de registro e login.
# Não precisamos de request real — usamos um objeto falso (None)
# porque o service só usa o request no login() do Django.
# ══════════════════════════════════════════════════════════════

class RegisterUserServiceTest(TestCase):

    def test_register_success(self):
        """
        A valid registration should create a user and return success=True.
        """
        result = register_user(None, "joao", "joao@email.com", "senha123", "senha123")

        self.assertTrue(result["success"])
        self.assertTrue(User.objects.filter(username="joao").exists())

    def test_register_passwords_dont_match(self):
        """
        When passwords don't match, no user should be created and error should be returned.
        Like filling a form with two different passwords — the system must reject it.
        """
        result = register_user(None, "joao", "joao@email.com", "senha123", "outrasenha")

        self.assertFalse(result["success"])
        self.assertIn("senhas", result["error"].lower())
        self.assertFalse(User.objects.filter(username="joao").exists())

    def test_register_duplicate_username(self):
        """
        When a username is already taken, registration should fail.
        Like trying to create a second account with the same CPF.
        """
        make_user(username="joao")

        result = register_user(None, "joao", "outro@email.com", "senha123", "senha123")

        self.assertFalse(result["success"])
        self.assertIn("usuário", result["error"].lower())
        self.assertEqual(User.objects.filter(username="joao").count(), 1)


# ══════════════════════════════════════════════════════════════
# CART SERVICES
# Testa as regras de negócio do carrinho.
# Cada teste começa do zero (banco limpo) — o Django garante isso.
# ══════════════════════════════════════════════════════════════

class CartServiceTest(TestCase):

    def setUp(self):
        """
        setUp runs before each test method.
        Like setting the table before every meal — always fresh.
        """
        self.product = make_product()
        self.session_key = "session-abc123"

    def test_add_product_creates_cart_item(self):
        """
        Adding a product to an empty cart should create a CartItem with quantity=1.
        """
        add_product_to_cart(self.session_key, self.product.id)

        item = CartItem.objects.get(cart__session_key=self.session_key, product=self.product)
        self.assertEqual(item.quantity, 1)

    def test_add_same_product_increases_quantity(self):
        """
        Adding the same product twice should increase quantity to 2, not create two items.
        Like scanning the same item twice at a self-checkout — it adds to the count.
        """
        add_product_to_cart(self.session_key, self.product.id)
        add_product_to_cart(self.session_key, self.product.id)

        item = CartItem.objects.get(cart__session_key=self.session_key, product=self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(CartItem.objects.filter(cart__session_key=self.session_key).count(), 1)

    def test_increase_cart_item(self):
        """
        Increasing a cart item should add 1 to its quantity.
        """
        add_product_to_cart(self.session_key, self.product.id)
        increase_product_from_cart(self.session_key, self.product.id)

        item = CartItem.objects.get(cart__session_key=self.session_key, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_decrease_cart_item(self):
        """
        Decreasing a cart item with quantity > 1 should subtract 1.
        """
        add_product_to_cart(self.session_key, self.product.id)
        add_product_to_cart(self.session_key, self.product.id)  # quantity = 2
        decrease_product_from_cart(self.session_key, self.product.id)

        item = CartItem.objects.get(cart__session_key=self.session_key, product=self.product)
        self.assertEqual(item.quantity, 1)

    def test_decrease_cart_item_removes_when_quantity_is_one(self):
        """
        Decreasing a cart item with quantity=1 should remove the item entirely.
        Like removing the last unit of a product from the cart.
        """
        add_product_to_cart(self.session_key, self.product.id)  # quantity = 1
        decrease_product_from_cart(self.session_key, self.product.id)

        exists = CartItem.objects.filter(
            cart__session_key=self.session_key,
            product=self.product
        ).exists()
        self.assertFalse(exists)

    def test_remove_product_from_cart(self):
        """
        Removing a product should delete the CartItem completely regardless of quantity.
        """
        add_product_to_cart(self.session_key, self.product.id)
        add_product_to_cart(self.session_key, self.product.id)  # quantity = 2
        remove_product_from_cart(self.session_key, self.product.id)

        exists = CartItem.objects.filter(
            cart__session_key=self.session_key,
            product=self.product
        ).exists()
        self.assertFalse(exists)

    def test_update_product_quantity(self):
        """
        Updating quantity should set it to the exact value given.
        """
        add_product_to_cart(self.session_key, self.product.id)
        update_product_quantity(self.session_key, self.product.id, 5)

        item = CartItem.objects.get(cart__session_key=self.session_key, product=self.product)
        self.assertEqual(item.quantity, 5)

    def test_update_quantity_to_zero_removes_item(self):
        """
        Setting quantity to 0 should remove the item from the cart.
        """
        add_product_to_cart(self.session_key, self.product.id)
        update_product_quantity(self.session_key, self.product.id, 0)

        exists = CartItem.objects.filter(
            cart__session_key=self.session_key,
            product=self.product
        ).exists()
        self.assertFalse(exists)


# ══════════════════════════════════════════════════════════════
# ORDER SERVICES
# Testa o fluxo de checkout — a regra de negócio mais crítica.
# ══════════════════════════════════════════════════════════════

class CheckoutServiceTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.product = make_product(price=Decimal("99.90"))
        self.session_key = "session-checkout"

    def test_checkout_empty_cart_fails(self):
        """
        Checking out with an empty cart should return success=False.
        Like trying to pay for nothing at a cashier — the system must block it.
        """
        result = checkout(self.session_key, self.user)

        self.assertFalse(result["success"])
        self.assertIn("vazio", result["error"].lower())

    def test_checkout_success_creates_order(self):
        """
        A successful checkout should create an Order with the correct user.
        """
        add_product_to_cart(self.session_key, self.product.id)

        result = checkout(self.session_key, self.user)

        self.assertTrue(result["success"])
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)

    def test_checkout_creates_order_items_with_locked_price(self):
        """
        The OrderItem price should be locked at the product's price at checkout time.
        Even if the product price changes later, the order must reflect the original price.
        Like a receipt — it freezes the price at the moment of purchase.
        """
        add_product_to_cart(self.session_key, self.product.id)

        result = checkout(self.session_key, self.user)

        order_item = OrderItem.objects.get(order=result["order"])
        self.assertEqual(order_item.price, Decimal("99.90"))
        self.assertEqual(order_item.quantity, 1)

    def test_checkout_clears_cart(self):
        """
        After a successful checkout, the cart should be empty.
        Like a cashier scanning and bagging all your items — the belt is cleared.
        """
        add_product_to_cart(self.session_key, self.product.id)
        add_product_to_cart(self.session_key, self.product.id)

        checkout(self.session_key, self.user)

        cart = Cart.objects.get(session_key=self.session_key)
        self.assertTrue(cart.is_empty())

    def test_checkout_locks_price_independently_of_product_changes(self):
        """
        Changing the product price after checkout should not affect the order total.
        """
        add_product_to_cart(self.session_key, self.product.id)
        result = checkout(self.session_key, self.user)

        # Simulate a price change after the order was placed
        self.product.price = "199.90"
        self.product.save()

        order_item = OrderItem.objects.get(order=result["order"])
        self.assertEqual(str(order_item.price), "99.90")



# ══════════════════════════════════════════════════════════════
# STOCK
# Testa as regras de negócio relacionadas ao estoque.
# ══════════════════════════════════════════════════════════════

class StockServiceTest(TestCase):

    def setUp(self):
        self.session_key = "session-stock"

    def test_add_product_out_of_stock_fails(self):
        """
        Adding a product with stock=0 to the cart should return success=False.
        The system must block it before even creating a CartItem.
        """
        product = make_product(stock=0)

        result = add_product_to_cart(self.session_key, product.id)

        self.assertFalse(result["success"])
        self.assertIn("estoque", result["error"].lower())
        self.assertFalse(CartItem.objects.filter(cart__session_key=self.session_key).exists())

    def test_add_product_exceeding_stock_fails(self):
        """
        Adding more units than available stock should return success=False.
        Like trying to put 5 items in your cart when there are only 2 on the shelf.
        """
        product = make_product(stock=2)

        add_product_to_cart(self.session_key, product.id)  # quantity = 1
        add_product_to_cart(self.session_key, product.id)  # quantity = 2
        result = add_product_to_cart(self.session_key, product.id)  # would be 3 — blocked

        self.assertFalse(result["success"])
        item = CartItem.objects.get(cart__session_key=self.session_key, product=product)
        self.assertEqual(item.quantity, 2)

    def test_checkout_decreases_stock(self):
        """
        After a successful checkout, the product stock must be reduced
        by the quantity purchased.
        Like a warehouse removing items from the shelf after an order ships.
        """
        product = make_product(stock=10, price=Decimal("50.00"))
        user = make_user()

        add_product_to_cart(self.session_key, product.id)
        add_product_to_cart(self.session_key, product.id)  # 2 units in cart

        checkout(self.session_key, user)

        product.refresh_from_db()
        self.assertEqual(product.stock, 8)

    def test_checkout_fails_when_stock_insufficient(self):
        """
        If stock runs out between adding to cart and checking out,
        the checkout must fail and the order must NOT be created.
        This simulates a race condition — two users competing for the last item.
        """
        product = make_product(stock=1, price=Decimal("50.00"))
        user = make_user()

        add_product_to_cart(self.session_key, product.id)  # 1 unit in cart

        # Simulate another user buying the last unit
        product.stock = 0
        product.save()

        result = checkout(self.session_key, user)

        self.assertFalse(result["success"])
        self.assertIn("estoque", result["error"].lower())
        self.assertEqual(Order.objects.filter(user=user).count(), 0)

    def test_product_is_available_returns_false_when_stock_zero(self):
        """
        is_available() must return False when stock is 0.
        This is used by templates to disable the add-to-cart button.
        """
        product = make_product(stock=0)
        self.assertFalse(product.is_available())

    def test_product_is_available_returns_true_when_stock_positive(self):
        """
        is_available() must return True when stock > 0.
        """
        product = make_product(stock=5)
        self.assertTrue(product.is_available())

    def test_has_enough_stock(self):
        """
        has_enough_stock() must return True only when stock >= requested quantity.
        """
        product = make_product(stock=3)
        self.assertTrue(product.has_enough_stock(1))
        self.assertTrue(product.has_enough_stock(3))
        self.assertFalse(product.has_enough_stock(4))


# ══════════════════════════════════════════════════════════════
# VIEWS — INTEGRAÇÃO
# Testa o fluxo completo: request HTTP → view → banco → response.
# Usa o Client do Django que simula um browser sem precisar de
# um servidor rodando. É como um robô que clica nos botões.
# ══════════════════════════════════════════════════════════════

class AccountViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        """
        GET /register/ should return 200 with the registration form.
        """
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/account/register.html")

    def test_register_post_creates_user_and_redirects(self):
        """
        POST to /register/ with valid data should create a user and redirect to login.
        """
        response = self.client.post(reverse("register"), {
            "username": "novousuario",
            "email": "novo@email.com",
            "password": "senha123",
            "confirm_password": "senha123",
        })

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="novousuario").exists())

    def test_register_post_with_wrong_passwords_shows_error(self):
        """
        POST to /register/ with mismatched passwords should stay on the page and show an error.
        """
        response = self.client.post(reverse("register"), {
            "username": "novousuario",
            "email": "novo@email.com",
            "password": "senha123",
            "confirm_password": "diferente",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "senhas")

    def test_login_page_loads(self):
        """
        GET /login/ should return 200 with the login form.
        """
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/account/login.html")

    def test_login_post_with_valid_credentials_redirects(self):
        """
        POST to /login/ with correct credentials should log the user in and redirect.
        """
        make_user(username="joao", password="senha123")

        response = self.client.post(reverse("login"), {
            "username": "joao",
            "password": "senha123",
        })

        self.assertRedirects(response, reverse("product_list"))

    def test_login_post_with_wrong_password_shows_error(self):
        """
        POST to /login/ with wrong password should stay on the page and show an error.
        """
        make_user(username="joao", password="senha123")

        response = self.client.post(reverse("login"), {
            "username": "joao",
            "password": "errada",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "inválidos")


class OrderViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.product = make_product(price=Decimal("50.00"))
        self.client.login(username="testuser", password="senha123")

        # Create a session key matching what Django assigns after login
        session = self.client.session
        session.save()
        self.session_key = session.session_key

    def test_checkout_page_loads_with_cart(self):
        """
        GET /checkout/ should show the cart summary.
        """
        add_product_to_cart(self.session_key, self.product.id)

        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/order/checkout.html")

    def test_checkout_post_creates_order_and_redirects(self):
        """
        POST /checkout/ with items in cart should create an order and redirect to confirmation.
        """
        add_product_to_cart(self.session_key, self.product.id)

        response = self.client.post(reverse("checkout"))

        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertRedirects(response, reverse("order_confirmation", args=[order.id]))

    def test_checkout_post_with_empty_cart_shows_error(self):
        """
        POST /checkout/ with an empty cart should stay on checkout page with an error.
        """
        response = self.client.post(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "vazio")

    def test_order_list_shows_user_orders(self):
        """
        GET /orders/ should show all orders placed by the logged-in user.
        """
        add_product_to_cart(self.session_key, self.product.id)
        self.client.post(reverse("checkout"))

        response = self.client.get(reverse("order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/order/list.html")
        self.assertEqual(response.context["orders"].count(), 1)

    def test_order_list_requires_login(self):
        """
        GET /orders/ without being logged in should redirect to login page.
        Like trying to enter a restricted area without a badge.
        """
        self.client.logout()

        response = self.client.get(reverse("order_list"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('order_list')}")

    def test_order_detail_shows_correct_order(self):
        """
        GET /orders/<id>/ should show the order detail for the logged-in user.
        """
        add_product_to_cart(self.session_key, self.product.id)
        self.client.post(reverse("checkout"))

        order = Order.objects.filter(user=self.user).first()
        response = self.client.get(reverse("order_detail", args=[order.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/order/detail.html")

    def test_order_detail_another_user_cannot_access(self):
        """
        A user should not be able to see another user's order.
        Security rule: orders are private to their owner.
        """
        add_product_to_cart(self.session_key, self.product.id)
        self.client.post(reverse("checkout"))
        order = Order.objects.filter(user=self.user).first()

        # Login as a different user
        other_user = make_user(username="outro", password="senha123")
        self.client.login(username="outro", password="senha123")

        response = self.client.get(reverse("order_detail", args=[order.id]))

        # Should redirect to order list since the order doesn't belong to this user
        self.assertRedirects(response, reverse("order_list"))