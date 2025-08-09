from django.urls import path

from apps.inventory.views import CategoriesAPIView, CategoryDetailAPIView, CreateCategoryAPIView, CreateInventoryItemAPIView, CreateUnitOfMeasureAPIView, InventoryItemDetailAPIView, InventoryItemsListView, UnitOfMeasureAPIView, UnitOfMeasureDetailAPIView


urlpatterns = [
    path("units-of-measure/", UnitOfMeasureAPIView.as_view(), name="units-of-measure-list"),
    path("units-of-measure/<int:pk>/", UnitOfMeasureDetailAPIView.as_view(), name="units-of-measure-detail-update-delete"),
    path("units-of-measure/create/", CreateUnitOfMeasureAPIView.as_view(), name="units-of-measure-create"),
    path("categories/", CategoriesAPIView.as_view(), name="categories-list"),
    path("categories/<int:pk>/", CategoryDetailAPIView.as_view(), name="categories-detail-update-delete"),
    path("categories/create/", CreateCategoryAPIView.as_view(), name="categories-create"),
    path("items/", InventoryItemsListView.as_view(), name="items-list"),
    path("items/create/", CreateInventoryItemAPIView.as_view(), name="items-create"),
    path("items/<int:pk>/", InventoryItemDetailAPIView.as_view(), name="items-detail"),

]
