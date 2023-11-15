import pandas as pd
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.http import JsonResponse
from .models import SchoolInfo

@csrf_exempt
@api_view(['POST'])
def crawling_menu(request):
    
    file_path = "./kau_data_eng_major.csv"
    df = pd.read_csv(file_path)
    
    options = Options()
    options.add_argument("headless")
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.kau.ac.kr/web/pages/gc13087b.do")
    
    table = driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[2]/table')
    fourth_row = table.find_element(By.XPATH, './tbody/tr[4]//a')
    fourth_row.click()
    
    driver.implicitly_wait(3)
    
    menu_table = driver.find_element(By.XPATH, '//*[@id="divViewConts"]/table/tbody')    
    rows = menu_table.find_elements(By.TAG_NAME, 'tr')
    
    week = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    
    arr = [[] for _ in range(len(rows[0].find_elements(By.TAG_NAME, 'td')))]
    new_array = []
    
    for i in range(len(rows)):
        x = 0
        row = menu_table.find_element(By.XPATH, f'//*[@id="divViewConts"]/table/tbody/tr[{i + 1}]')
        cells = row.find_elements(By.TAG_NAME, 'td')

        for cell in cells:
            if len(cells) == 1:
                continue
            
            cell_text = cell.text

            if any(day_of_week in cell_text for day_of_week in week):
                if any(row for row in arr if row):  
                    new_array.append(arr)
                arr = [[] for _ in range(len(rows[0].find_elements(By.TAG_NAME, 'td')))]
            
            if cell_text:
                arr[x].append(cell_text)
            x += 1

    if arr:
        new_array.append(arr)

    result_combined = ['\n'.join([' '.join(map(str, row)) for row in sublist]) for sublist in new_array]
    result_str = '\n\n'.join(result_combined)
    result_str = '항공대 일주일 식단표\n\n' + result_str

    UpdateSchoolMenu(result_str)

    row_index = 38
    column_names = ['INDEX', 'KOREAN', 'URL', 'ENGLISH']
    new_data = [row_index, result_str, 'https://www.kau.ac.kr/web/pages/gc13087b.do', 'meal menu']
    
    df.loc[df['INDEX'] == row_index, column_names] = new_data
    df.to_csv(file_path, index=False)

    driver.quit()

    return JsonResponse({"response": "크롤링 성공"})


def UpdateSchoolMenu(new_data):
    old_data = get_object_or_404(SchoolInfo, keyword='학식')
    
    old_data.content = new_data
    old_data.save()
    
    
