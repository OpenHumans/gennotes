import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, serializers
from reversion import revisions as reversion

from .models import Relation, Variant


class CurrentVersionMixin(object):

    def get_current_version(self, obj):
        """
        Return current version ID for non-edit methods, otherwise 'Unknown'.

        When editing, a new version will be created by django-reversion.
        However, due to transaction timing the ID for this new Version hasn't
        yet been generated and stored by the time the response for the editing
        API call is generated. Rather than return the old, incorrect ID, we
        simply report 'Unknown' for editing API calls.

        An editing app will need to perform a new GET request to get the new
        version ID for the object.
        """
        if self.context['request'].method in permissions.SAFE_METHODS:
            return reversion.get_for_date(obj, timezone.now()).id
        else:
            return 'Unknown'


class SafeTagCurrentVersionUpdateMixin(object):

    def _check_current_version(self, instance):
        """
        Check that the edited_version parameter matches the current version.

        If different, it indicates a probably "edit conflict": the submitted
        edit is being made to a stale version of the model.
        """
        edited_version = self.context['request'].data['edited_version']
        current_version = reversion.get_for_date(
            instance, timezone.now()).id
        if not current_version == edited_version:
            raise serializers.ValidationError(detail={
                'detail':
                    'Edit conflict error! The current version for this object '
                    'does not match the reported version being edited.',
                'current_version': current_version,
                'submitted_data': self.context['request'].data,
            })

    def _check_tag_data(self, instance, validated_data):
        tag_data = validated_data['tags']
        # For PUT, check that special tags are retained and unchanged.
        if not self.partial:
            for tag in instance.special_tags:
                if tag in instance.tags and tag not in tag_data:
                    raise serializers.ValidationError(detail={
                        'detail': 'PUT requests must retain all special tags. '
                        'Your request is missing the tag: {}'.format(tag)})
        # Check that special tags are unchanged.
        for tag in instance.special_tags:
            if (tag in instance.tags and tag in tag_data and
                    tag_data[tag] != instance.tags[tag]):
                raise serializers.ValidationError(detail={
                    'detail': 'Updates (PUT or PATCH) must not attempt '
                    'to change the values for special tags. Your request '
                    'attempts to change the value for tag '
                    "'{}' from '{}' to '{}'".format(
                        tag, instance.tags[tag], tag_data[tag])})
        return tag_data

    def update(self, instance, validated_data):
        """
        Update tags. Accept edit to current version, check protected tags.
        """
        if 'edited_version' not in self.context['request'].data:
            raise serializers.ValidationError(detail={
                'detail':
                    'Edit submissions to the API must include a parameter '
                    "'edited_version' that reports the version ID of the item "
                    'being edited.'
            })
        if ['tags'] != sorted(validated_data.keys()):
            raise serializers.ValidationError(detail={
                'detail':
                    "Edits must update the 'tags' field of a Variant or "
                    'Relation, and no other object fields. Your request '
                    'includes the following object fields: {}'.format(
                        validated_data.keys())
            })

        self._check_current_version(instance)
        tag_data = self._check_tag_data(instance, validated_data)

        if self.partial:
            instance.tags.update(tag_data)
        else:
            instance.tags = tag_data
        instance.save()

        return instance


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize a User object.
    """

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email')


class RelationSerializer(CurrentVersionMixin,
                         SafeTagCurrentVersionUpdateMixin,
                         serializers.HyperlinkedModelSerializer):
    """
    Serialize a Relation object.

    API-mediated updates to Relations may only be performed for the tags field.

    POST create must include required tags (e.g. type).

    PUT update overwrites all tags with the tags data in the request. Any
    existing special tags data (e.g. type) must be retained and unchanged.

    PATCH update will update any tags included in the request tag data. If
    special tags are listed, their values must be unchanged.
    """
    current_version = serializers.SerializerMethodField()
    variant = serializers.HyperlinkedRelatedField(
        queryset=Variant.objects.all(), view_name='variant-detail',
        required=False)

    class Meta:
        model = Relation

    def create(self, validated_data):
        """
        Check that all required tags are included in tag data before creating.
        """
        if ['tags', 'variant'] != sorted(validated_data.keys()):
            raise serializers.ValidationError(detail={
                'detail': "Create (POST) should include the 'tags' and "
                "'variant' fields. Your request contains the following "
                'fields: {}'.format(str(validated_data.keys()))})
        if 'tags' in validated_data:
            for tag in Relation.required_tags:
                if tag not in validated_data['tags']:
                    raise serializers.ValidationError(detail={
                        'detail': 'Create (POST) tag data must include all '
                        'required tags: {}'.format(Relation.required_tags)})
        return super(RelationSerializer, self).create(validated_data)


class VariantSerializer(CurrentVersionMixin,
                        SafeTagCurrentVersionUpdateMixin,
                        serializers.HyperlinkedModelSerializer):
    """
    Serialize a Variant object.

    API-mediated updates to Variants may only be performed for the tags field.

    PUT update overwrites all tags with the tags data in the request. Any
    existing special tags data (e.g. build 37 position) must be retained and
    unchanged.

    PATCH update will update any tags included in the request tag data. If
    special tags are listed, their values must be unchanged.
    """
    b37_id = serializers.SerializerMethodField()
    current_version = serializers.SerializerMethodField()
    relation_set = RelationSerializer(many=True, required=False)

    class Meta:
        model = Variant

    @staticmethod
    def get_b37_id(obj):
        """
        Return an ID like "b37-1-883516-G-A".
        """
        print obj.tags
        return '-'.join([
            'b37',
            obj.tags['chrom_b37'],
            obj.tags['pos_b37'],
            obj.tags['ref_allele_b37'],
            obj.tags['var_allele_b37'],
        ])

    def create(self, validated_data):
        """
        Check that all required tags are included in tag data before creating.
        """
        if ['tags'] != sorted(validated_data.keys()):
            raise serializers.ValidationError(detail={
                'detail': "Create (POST) should include the 'tags' field."
                "Your request contains the following "
                'fields: {}'.format(str(validated_data.keys()))})
        for tag in Variant.required_tags:
            if tag not in validated_data['tags']:
                raise serializers.ValidationError(detail={
                    'detail': 'Create (POST) tag data must include all '
                    'required tags: {}'.format(Relation.required_tags)})
            if (tag == 'chrom_b37' and validated_data['tags'][tag] not
                    in Variant.ALLOWED_CHROMS):
                raise serializers.ValidationError(detail={
                    'detail': 'Chromosomes must be numbers: "1", "2", '
                    '"3"... and "23" for X, "24" for Y, and "25" for MT.'})
        if Variant.objects.filter(
                tags__chrom_b37=validated_data['tags']['chrom_b37'],
                tags__pos_b37=validated_data['tags']['pos_b37'],
                tags__ref_allele_b37=validated_data['tags']['ref_allele_b37'],
                tags__var_allele_b37=validated_data['tags']['var_allele_b37']):
            raise serializers.ValidationError(detail={
                'detail': 'A variant for the following data already '
                          'exists: {}'.format(validated_data['tags'])})
        return super(VariantSerializer, self).create(validated_data)
