from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from .serializers import VideoListSerializer
from .models import Video
from .permissions import CookieJWTAuthentication
from .utils import serve_m3u8, serve_segment


class VideoListView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Video.objects.all().only("id", "created_at", "title", "description", "thumbnail", "category")
        data = VideoListSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class HLSManifestView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        return serve_m3u8(movie_id, resolution)


class HLSSegmentView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        return serve_segment(movie_id, resolution, segment)
