from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()

router.register(r'', PostViewSet, basename='posts')
urlpatterns = router.urls
