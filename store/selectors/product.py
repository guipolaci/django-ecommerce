from store.models import Product


def get_all_products():
    """
    Retrieve all products from the database.

    This layer is responsible only for read operations.
    No business rules should be placed here.
    """
    return Product.objects.all()


def get_product_by_id(product_id: int):
    """
    Retrieve a single product by its ID.
    """
    return Product.objects.get(id=product_id)