from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView

from .models import Relation, Variant
from .permissions import IsVerifiedOrReadOnly
from .serializers import RelationSerializer, UserSerializer, VariantSerializer


class VariantLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get lookup by variant.
    """

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        try:
            parts = self.kwargs['pk'].split('-')

            lookup_type = parts[0]

            if lookup_type == 'b37':
                filter_kwargs = {
                    'tags__chrom_b37': parts[1],
                    'tags__pos_b37': parts[2],
                    'tags__ref_allele_b37': parts[3],
                    'tags__var_allele_b37': parts[4],
                }
            else:
                raise IndexError
        except IndexError:
            raise Http404('No {} matches the given query.'.format(
                queryset.model._meta.object_name))

        return get_object_or_404(queryset, **filter_kwargs)


# http GET localhost:8000/api/variant/   # all variants
# http GET localhost:8000/api/variant/1-123456-C-T/ # a specific variant
#
# TODO: you should never be able to PATCH a variant, each change to a variant
# should create a new changeset
# http -a youruser:yourpass PATCH localhost:8000/api/variant/1-123456-C-T/ \
#  tags:='{"foo": "bar"}'                # set tags to '{"foo": "bar"}'
class VariantViewSet(VariantLookupMixin, viewsets.ModelViewSet):
    """
    A viewset for Variants which uses "1-883516-G-A" notation for lookups.
    """

    permission_classes = (IsVerifiedOrReadOnly,)
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


# http GET localhost:8000/api/relation/   # all relations
# http GET localhost:8000/api/relation/2/ # relation with ID 2
# http -a youruser:yourpass PATCH localhost:8000/api/relation/2/ \
#  tags:='{"foo": "bar"}'                # set tags to '{"foo": "bar"}'
class RelationViewSet(viewsets.ModelViewSet):
    """
    A viewset for Relations.
    """

    permission_classes = (IsVerifiedOrReadOnly,)
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer


class CurrentUserView(RetrieveAPIView):
    """
    A viewset that returns the current user.
    """

    model = get_user_model()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
