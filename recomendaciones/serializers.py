from rest_framework import serializers


class GameRecommendationSerializer(serializers.Serializer):
    """Serializador del endpoint REST: evidencia el paradigma declarativo
    (DRF declara QUÉ campos exponer, sin lógica imperativa de renderizado)."""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    genre = serializers.SerializerMethodField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    description = serializers.CharField(read_only=True)
    affinity_score = serializers.SerializerMethodField()

    def get_genre(self, obj):
        return obj.genre.name

    def get_affinity_score(self, obj):
        scores = self.context.get('scores', {})
        return round(scores.get(obj.pk, 0.0), 4)
