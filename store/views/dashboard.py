from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from store.models import Product, Order
from store.forms import ProductForm


@staff_member_required(login_url='/login/')
def dashboard_index(request):
    """
    Página principal do dashboard.
    Mostra cards com totais e últimos pedidos.
    """
    total_orders   = Order.objects.count()
    total_products = Product.objects.count()
    low_stock      = Product.objects.filter(stock__lte=5, stock__gt=0)
    out_of_stock   = Product.objects.filter(stock=0).count()
    latest_orders  = Order.objects.select_related('user').order_by('-created_at')[:10]

    return render(request, 'store/dashboard/index.html', {
        'total_orders':   total_orders,
        'total_products': total_products,
        'low_stock':      low_stock,
        'out_of_stock':   out_of_stock,
        'latest_orders':  latest_orders,
    })


@staff_member_required(login_url='/login/')
def dashboard_product_create(request):
    """
    Formulário de cadastro de novo produto.
    GET  — exibe o formulário vazio.
    POST — valida e salva o produto.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('dashboard_index')
    else:
        form = ProductForm()

    return render(request, 'store/dashboard/product_create.html', {'form': form})


@staff_member_required(login_url='/login/')
def dashboard_product_list(request):
    """
    Lista todos os produtos com opção de edição.
    """
    products = Product.objects.order_by('-created_at')
    return render(request, 'store/dashboard/product_list.html', {'products': products})


@staff_member_required(login_url='/login/')
def dashboard_product_edit(request, product_id):
    """
    Edição de produto existente.
    Mesmo formulário do cadastro, mas preenchido com os dados atuais.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('dashboard_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/dashboard/product_create.html', {
        'form': form,
        'editing': True,
        'product': product,
    })

@staff_member_required(login_url='/login/')
def dashboard_product_delete(request, product_id):
    """
    Exclui um produto.
    Só aceita POST — nunca DELETE via URL direta.
    Isso evita que alguém exclua um produto só acessando um link.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Produto "{product.name}" excluído com sucesso.')
        return redirect('dashboard_product_list')

    return redirect('dashboard_product_list')