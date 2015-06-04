from rest_framework import serializers
from .models import Relation, Variant


class VariantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Variant
        fields = ["tags"]


class RelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Relation
        fields = ["tags"]
