from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartItemReadSerializer, CartSerializer

# Create your views here.


class CartListCreateView(generics.ListCreateAPIView):
    """
    List or create the user's cart.
    - GET: Returns the active cart for the authenticated user (creates one if none exists).
    - POST: Returns the active cart if it exists, otherwise creates one.
    Only one cart per user is allowed.
    Filtering, search, and ordering are supported.
    """

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["is_active", "checked_out"]
    search_fields = ["user__email"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        # Fix for drf-yasg schema generation (AnonymousUser)
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        return (
            Cart.objects.select_related("user")
            .prefetch_related("items__product")
            .filter(user=self.request.user, is_active=True)
        )

    def list(self, request, *args, **kwargs):
        # Return the active cart, or create one if none exists
        cart, created = Cart.objects.get_or_create(
            user=request.user, is_active=True, defaults={}
        )
        serializer = self.get_serializer(cart)
        return Response([serializer.data])

    def create(self, request, *args, **kwargs):
        # Return the active cart if it exists, otherwise create one
        cart, created = Cart.objects.get_or_create(
            user=request.user, is_active=True, defaults={}
        )
        serializer = self.get_serializer(cart)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CartRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the user's cart by ID.
    Filtering, search, and ordering are supported.
    """

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["is_active", "checked_out"]
    search_fields = ["user__email"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        # Fix for drf-yasg schema generation (AnonymousUser)
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        return (
            Cart.objects.select_related("user")
            .prefetch_related("items__product")
            .filter(user=self.request.user)
        )


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemReadSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # Fix for drf-yasg schema generation (AnonymousUser)
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        return CartItem.objects.filter(
            cart__user=self.request.user,
            cart_id=self.kwargs["cart_id"],
            cart__is_active=True,
        )

    def perform_create(self, serializer):
        cart = Cart.objects.get(
            id=self.kwargs["cart_id"], user=self.request.user, is_active=True
        )
        product = serializer.validated_data["product"]
        price = product.price
        serializer.save(cart=cart, price=price)


class CartItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemReadSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # Fix for drf-yasg schema generation (AnonymousUser)
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        return CartItem.objects.filter(
            cart__user=self.request.user,
            cart_id=self.kwargs["cart_id"],
            cart__is_active=True,
        )


class CartClearItemsView(APIView):
    """
    Remove all items from the specified cart for the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id, user=request.user, is_active=True)
            cart.clear_items()
            return Response({"detail": "All items removed from cart."})
        except Exception as exc:
            return Response(
                {"detail": str(exc), "type": type(exc).__name__},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CartItemListCreateTopView(generics.ListCreateAPIView):
    """
    List all cart items for the active cart or add a new item.
    - GET: Returns all items in the active cart for the authenticated user.
    - POST: Add a new item to the active cart.
    Filtering, search, and ordering are supported.
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["product", "quantity"]
    search_fields = ["product__name"]
    ordering_fields = ["created_at", "updated_at", "quantity"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemReadSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return CartItem.objects.select_related("product").filter(
            cart__user=self.request.user, cart__is_active=True
        )

    def perform_create(self, serializer):
        # Get or create active cart for the user
        cart, created = Cart.objects.get_or_create(
            user=self.request.user, 
            is_active=True, 
            defaults={}
        )
        product = serializer.validated_data["product"]
        price = product.price
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        if existing_item:
            existing_item.quantity += serializer.validated_data.get("quantity", 1)
            existing_item.save()
            # Set the instance to the updated existing item
            serializer.instance = existing_item
        else:
            serializer.save(cart=cart, price=price)


class CartItemRetrieveUpdateDestroyTopView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a cart item from the active cart.
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemReadSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # Fix for drf-yasg schema generation (AnonymousUser)
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        return CartItem.objects.filter(
            cart__user=self.request.user, cart__is_active=True
        )
