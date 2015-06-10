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
        fields = ['tags']


class VariantSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize a Variant object.
    """
    b37_id = serializers.SerializerMethodField()
    relation_set = RelationSerializer(many=True)

    class Meta:
        model = Variant
        fields = ['b37_id', 'tags', 'relation_set']

    @staticmethod
    def get_b37_id(obj):
        """
        Return an ID like "1-883516-G-A".
        """
        return '-'.join([
            obj.tags['chrom_b37'],
            obj.tags['pos_b37'],
            obj.tags['ref_allele_b37'],
            obj.tags['var_allele_b37'],
        ])
