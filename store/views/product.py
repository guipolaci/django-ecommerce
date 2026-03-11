from django.shortcuts import render
from store.services import list_products, retrieve_product


def product_list(request):
    """
    Handle product list page request.
    """

    products = list_products()

    context = {
        "products": products
    }

    return render(request, "store/product/list.html", context)


def product_detail(request, product_id: int):
    """
    Handle product detail page request.
    """

    product = retrieve_product(product_id)

    context = {
        "product": product
    }

    return render(request, "store/product/detail.html", context)