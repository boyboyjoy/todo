import os
import zipfile
from datetime import datetime
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import CreateTaskForm, CreateBoardForm, AddTagForm, ReplaceTaskForm
from .models import Board, Task
from .services import date_validate, get_all_boards, add_json_in_zip, search_tasks_by_tag, \
    change_task_fields_from_request


def board_list(request):
    if request.user.is_authenticated:
        return render(request, 'BoardList.html', {'board_list': get_all_boards(request.user)})
    else:
        return redirect(reverse('auth:login'))


def task_list(request, pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=pk)
        task_object_list = board.task_set.all()
        context = {'task_list': task_object_list, 'board': board,
                   'create_task_form': CreateTaskForm()}
        return render(request, 'TaskList.html', context)
    else:
        return redirect('main-page')


def create_board(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            color = request.POST.get('color', None)
            if len(color) != 7 or color[0] != '#' or str(color[1:]).isalpha() is not True:
                messages.add_message(request, messages.WARNING, 'Color format is: #AAAAAA')
                return render(request, 'CreateBoard.html', context={'create_board_form': CreateBoardForm()})
            title_board = request.POST.get('title', None)
            Board.objects.create(title=title_board, user_creator=request.user, color=color)
        if request.method == 'GET':
            return render(request, 'CreateBoard.html', context={'create_board_form': CreateBoardForm()})
    return redirect('main-page')


def delete_board(request, pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=pk)
        board.delete()
    return redirect('main-page')


def create_task(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'CreateTask.html', context={'create_task_form': CreateTaskForm(),
                                                               'pk': pk, 'title_page': 'Create task',
                                                               'color': board.color})
        elif request.method == 'POST':
            description = request.POST.get('description', None)
            scheduled_deadline = request.POST.get('scheduled_deadline', None)
            error = date_validate(scheduled_deadline)
            if error != 'Okay':
                messages.add_message(request, messages.WARNING, error)
                return redirect(reverse('create_task', kwargs={'pk': pk}))
            status = request.POST.get('task_status', None)
            file = request.FILES.get('file', None)
            if file is None or file.size > 8388608:
                file = None
            board = get_object_or_404(Board, pk=pk)
            task = board.task_set.create(description=description,
                                         scheduled_deadline=scheduled_deadline,
                                         task_status=status, file=file)
            task.save()
    return redirect(reverse('Board', kwargs={'pk': pk}))


def replace_task(request, board_pk, task_pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            new_parent_board_id = request.POST.get('new_parent_board', None)
            task = Task.objects.get(pk=task_pk)
            new_parent_board = Board.objects.get(pk=new_parent_board_id)
            if 'replace' in request.POST:
                task.parent_board = new_parent_board
                task.save()
            elif 'copy' in request.POST:
                copy_of_task = new_parent_board.task_set.create(description=task.description,
                                                                scheduled_deadline=task.scheduled_deadline,
                                                                real_deadline=task.real_deadline,
                                                                task_status=task.task_status,
                                                                file=task.file)
                for tag in task.tag_set.all():
                    copy_of_task.tag_set.create(text=tag.text)
                copy_of_task.save()
            return redirect(reverse('Board', kwargs={'pk': board_pk}))
        elif request.method == 'GET':
            board = get_object_or_404(Board, pk=board_pk)
            board_object_list = get_all_boards(request.user)
            return render(request, 'Replace_copy_task.html', context={'title_page': 'Replace or copy task',
                                                                      'board_pk': board_pk,
                                                                      'task_pk': task_pk,
                                                                      'replace_task_form': ReplaceTaskForm(
                                                                          board_object_list),
                                                                      'board_list': board_object_list,
                                                                      'color': board.color})
    return redirect('main-page')


def detail_task(request, task_pk, board_pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=board_pk)
        task = board.task_set.get(pk=task_pk)
        board_object_list = get_all_boards(request.user)
        replace_task_form = ReplaceTaskForm(board_object_list)
        return render(request, 'DetailTask.html',
                      context={'task': task, 'board': board,
                               'edit_task_form': CreateTaskForm(),
                               'replace_task_form': replace_task_form,
                               'add_tag_form': AddTagForm(), 'color': board.color})
    return redirect('main-page')


def delete_task(request, task_pk, board_pk):
    if request.user.is_authenticated:
        board = get_object_or_404(Board, pk=board_pk)
        deleting_task = board.task_set.get(pk=task_pk)
        deleting_task.delete()
        return redirect(reverse('Board', kwargs={'pk': board_pk}))
    return redirect('main-page')


def edit_board(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            board = get_object_or_404(Board, pk=pk)
            new_board_title = request.POST.get('title', None)
            new_board_color = request.POST.get('color', None)
            if len(new_board_color) != 7 or new_board_color[0] != '#' or str(new_board_color[1:]).isalpha() is not True:
                messages.add_message(request, messages.WARNING, 'Color format is: #AAAAAA')
                return render(request, 'EditBoard.html', context={'title_page': 'Edit board',
                                                                  'edit_board_form': CreateBoardForm(),
                                                                  'pk': pk,
                                                                  'color': board.color})
            board.title = new_board_title
            board.color = new_board_color
            board.save()
            return redirect(reverse('Board', kwargs={'pk': pk}))
        elif request.method == 'GET':
            board = get_object_or_404(Board, pk=pk)
            return render(request, 'EditBoard.html', context={'title_page': 'Edit board',
                                                              'edit_board_form': CreateBoardForm,
                                                              'pk': pk, 'color': board.color})
    else:
        return redirect('main-page')


def edit_task(request, board_pk, task_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if request.user.is_authenticated:
        if request.method == 'POST':
            board = get_object_or_404(Board, pk=board_pk)
            task = board.task_set.get(pk=task_pk)
            scheduled_deadline = request.POST.get('scheduled_deadline', None)
            error = date_validate(scheduled_deadline)
            if error != 'Okay':
                messages.add_message(request, messages.WARNING, error)
                return redirect(reverse('edit_task', kwargs={'task_pk': task_pk, 'board_pk': board_pk}))
            change_task_fields_from_request(task, request)
            try:
                task.save()
            except ValidationError:
                messages.add_message(request, messages.WARNING, 'Input deadlines !!!')
                return render(request, 'EditTask.html', context={'edit_task_form': CreateTaskForm(),
                                                                 'title_page': 'Edit task',
                                                                 'board_pk': board_pk,
                                                                 'task_pk': task_pk,
                                                                 'color': board.color})
            return redirect(reverse('detail_task', kwargs={'board_pk': board_pk,
                                                           'task_pk': task_pk}))
        elif request.method == 'GET':
            return render(request, 'EditTask.html', context={'edit_task_form': CreateTaskForm(),
                                                             'title_page': 'Edit task',
                                                             'board_pk': board_pk, 'task_pk': task_pk,
                                                             'color': board.color})
    else:
        return redirect('main-page')


def get_json(request):
    if request.user.is_authenticated:
        response = HttpResponse(content_type='application/zip')
        board_object_list = get_all_boards(request.user)
        file_list = []
        if len(board_object_list) == 0:
            messages.add_message(request, messages.WARNING, "You have not board")
            return redirect(reverse('main-page'))
        add_json_in_zip(board_object_list, response, file_list)
        response['Content-Disposition'] = f'attachment; filename={str(request.user.name)}.zip'
        return response
    return redirect('main-page')


def get_task_file(request, board_pk, task_pk):
    if request.user.is_authenticated:
        response = HttpResponse(content_type='application/zip')
        zip_file = zipfile.ZipFile(response, 'w')
        task = get_object_or_404(Task, pk=task_pk)
        filepath = os.path.join(os.getcwd(), 'media', str(task.file))
        if os.path.exists(filepath):
            zip_file.write((os.path.relpath(filepath)))
            zip_file.close()
            response['Content-Disposition'] = f'attachment; filename={task.file}.zip'
            return response
        return redirect(reverse('detail_task', kwargs={'board_pk': board_pk, 'task_pk': task_pk}))
    return redirect('main-page')


def add_tag(request, board_pk, task_pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            board = get_object_or_404(Board, pk=board_pk)
            task = board.task_set.get(pk=task_pk)
            tag = request.POST.get('tag', None)
            task.tag_set.create(text=tag)
            return redirect(reverse('detail_task', kwargs={'board_pk': board_pk, 'task_pk': task_pk}))
        elif request.method == 'GET':
            board = get_object_or_404(Board, pk=board_pk)
            return render(request, 'AddTag.html', context={'title_page': 'Add tag',
                                                           'add_tag_form': AddTagForm(),
                                                           'board_pk': board_pk, 'task_pk': task_pk,
                                                           'color': board.color})
    else:
        return redirect('main-page')


def search_tag(request, tag):
    if request.user.is_authenticated:
        list_of_lists = []
        all_boards = []
        board_object_list = get_all_boards(request.user)
        search_tasks_by_tag(board_object_list, tag, all_boards, list_of_lists)
        list_of_lists = [item for item in list_of_lists if item]
        pair_list = zip(all_boards, list_of_lists)
        return render(request, 'SearchedTask.html', context={'board_list': pair_list,
                                                             'tag': tag})
    return redirect('main-page')


def complete_task(request, board_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.task_status == 'COMPLETED':
        messages.add_message(request, messages.WARNING, 'This task has already been completed')
        return redirect(reverse('detail_task', kwargs={'board_pk': board_pk, 'task_pk': task_pk}))
    else:
        task.task_status = 'COMPLETED'
        task.real_deadline = datetime.date(datetime.now())
        task.save()
        return redirect(reverse('detail_task', kwargs={'board_pk': board_pk,
                                                       'task_pk': task_pk}))
