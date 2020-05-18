from django.urls import path
from . import views
from posts.views import new_post
# MEDIA
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug>/", views.group_posts, name="group"),
    path("new", new_post, name="new_post"),
    path("follow/", views.follow_index, name="follow_index"),
    path("<username>/follow", views.profile_follow, name="profile_follow"),
    path("<username>/unfollow", views.profile_unfollow, name="profile_unfollow"),
    path("<username>/", views.profile, name="profile"),  # PROFILE
    path("<username>/<post_id>/", views.post_view, name="post"),  # POST
    path("<username>/<post_id>/edit/", views.post_edit, name="post_edit"),  # POST EDIT
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
