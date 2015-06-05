from rest_framework import serializers
from .models import Relation, Variant


class VariantSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize a Variant object.
    """

    b37_id = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = ['b37_id', 'tags']

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


class RelationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize a Relation object.
    """

    class Meta:
        model = Relation
        fields = ['tags']
