from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
import json
import os
import openai
import sys
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
import time
import csv
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys

vectordb = None

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

def initialize_vectordb():
    global vectordb
    
    loader = CSVLoader("./test3_filter.csv")
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1500,
        chunk_overlap = 150
    )
    splits = text_splitter.split_documents(documents)
    
    persist_directory = 'docs/chroma/'
    embedding = OpenAIEmbeddings()
    
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=persist_directory
    )

if vectordb is None:
    initialize_vectordb()

@csrf_exempt
def langchain(request):
    global vectordb
    
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*" 
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"  
        response["Access-Control-Allow-Headers"] = "origin, content-type, accept" 
        return response

    elif request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        question = data["messages"][0]["content"]
        
        docs = vectordb.similarity_search(question, k=3)
        response_content = docs[0].page_content

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": (
                    f"이건 항공대학교에 대한 정보야. "
                    f"내가 준 기반 정보를 바탕으로만 대답해. "
                    f"기반 정보: {response_content} / "
                    f"내 질문: {question}"
                )
            }]
        )
        
        gpt_response = response['choices'][0]['message']['content']

        return JsonResponse({
            "choices": [{
                "message": {
                    "content": gpt_response
                }
            }]
        })

    return JsonResponse({"error": "Only POST requests are allowed."}, status=400)


def index(request):
    return render(request, 'home.html')