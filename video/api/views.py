"""
API views for listing videos and serving protected HLS video streams.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from .serializers import VideoListSerializer
from ..models import Video
from .permissions import CookieJWTAuthentication
from .utils import serve_m3u8, serve_segment


class VideoListView(APIView):
    """
    Return a list of available videos for authenticated users.
    """

    authentication_classes = [CookieJWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve a list of videos with basic metadata and thumbnail URLs.

        Returns:
            Response: 200 OK with serialized video data.
        """
        qs = Video.objects.all().only(
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail",
            "category",
        )
        data = VideoListSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class HLSManifestView(APIView):
    """
    Serve the HLS manifest (index.m3u8) for a given movie and resolution.
    """

    authentication_classes = [CookieJWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        """
        Return the HLS manifest file for the requested video and resolution.

        Args:
            movie_id (int): Identifier of the video.
            resolution (str): Requested resolution (e.g. "480p").

        Returns:
            FileResponse: The HLS playlist, or 404 if not found.
        """
        return serve_m3u8(movie_id, resolution)


class HLSSegmentView(APIView):
    """
    Serve individual HLS segment files for a given movie and resolution.
    """

    authentication_classes = [CookieJWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        """
        Return a single HLS segment for the requested video and resolution.

        Args:
            movie_id (int): Identifier of the video.
            resolution (str): Requested resolution (e.g. "480p").
            segment (str): Segment filename (e.g. "segment_001.ts").

        Returns:
            FileResponse: The HLS segment, or 404 if not found.
        """
        return serve_segment(movie_id, resolution, segment)
