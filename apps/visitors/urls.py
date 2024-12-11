from django.urls import path
from apps.visitors.views import (
    VisitorListView,
    new_visitor,
    edit_visitor,
    checkout_visitor,
    delete_visitor,
)

urlpatterns = [
    path("", VisitorListView.as_view(), name="visitors"),
    path("new-visitor/", new_visitor, name="new-visitor"),
    path("edit-visitor/", edit_visitor, name="edit-visitor"),
    path("checkout-visitor/<int:id>/", checkout_visitor, name="checkout-visitor"),
    path("delete-visitor/", delete_visitor, name="delete-visitor"),
]
