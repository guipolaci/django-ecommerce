from store.selectors import get_all_products, get_product_by_id


def list_products():
    """
    Business layer responsible for listing products.

    Future business rules such as filtering active products
    or applying pricing rules should be placed here.
    """
    return get_all_products()


def retrieve_product(product_id: int):
    """
    Business layer responsible for retrieving a single product.

    Validation rules or additional business logic
    can be added here later.
    """
    return get_product_by_id(product_id)