from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('board<int:board_pk>/task<int:task_pk>/get_task_file', views.get_task_file, name='get_task_file'),
    path('board<int:board_pk>/task<int:task_pk>/complete_task', views.complete_task, name='complete_task'),
    path('board<int:board_pk>/task<int:task_pk>/delete_task', views.delete_task, name='delete_task'),
    path('board<int:board_pk>/task<int:task_pk>/', views.detail_task, name='detail_task'),
    path('board<int:board_pk>/task<int:task_pk>/replace_task', views.replace_task, name='replace_task'),
    path('board<int:pk>/create_task', views.create_task, name='create_task'),
    path('board<int:board_pk>/task<int:task_pk>/edit_task', views.edit_task, name='edit_task'),
    path('board<int:board_pk>/task<int:task_pk>/add_tag', views.add_tag, name='add_tag'),
    path('board<int:pk>/delete_board', views.delete_board, name='delete_board'),
    path('create_board/', views.create_board, name='create_board'),
    path('board<int:pk>/edit_board', views.edit_board, name='edit_board'),
    path('search_tag_<str:tag>/', views.search_tag, name='search_tag'),
    path('get_json', views.get_json, name='get_json'),
    path('', views.board_list, name='main-page'),
    path('board<int:pk>/', views.task_list, name='Board'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
