from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('get-started/', views.get_started_view, name='get_started'),
    path('stats/', views.stats, name='stats'),
    path('stats/export/', views.stats_export, name='stats_export'),
    path('my-stats/', views.my_stats, name='my_stats'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
        path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Study Groups
    path('groups/', views.StudyGroupListView.as_view(), name='group_list'),
    path('groups/search/', views.StudyGroupSearchView.as_view(), name='group_search'),
    path('groups/<int:pk>/', views.StudyGroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:group_id>/stats/export/', views.group_stats_export, name='group_stats_export'),
    path('groups/create/', views.StudyGroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', views.StudyGroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/join/', views.join_group, name='join_group'),
    path('groups/<int:pk>/leave/', views.leave_group, name='leave_group'),
    
    # Comments
    path('groups/<int:group_id>/comments/add/', views.add_comment, name='add_comment'),
    path('groups/<int:group_id>/comments/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('groups/<int:group_id>/comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('groups/<int:group_id>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Study Sessions
    path('groups/<int:group_id>/sessions/create/', views.StudySessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/edit/', views.StudySessionUpdateView.as_view(), name='session_edit'),
    path('sessions/<int:pk>/delete/', views.StudySessionDeleteView.as_view(), name='session_delete'),
    
    # Study Materials
    path('groups/<int:group_id>/materials/upload/', views.StudyMaterialCreateView.as_view(), name='material_upload'),
    path('materials/<int:pk>/edit/', views.StudyMaterialUpdateView.as_view(), name='material_edit'),
    path('materials/<int:pk>/delete/', views.StudyMaterialDeleteView.as_view(), name='material_delete'),
    
    # Member Management
    path('groups/<int:group_id>/members/<int:membership_id>/change-role/', views.change_member_role, name='change_member_role'),
    path('groups/<int:group_id>/members/<int:membership_id>/remove/', views.remove_member, name='remove_member'),
        path('groups/<int:group_id>/stats/export_top/', views.group_top_members_export, name='group_top_members_export'),
        path('stats/export_top/', views.stats_top_members_export, name='stats_export_top'),
]