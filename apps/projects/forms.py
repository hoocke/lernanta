import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from drumbeat.utils import CKEditorWidget

from links.models import Link
from projects.models import Project, ProjectMedia, Participation
from users.models import UserProfile

log = logging.getLogger(__name__)


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'short_description', 'long_description', 'school')
	widgets = {
		'long_description': CKEditorWidget(config_name='reduced'),
	}


class ProjectLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url', 'subscribe')



class ProjectImageForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('image',)

    def clean_image(self):
        if self.cleaned_data['image'].size > settings.MAX_IMAGE_SIZE:
            max_size = settings.MAX_IMAGE_SIZE / 1024
            raise forms.ValidationError(
                _("Image exceeds max image size: %(max)dk",
                  dict(max=max_size)))
        return self.cleaned_data['image']


class ProjectStatusForm(forms.ModelForm):

    start_date = forms.DateField(localize=True, required=False)
    end_date = forms.DateField(localize=True, required=False)

    class Meta:
        model = Project
        fields = ('start_date', 'end_date', 'under_development', 'testing_sandbox', 'signup_closed')


class ProjectAddParticipantForm(forms.Form):
    user = forms.CharField()

    def __init__(self, project, *args, **kwargs):
        super(ProjectAddParticipantForm, self).__init__(*args, **kwargs)
        self.project = project

    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(_('There is no user with username: %s.') % username)
        if user == self.project.created_by:
            raise forms.ValidationError(_('User %s is organizing the study group.') % username)
        try:
            participation = self.project.participants().get(user=user)
            raise forms.ValidationError(_('User %s is already a participant.') % username)
        except Participation.DoesNotExist:
            pass
        return user



