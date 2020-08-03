from django import forms
from .models import Task, Board


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ('title', 'color')


class ReplaceTaskForm(forms.Form):
    new_parent_board = forms.ModelChoiceField(queryset=None)

    def __init__(self, board_list):
        super(ReplaceTaskForm, self).__init__()
        self.fields['new_parent_board'].queryset = board_list


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('description', 'task_status', 'file')


class AddTagForm(forms.Form):
    tag = forms.CharField(max_length=15)
