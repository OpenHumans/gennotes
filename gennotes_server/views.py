from rest_framework import viewsets

from .models import Relation, Variant
from .serializers import RelationSerializer, VariantSerializer

# http GET localhost:8000/api/variant/   # all variants
# http GET localhost:8000/api/variant/2/ # variant with ID 2
# http PATCH localhost:8000/api/variant/2/ tags:='{"foo": "bar"}'
# ^ set tags to '{"foo": "bar"}'
class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


# http GET localhost:8000/api/relation/   # all relations
# http GET localhost:8000/api/relation/2/ # relation with ID 2
# http PATCH localhost:8000/api/relation/2/ tags:='{"foo": "bar"}'
# ^ set tags to '{"foo": "bar"}'
class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
