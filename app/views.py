from django.shortcuts import render
from .forms import Doc_Form
import os
import boto3
from django.conf import settings
from django.contrib import messages
from .models import Language
import docx2txt
from django.http import JsonResponse
from .models import Gender, Voice


aws_access_key_id = settings.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY 
region_name = 'ap-southeast-1'




def doc_file_upload(request):
    form = Doc_Form()
    
    if request.method == 'POST':
        form = Doc_Form(request.POST, request.FILES)
        
        if form.is_valid():
            doc_file = request.FILES['file_attachment']
            
            if not doc_file.name.endswith(('.doc', '.docx')):
                messages.error(request, "Please upload a Word document (.doc or .docx).")
            else:
                language_id = form.cleaned_data['language'].id
                gender_id = form.cleaned_data['gender'].id
                voice_id =form.cleaned_data['voice'].id
                audio_files = extract_paragraph_and_generate_audio(doc_file, language_id, gender_id,voice_id)
                
                audio_files_with_url = [{'audio_url': f'{settings.MEDIA_URL}output_audio/{os.path.basename(file)}'} for file in audio_files]
                return render(request, 'doc_file_upload.html', {'audio_files': audio_files_with_url, 'doc_file': doc_file})

        else:
            messages.error(request, "File is not valid.")
    
    return render(request, "doc_file_upload.html", {'form': form})

def extract_paragraph_and_generate_audio(document, language_id, gender_id,voice_id):
    audio_files = []
    output_directory = os.path.join(settings.MEDIA_ROOT, 'output_audio')
    os.makedirs(output_directory, exist_ok=True)
    
    # Extract text from the document
    text = docx2txt.process(document)
    
    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # Convert each paragraph into mp3
    for i, paragraph in enumerate(paragraphs):
        print('i',i,'---------------------para:',paragraph)
        output_file = os.path.join(output_directory, f'paragraph_{i+1}.mp3')
        convert_text_to_speech(paragraph, output_file, language_id, gender_id,voice_id)
        audio_files.append(output_file)

    return audio_files



def convert_text_to_speech(text, output_file, language_id, gender_id,voice_id):
    try:
        # Retrieve the gender based on the provided gender_id
        gender = Gender.objects.get(id=gender_id)
        
        # Retrieve the voices associated with the gender
        voices = Voice.objects.filter(gender=gender)
        
        # Select a default voice for the gender (you can customize this logic)
        default_voice = voices.first()  # Or implement your logic to select a default voice
        selected_voice = Voice.objects.get(id=voice_id)
        
        if selected_voice:
            # Initialize Amazon Polly client
            polly_client = boto3.client('polly', region_name=region_name,
                                        aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key)
           
            # Synthesize speech
            response = polly_client.synthesize_speech(Text=text, OutputFormat='mp3', 
                                                       VoiceId=selected_voice.name, LanguageCode=selected_voice.gender.language.language_code)
           
            # Write audio stream to file
            with open(output_file, 'wb') as file:
                file.write(response['AudioStream'].read())

            return response['ResponseMetadata']['HTTPHeaders']['x-amzn-requestcharacters'], response['ResponseMetadata']['HTTPStatusCode']
        else:
            # Handle the case where no voice is available for the selected gender
            raise ValueError("No voice available for the selected gender.")
    except (Gender.DoesNotExist, Voice.DoesNotExist, Language.DoesNotExist) as e:
        # Handle the case where one of the objects does not exist
        raise e







def get_genders(request):
    language_id = request.GET.get('language_id')
    if language_id:
        genders = Gender.objects.filter(language_id=language_id).values_list('id', 'name')
        data = {'genders': dict(genders)}
        return JsonResponse(data)
    else:
        return JsonResponse({})

def get_voices(request):
    gender_id = request.GET.get('gender_id')
    language_id = request.GET.get('language_id')
    if gender_id and language_id:
        voices = Voice.objects.filter(gender_id=gender_id).values_list('id', 'name')
        data = {'voices': dict(voices)}
        return JsonResponse(data)
    else:
        return JsonResponse({})
    
def doc_summary(request):
    return render(request,'doc_summary.html')

