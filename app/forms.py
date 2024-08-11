from django import forms

from .models import Language, Gender, Voice

class Doc_Form(forms.Form):
    file_attachment=forms.FileField(label="Upload Document")
    
    language = forms.ModelChoiceField(queryset=Language.objects.all(), label="Select Language")
    
    gender = forms.ModelChoiceField(queryset=Gender.objects.none(), label="Select Gender")
    
    voice = forms.ModelChoiceField(queryset=Voice.objects.none(), label="Select Voice")

    def __init__(self, *args, **kwargs):
        super(Doc_Form, self).__init__(*args, **kwargs)
        # Set the initial queryset for gender and voice fields
        if 'language' in self.data:
            language_id = self.data.get('language')
            self.fields['gender'].queryset = Gender.objects.filter(language_id=language_id)
        if 'gender' in self.data:
            gender_id = self.data.get('gender')
            self.fields['voice'].queryset = Voice.objects.filter(gender_id=gender_id)
