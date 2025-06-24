from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser  # Corrected to IsAdminUser
from .models import  Voting ,Fan
from .serializers import  *
from django.db.models import Count
from django.db import models
from authentications.models import *
# Voting Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def voting_list_create(request):
    if request.method == 'GET':
        votes = Voting.objects.all()
        serializer = VotingSerializer(votes, many=True)
        return Response(serializer.data)
    

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def voting_detail(request, pk):
    try:
        vote = Voting.objects.get(pk=pk, user=request.user)
    except Voting.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = VotingSerializer(vote)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = request.data.copy()
        data['user_id'] = request.user.id
        serializer = VotingSerializer(vote, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_staff:  # Restrict DELETE to admins
            return Response({"detail": "Admin permission required"}, status=status.HTTP_403_FORBIDDEN)
        vote.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Optional: Template-based views for web interface


# Voting View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_create(request):
    serializer = VotingSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def vote_stats(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        return Response({"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND)

    votes = Voting.objects.filter(match=match).aggregate(
        team_a_votes=Count('pk', filter=models.Q(who_will_win='team_a')),
        team_b_votes=Count('pk', filter=models.Q(who_will_win='team_b')),
        draw_votes=Count('pk', filter=models.Q(who_will_win='draw'))
    )

    total_votes = votes['team_a_votes'] + votes['team_b_votes'] + votes['draw_votes']

    if total_votes > 0:
        team_a_percent = (votes['team_a_votes'] / total_votes) * 100
        team_b_percent = (votes['team_b_votes'] / total_votes) * 100
        draw_percent = (votes['draw_votes'] / total_votes) * 100
    else:
        team_a_percent = 0.0
        team_b_percent = 0.0
        draw_percent = 0.0

    return Response({
        "match_id": match_id,
        "total_votes": total_votes,
        "percentages": {
            "team_a": round(team_a_percent, 1),
            "team_b": round(team_b_percent, 1),
            "draw": round(draw_percent, 1)
        }
    })



@api_view(['GET'])
def engagement_stats(request):
    total_users = CustomUser.objects.count()
    total_votes = Voting.objects.count()
    return Response({
        "total_users": total_users,
        "total_votes": total_votes
    })

# Fan Points View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fan_points(request):
    fan, created = Fan.objects.get_or_create(user=request.user)
    serializer = FanSerializer(fan)
    return Response(serializer.data)

# Fan Leaderboard View
@api_view(['GET'])
def fan_leaderboard(request):
    fans = Fan.objects.all().order_by('-points')[:10]
    fans_with_ranks = []
    current_rank = 1
    previous_points = None
    for index, fan in enumerate(fans):
        if fan.points != previous_points:
            current_rank = index + 1
        fans_with_ranks.append({'fan': fan, 'rank': current_rank})
        previous_points = fan.points
    serializer = FanSerializer(
        [item['fan'] for item in fans_with_ranks],
        many=True,
        context={'ranks': {index: item['rank'] for index, item in enumerate(fans_with_ranks)}}
    )
    return Response(serializer.data)