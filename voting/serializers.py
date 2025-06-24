from rest_framework import serializers
from .models import  Voting ,Fan
from player.models import Player
from django.contrib.auth import get_user_model
User = get_user_model()
from player.serializers import PlayerSerializer
from match.models import Match
from authentications.serializers import CustomUserSerializer

class VotingSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())
    selected_players = PlayerSerializer(many=True, read_only=True)
    selected_players_ids = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(), source='selected_players', many=True, write_only=True, required=False
    )

    class Meta:
        model = Voting
        fields = ['id', 'user', 'match', 'who_will_win', 'goal_difference', 'selected_players', 'selected_players_ids', 'points_earned']

    def validate(self, data):
        match = data['match']
        if match.status == 'finished':
            raise serializers.ValidationError("Cannot vote on a finished match.")
        selected_players = data.get('selected_players', [])
        if len(selected_players) > 3:
            raise serializers.ValidationError("Cannot select more than 3 players.")
        for player in selected_players:
            if player not in match.selected_players.all():
                raise serializers.ValidationError(f"Player {player.name} is not in this match.")
        if data['who_will_win'] not in ['team_a', 'team_b', 'draw']:  # Added draw
            raise serializers.ValidationError("who_will_win must be 'team_a', 'team_b', or 'draw'.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
class FanSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = Fan
        fields = ['user', 'points', 'rank']

    def get_rank(self, obj):
        # Get rank from context (integer)
        rank = self.context.get('ranks', {}).get(self.instance.index(obj) if self.instance else 0, 1)
        # Format as 1st, 2nd, 3rd, etc.
        if rank % 10 == 1 and rank % 100 != 11:
            suffix = 'st'
        elif rank % 10 == 2 and rank % 100 != 12:
            suffix = 'nd'
        elif rank % 10 == 3 and rank % 100 != 13:
            suffix = 'rd'
        else:
            suffix = 'th'
        return f"{rank}{suffix}"