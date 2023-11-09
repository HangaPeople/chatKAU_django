import pandas as pd
import chromadb
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
from rest_framework.decorators import api_view
from chatKAU_main.models import SchoolInfo

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

collection = None
ids = []
documents = []
doc_meta = []

def index(request):
    return render(request, 'home.html')


def translate_to_english(text):
    translator = Translator()
    translated = translator.translate(text, src='auto', dest='en')
    return translated.text


def initialize_vectordb():
    global collection
    if collection is not None:
        return
    
    df = pd.read_csv("./kau_data_eng.csv")

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
        ids.append(item['CONTENT'])
        documents.append(item['ENGLISH'])
        
    collection.add(
        documents=documents,
        metadatas=doc_meta,
        ids=ids
    )
    

@csrf_exempt
@api_view(['POST'])  
def langchain(request):
    data = json.loads(request.body.decode("utf-8"))
    question = data["messages"][0]["content"]
    
    english_question = translate_to_english(question)
    print(english_question)
    
    initialize_vectordb()
    
    queryset = SchoolInfo.objects.filter(keyword=question)
    
    if queryset.exists():
        gpt_response = queryset.first().content
        content_origin = 'DB'
        metadata = 'DB'
    
    else:
        result = collection.query(
            query_texts=english_question,
            n_results=2
        )
        
        content_origin = result['ids'][0][0]      
        metadata = result['metadatas'][0][0]
        
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": 
                """너는 항공대학교에 대한 정보를 간략하고 꼼꼼하게 설명해주는 챗봇이야. 
                기반정보를 이용해서만 대답해. 기반정보에 없는 내용은 답변에 포함하지마."""},
            {"role": "assistant", "content": f"기반정보: {content_origin}"},
            {"role": "user", "content": question}
        ])
        gpt_response = response['choices'][0]['message']['content']
    
    return JsonResponse({
        "choices": [{
            "message": {
                "content": gpt_response,
                "content_origin": content_origin,
                "metadata": metadata
            }
        }]
    })