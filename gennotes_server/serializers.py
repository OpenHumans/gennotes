from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Relation, Variant


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize a User object.
    """

    class Meta:
        model = get_user_model()
        fields = ('id', 'username')


class RelationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize a Relation object.
    """

    class Meta:
        model = Relation
        fields = ['url', 'tags']


class VariantSerializer(serializers.HyperlinkedModelSerializer):
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
    relation_set = RelationSerializer(many=True, required=False)

    class Meta:
        model = Variant
        fields = ['url', 'b37_id', 'tags', 'relation_set']

    @staticmethod
    def get_b37_id(obj):
        """
        Return an ID like "1-883516-G-A".
        """
        return '-'.join([
            obj.tags['chrom-b37'],
            obj.tags['pos-b37'],
            obj.tags['ref-allele-b37'],
            obj.tags['var-allele-b37'],
        ])

    def update(self, instance, validated_data):
        """
        Update which only accepts 'tags' edits and checks for protected tags.
        """
        if ['tags'] != validated_data.keys():
            raise serializers.ValidationError(detail={
                'detail': "Variant edits should include the 'tags' field, "
                'and only this field. Your request is attempting to edit '
                'the following fields: {}'.format(validated_data.keys())})
        tag_data = validated_data['tags']

        # For PUT, check that special tags are retained and unchanged.
        if not self.partial:
            for tag in Variant.special_tags:
                if tag in instance.tags and tag not in tag_data:
                    raise serializers.ValidationError(detail={
                        'detail': 'PUT requests must retain all special tags. '
                        'Your request is missing the tag: {}'.format(tag)})
        # Check that special tags are unchanged.
        for tag in Variant.special_tags:
            if (tag in instance.tags and tag in tag_data and
                    tag_data[tag] != instance.tags[tag]):
                raise serializers.ValidationError(detail={
                    'detail': 'Updates (PUT or PATCH) must not attempt '
                    'to change the values for special tags. Your request '
                    'attempts to change the value for tag '
                    "'{}' from '{}' to '{}'".format(
                        tag, instance.tags[tag], tag_data[tag])})
        if self.partial:
            instance.tags.update(tag_data)
        else:
            instance.tags = tag_data
        instance.save()
        return instance
