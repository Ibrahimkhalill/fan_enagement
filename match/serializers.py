from rest_framework import serializers
from .models import  Match
from django.contrib.auth.models import User
from player.models import Player
from player.serializers import PlayerSerializer


class MatchSerializer(serializers.ModelSerializer):
    selected_players = PlayerSerializer(many=True, read_only=True)
    selected_players_ids = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(), source='selected_players', many=True, write_only=True, required=False
    )

    class Meta:
        model = Match
        fields = ['id', 'team_a', 'team_b', 'time', 'date', 'selected_players', 'selected_players_ids', 'winner', 'status', 'win_name']