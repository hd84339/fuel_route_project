from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def route_api_view(request):
    start = request.GET.get('start')
    end = request.GET.get('end')

    return Response({
        "start": start,
        "end": end,
        "message": "API working"
    })