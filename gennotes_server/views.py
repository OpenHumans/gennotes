import json
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

import rest_framework
from rest_framework import viewsets as rest_framework_viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

import reversion

from .models import CommitDeletion, Relation, Variant
from .permissions import IsVerifiedOrReadOnly
from .serializers import RelationSerializer, UserSerializer, VariantSerializer


class VariantLookupMixin(object):
    """
    Mixin method for looking up a variant according to b37 position.
    """

    def _custom_variant_filter_kwargs(self, variant_lookup):
        """
        For a variant lookup string, return the variant filter arguments.
        """
        try:
            parts = variant_lookup.split('-')
            if parts[0] == 'b37':
                return {
                    'tags__chrom-b37': parts[1],
                    'tags__pos-b37': parts[2],
                    'tags__ref-allele-b37': parts[3],
                    'tags__var-allele-b37': parts[4],
                }
        except IndexError:
            return None
        return None


class RevisionUpdateMixin(object):
    """
    ViewSet update mixin that records a django-reversion revision.
    """

    @transaction.atomic()
    @reversion.create_revision()
    def update(self, request, *args, **kwargs):
        """Custom update method to record revision information."""
        partial = kwargs.pop('partial', False)
        commit_comment = request.data.get('commit-comment', '')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        reversion.set_user(user=self.request.user)
        reversion.set_comment(comment=commit_comment)
        return Response(serializer.data)


class VariantViewSet(VariantLookupMixin,
                     RevisionUpdateMixin,
                     rest_framework.mixins.RetrieveModelMixin,
                     rest_framework.mixins.ListModelMixin,
                     rest_framework.mixins.UpdateModelMixin,
                     rest_framework_viewsets.GenericViewSet):
    """
    A viewset for Variants, allowing id and position-based lookups.

    Similar to rest_framework.viewsets.ModelViewSet, but create and delete
    methods ('POST' and 'DELETE') are not implemented.

    Update is implemented ('PUT' and 'PATCH'), and uses django-reversion to
    record the revision, user, and commit comment. API users are strongly
    encouraged to use PATCH to add and edit tags.

    In addition to lookup by primary key, Variants may be referenced by
    build 37 information (e.g. 'b37-1-123456-C-T'). Bulk GET requests can be
    formed by specifying a list of variants as a parameter.

    Example GETs on localhost:8000 using requests for all Variants (paginated):
        requests.get('http://localhost:8000/api/variant/')
        requests.get('http://localhost:8000/api/variant/',
                     params={'page_size': 20})
    Example GETs on localhost:8000 for a specific variant:
        requests.get('http://localhost:8000/api/variant/1234/')
        requests.get('http://localhost:8000/api/variant/b37-1-40758116-G-A/')
    Example GET for a list of variants (specified by id or b37 position):
        requests.get('http://localhost:8000/api/variant/', params={
            'variant_list': json.dumps(['123', '1233', 'b37-1-40758116-G-A'])})

    PUT and PATCH use the following data fields:
        - tags              (required) used to update or overwrite a Variant's
                            'tags' field
        - commit-comment    (optional) records a comment for this commit

    Example PATCH and PUT on localhost:8000 using requests:
        requests.patch(
            'http://localhost:8000/api/variant/1234/',
            data=json.dumps({
                'tags': {'example-tag': 'example-value'}
                'commit-comment': 'Adding an example tag using PATCH.'}),
            headers={'Content-type': 'application/json'},
            auth=('username', 'password'))
        requests.put(
            'http://localhost:8000/api/variant/b37-1-40758116-G-A',
            data=json.dumps({
                'tags': {'chrom-b37': '1',
                         'pos-b37': '40758116',
                         'ref-allele-b37': 'G',
                         'var-allele-b37': 'A',
                         'example-tag': 'example-value'},
                'commit-comment': 'Adding an example tag using PUT.'}),
            headers={'Content-type': 'application/json'},
            auth=('username', 'password'))
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
            if variant_lookup.isdigit():
                filter_kwargs = {'id': variant_lookup}
            else:
                filter_kwargs = self._custom_variant_filter_kwargs(variant_lookup)
            if filter_kwargs:
                if not Q_obj:
                    Q_obj = Q(**filter_kwargs)
                else:
                    Q_obj = Q_obj | Q(**filter_kwargs)
        queryset = queryset.filter(Q_obj)
        return queryset

    def get_object(self):
        """
        Primary key lookup if pk numeric, otherwise use custom filter kwargs.

        This allows us to also support build 37 lookup by chromosome, position,
        reference and variant.
        """
        if self.kwargs['pk'].isdigit():
            return super(VariantViewSet, self).get_object()

        queryset = self.filter_queryset(self.get_queryset())

        filter_kwargs = self._custom_variant_filter_kwargs(self.kwargs['pk'])
        if not filter_kwargs:
            raise Http404('No {} matches the given query.'.format(
                queryset.model._meta.object_name))

        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


# http GET localhost:8000/api/relation/   # all relations
# http GET localhost:8000/api/relation/2/ # relation with ID 2
# http -a youruser:yourpass PATCH localhost:8000/api/relation/2/ \
#  tags:='{"foo": "bar"}'                # set tags to '{"foo": "bar"}'
class RelationViewSet(RevisionUpdateMixin,
                      rest_framework.viewsets.ModelViewSet):
    """
    A viewset for Relations.

    Update ('PUT' and 'PATCH') uses django-reversion to record the revision,
    user, and commit comment.

    Create ('POST') records a new Relation.
    """
    permission_classes = (IsVerifiedOrReadOnly,)
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer

    @transaction.atomic()
    @reversion.create_revision()
    def create(self, request, *args, **kwargs):
        commit_comment = request.data.get('commit-comment', '')
        reversion.set_user(user=self.request.user)
        reversion.set_comment(comment=commit_comment)
        return super(RelationViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic()
    @reversion.create_revision()
    def record_destroy(self, request, instance):
        commit_comment = request.data.get('commit-comment', '')
        instance.save()
        reversion.set_user(user=self.request.user)
        reversion.set_comment(comment=commit_comment)
        reversion.add_meta(CommitDeletion)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.record_destroy(request, instance)
        return super(RelationViewSet, self).destroy(request, *args, **kwargs)


class CurrentUserView(RetrieveAPIView):
    """
    A viewset that returns the current user.
    """

    model = get_user_model()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
