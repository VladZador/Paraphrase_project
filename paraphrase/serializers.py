from nltk import Tree

from rest_framework import serializers


class TreeSerializer(serializers.Serializer):
    tree = serializers.CharField()

    def validate_tree(self, value):
        try:
            tree = Tree.fromstring(value)
        except ValueError:
            raise serializers.ValidationError("Invalid parse tree")
        return value


class ParaphraseSerializer(serializers.Serializer):
    paraphrases = TreeSerializer(many=True)
