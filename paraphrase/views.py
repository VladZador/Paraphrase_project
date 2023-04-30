from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .serializers import ParaphraseSerializer, TreeSerializer
from . import services


class ParaphraseListView(APIView):
    def get(self, request):
        tree_serializer = TreeSerializer(
            data={"tree": request.query_params.get("tree")}
        )
        if not tree_serializer.is_valid():
            return Response(
                tree_serializer.errors,
                status=HTTP_400_BAD_REQUEST
            )
        limit, is_valid = services.validate_limit(
            request.query_params.get("limit", 20)
        )
        if not is_valid:
            return Response(
                {"limit": ["Limit must be a positive integer"]},
                status=HTTP_400_BAD_REQUEST
            )
        tree_set = services.create_tree_variations(tree_serializer, limit)
        serializer = ParaphraseSerializer(data={"paraphrases": tree_set})
        serializer.is_valid()
        return Response(serializer.data)
