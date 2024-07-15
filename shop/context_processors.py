from shop.models import Category


def categories():
    categories = Category.objects.filter(parent=None)
    return {
        'categories': categories,
    }
