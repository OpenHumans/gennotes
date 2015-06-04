from rest_framework import permissions, viewsets

from .models import Relation, Variant
from .serializers import RelationSerializer, VariantSerializer

# http GET localhost:8000/api/variant/   # all variants
# http GET localhost:8000/api/variant/2/ # variant with ID 2
# http -a youruser:yourpass PATCH localhost:8000/api/variant/2/ \
#  tags:='{"foo": "bar"}'                # set tags to '{"foo": "bar"}'
class VariantViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


# http GET localhost:8000/api/relation/   # all relations
# http GET localhost:8000/api/relation/2/ # relation with ID 2
# http -a youruser:yourpass PATCH localhost:8000/api/relation/2/ \
#  tags:='{"foo": "bar"}'                # set tags to '{"foo": "bar"}'
class RelationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
