from rest_framework import serializers
from .models import Player




class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'image', 'name', 'jersey_number','status']



