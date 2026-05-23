from django import forms
from .models import MLModel, TrainingDataset


class MLModelForm(forms.ModelForm):
    class Meta:
        model = MLModel
        fields = ['name']


class TrainingDatasetForm(forms.ModelForm):
    class Meta:
        model = TrainingDataset
        fields = ['name']
