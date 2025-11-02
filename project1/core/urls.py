from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('groups/', views.StudyGroupListView.as_view(), name='group_list'),
    path('groups/search/', views.StudyGroupSearchView.as_view(), name='group_search'),
    path('groups/<int:pk>/', views.StudyGroupDetailView.as_view(), name='group_detail'),
    path('groups/create/', views.StudyGroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/join/', views.join_group, name='join_group'),
    path('groups/<int:pk>/leave/', views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/comments/add/', views.add_comment, name='add_comment'),
    path('groups/<int:group_id>/comments/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('groups/<int:group_id>/comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('groups/<int:group_id>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]