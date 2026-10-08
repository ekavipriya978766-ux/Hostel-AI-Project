from django import forms

from .models import Complaint, StatusUpdate


class ComplaintForm(forms.ModelForm):
    """Student-facing form. Deliberately excludes severity/department/status
    /assigned_warden - those are 100% AI + system generated, never chosen by
    the student."""

    class Meta:
        model = Complaint
        fields = ["title", "description", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Short summary of the issue"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe the issue in detail"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class StatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=Complaint.Status.choices, widget=forms.Select(attrs={"class": "form-select"}))
    note = forms.CharField(
        required=False, max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional note about this update"}),
    )
