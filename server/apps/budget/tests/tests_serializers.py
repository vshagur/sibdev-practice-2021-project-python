from ..factories import CategoryFactory
from ..models.budget.category import Category
from ..serializers import CategoryListSerializer
from django.test import testcases


class TestCategoryListSerializer(testcases.TestCase):
    def setUp(self):
        self.count = 15
        CategoryFactory.create_batch(size=self.count)
        self.categories = Category.objects.all()
        self.serializer = CategoryListSerializer(self.categories, many=True)
        self.fields = ('id', 'name', 'category_type')

    def test_serializer_data_contains_correct_field_values_of_objects(self):
        objects_as_dict = [dict(item) for item in self.serializer.data]
        expected = [item for item in self.categories.values(*self.fields)]
        self.assertSequenceEqual(objects_as_dict, expected)
