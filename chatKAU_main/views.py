import pandas as pd
import chromadb
from django.http import StreamingHttpResponse
from googletrans import Translator
from chromadb.utils import embedding_functions
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
import openai
import sys
import urllib.request
from datetime import datetime
from rest_framework.decorators import api_view
from chatKAU_main.models import SchoolInfo

papago_client_id = "CggFiq0B0YSdoyCO0P3q" 
papago_client_secret = "f4DwnSEbAX" 

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

collection = None
ids = []
documents = []
doc_meta = []

date = datetime.now().strftime("%Y-%m-%d")
day_of_week = datetime.now().strftime("%A")

def index(request):
    return render(request, 'home.html')


def translate_to_english(text):
    data = "source=ko&target=en&text=" + text
    url = "https://openapi.naver.com/v1/papago/n2mt"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", papago_client_id)
    request.add_header("X-Naver-Client-Secret", papago_client_secret)
    
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    
    if rescode==200:
        response_body = response.read()
        response_body_decoded = response_body.decode('utf-8') 
        response_data = json.loads(response_body_decoded)

        translated_text = response_data['message']['result']['translatedText']
        return translated_text
    else:
        print("Error Code:" + rescode)


def initialize_vectordb():
    global collection
    if collection is not None:
        return
    
    df = pd.read_csv("./kau_data_eng_major.csv")

    client = chromadb.PersistentClient(path="docs/chroma/")
    
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai.api_key,
                model_name="text-embedding-ada-002"
    )
    
    collection = client.get_or_create_collection(
        name="schoolInfo",
        metadata={"hnsw:space": "cosine"},
        embedding_function=openai_ef
    )
    
    for i in range(len(df)):
        item = df.iloc[i]
        
        meta = {
            "row": str(item['INDEX']),
            "source": item['URL']
        }
        
        doc_meta.append(meta)
        ids.append(item['KOREAN'])
        documents.append(item['ENGLISH'])
        
    collection.add(
        documents=documents,
        metadatas=doc_meta,
        ids=ids
    )


@csrf_exempt
@api_view(['POST'])
def saveChatHistory(request, isGood):
    data = json.loads(request.body)
    question = data.get("question", "")
    answer = data.get("answer", "")
    
    if isGood == 'true' and not SchoolInfo.objects.filter(keyword=question).exists():
        SchoolInfo.objects.create(keyword=question, content=answer, origin="user")
    
    return JsonResponse({"status": "success"})
         

@csrf_exempt
def langchain(request):
    question = request.GET.get('question', '')
    english_question = translate_to_english(question)
        
    initialize_vectordb()
    
    result = collection.query(
        query_texts=english_question,
        n_results=2
    )

    content_origin = result['ids'][0][0]
    metadata = result['metadatas'][0][0]

    def event_stream():        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            messages=[
                {"role": "system", "content": 
                    """너는 항공대학교에 대한 정보를 간략하고 꼼꼼하게 설명해주는 챗봇이야. 
                    기반정보를 이용해서만 대답해. 기반정보에 없는 내용은 답변에 포함하지마."""},
                {"role": "system", "content": "내가 준 날짜를 기반으로 대답해"},
                {"role": "assistant", "content": "학식은 주말에도 운영한다."},
                {"role": "assistant", "content": f"오늘 날짜와 요일 : {date}, {day_of_week}"},
                {"role": "assistant", "content": f"기반정보: {content_origin}"},
                {"role": "user", "content": question}
            ],
            stream=True
        )
        
        for line in response:
            chunk = line['choices'][0].get('delta', {}).get('content', '')
            if chunk:
                data_to_send = {
                    "choices": [{
                        "message": {
                            "content": chunk,
                            "content_origin": content_origin,
                            "metadata": metadata
                        }
                    }]
                }
                yield f"data: {json.dumps(data_to_send)}\n\n"
            
    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    
    
@csrf_exempt
@api_view(['POST'])
def responseSavedChat(request):
    data = json.loads(request.body)
    message = data.get("messages", [])
    keyword = message[0].get("content", "")
    
    queryset = SchoolInfo.objects.filter(keyword=keyword)
    
    content_origin = 'DB'
    metadata = 'DB'
    
    if queryset.exists():
        gpt_response = queryset.first().content
        
        return JsonResponse({
            "choices": [{
                "message": {
                    "content": gpt_response,
                    "content_origin": content_origin,
                    "metadata": metadata
                }
            }]
        })
    
    else:
        return JsonResponse({
            "choices": [{
                "message": {
                    "content": '등록되어 있지 않은 정보입니다.',
                    "content_origin": content_origin,
                    "metadata": metadata
                }
            }]
        })
        
    
        