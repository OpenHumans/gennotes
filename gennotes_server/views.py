import json

from django.contrib.auth import get_user_model
from django.db.models import Q
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

    def _get_variant_filter_kwargs(self, variant_lookup):
        """
        For a variant lookup string, return the variant filter arguments.
        """
        try:
            parts = variant_lookup.split('-')
            if parts[0] == 'b37':
                return {
                    'tags__chrom_b37': parts[1],
                    'tags__pos_b37': parts[2],
                    'tags__ref_allele_b37': parts[3],
                    'tags__var_allele_b37': parts[4],
                }
        except IndexError:
            return None
        return None

    def get_object(self):
        print "In get_object"
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        filter_kwargs = self._get_variant_filter_kwargs(self.kwargs['pk'])

        if not filter_kwargs:
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

    def get_queryset(self, *args, **kwargs):
        """
        Return all variant data, or a subset if a specific list is requested.
        """
        queryset = super(VariantViewSet, self).get_queryset(*args, **kwargs)

        variant_list_json = self.request.query_params.get('variant_list', None)
        if not variant_list_json:
            return queryset
        variant_list = json.loads(variant_list_json)

        # Combine the variant list to make a single db query.
        Q_obj = None
        for variant_lookup in variant_list:
            filter_kwargs = self._get_variant_filter_kwargs(variant_lookup)
            if filter_kwargs:
                if not Q_obj:
                    Q_obj = Q(**filter_kwargs)
                else:
                    Q_obj = Q_obj | Q(**filter_kwargs)
        queryset = queryset.filter(Q_obj)
        return queryset


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
