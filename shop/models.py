import random
import string

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def random_slug():
    return ''.join(random.choices(string.ascii_letters + string.digits) for _ in range(3))


class Category(models.Model):
    name = models.CharField(verbose_name='Category', max_length=200, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               related_name='children', blank=True, null=True)  # Ссылается на самого себя, по этому self
    slug = models.SlugField(verbose_name='URL', max_length=200, unique=True, null=False, editable=True)
    created_at = models.DateTimeField(verbose_name='Created time', auto_now_add=True)

    def __str__(self):
        full_path = [self.name]
        key = self.parent
        while key is not None:
            full_path.append(key.name)
            key = key.parent
        return ' > '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(random_slug() + '-pickBetter' + self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category_list', args=[str(self.slug)])

    class Meta:
        unique_together = (['slug', 'parent'])
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(verbose_name='Title', max_length=200)
    brand = models.CharField(verbose_name='Brand', max_length=200)
    description = models.TextField(verbose_name='Description', blank=True)
    slug = models.SlugField(verbose_name='URL', max_length=200)
    price = models.DecimalField(verbose_name='Price', max_digits=7, decimal_places=2, default=0)
    image = models.ImageField(verbose_name='Image', upload_to='products/products/%Y/%m/%d/')
    available = models.BooleanField(verbose_name='Available', default=True)
    created_at = models.DateTimeField(verbose_name='Created time', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated time', auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:products_detail', args=[str(self.slug)])

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ProductManager():
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(available=True)


class ProductProxy(Product):
    objects = ProductManager()

    class Meta:
        proxy = True
