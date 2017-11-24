from django import forms

from .models import Post
from .models import UploadFileModel
from .models import Document

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFileModel
        fields = ('title', 'file')

    def __init__(self, *args, **kwargs):
        #super(PostForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )
