import requests
from bs4 import BeautifulSoup as bs
import pymongo
import  re

headers = {'accept': '*/*',
           'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
db_address = 'localhost'
db_port = 27017
db_name = 'hh_parse_data'
coll_name = 'hhru'


def hhru_parse(base_url, header, search_parr):
    jobs_loc = []
    session = requests.Session()
    request = session.get(base_url, headers=header)
    if request.status_code == 200:
        while True:
            soup = bs(request.content, 'html.parser')
            divs = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
            for div in divs:
                title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                compensation = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                if compensation == None:  # Если зарплата не указана
                    compensation = ''
                else:
                    compensation = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
                href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                text1 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
                text2 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
                content = text1 + '  ' + text2
                all_txt = [title, compensation, company, content, href, search_parr]
                jobs_loc.append(all_txt)

            nextPage = soup.find("a", {"data-qa": "pager-next"})
            #print(nextPage)
            if nextPage is not None:
                base_url = url_base + nextPage.attrs["href"]
                request = session.get(base_url, headers=header)
            else:
                break
        return jobs_loc
    else:
        print('error')


def hhru_write_db(connect, port, db, coll, job_list):
    conn = pymongo.MongoClient(connect, port)
    db = conn[db]
    coll = db[coll]
    coll.remove({"_search_parr": job_list[0][5]})
    for i in job_list:
        doc = {"_job_name": i[0],
               "_salary": i[1],
               "_company": i[2],
               "_description": i[3],
               "_link": i[4],
               "_search_parr": i[5]
               }
        coll.save(doc)

def salary_calc_avg(connect, port, db, coll,search_value):
    conn = pymongo.MongoClient(connect, port)
    db = conn[db]
    coll = db[coll]
    avg_salary = 0
    count = 0

    for item in coll.find({"_search_parr": search_value}):
       # print(re.sub("[^-0-9]", "", item["_salary"]).split('-'))
        avg_el = re.sub("[^-0-9]", "", item["_salary"]).split('-')
        if len(avg_el) == 2:
            avg_salary = (int(avg_el[0] or 0) + int(avg_el[1] or 0))/2 + int(avg_salary)
        else:
            avg_salary = int(avg_el[0] or 0) + int(avg_salary)
        if int(re.sub("[^0-9]", "", item["_salary"]) or 0) > 0:
            count = count + 1
   # print(avg_salary/count)
    #print(count)
    if count == 0:
        return 0
    else:
        return avg_salary/count

exit_flag = False
flag_country = False
flag_prof = False
flag_period = False

print('Вас приветствует программа для подсчёта среднего уровня зарплаты для введенной должности')
while (not exit_flag):
    if not flag_country:
        print('Введите номер региона вашего проживания (Пермский край - 1317):')
        search_area = input() #'1317'
    if not flag_prof:
        print('Введите наименование должности (или ключевое слово для поиска набора профессий):')
        search_value = input()# 'python'
    if not flag_period:
        print('Введите период, за который хотите получить информацию (одно число):')
        search_period = input() #'30'
    url_base = 'https://perm.hh.ru/'
    url = url_base + 'search/vacancy?area=' + search_area + '&clusters=true&enable_snippets=true&search_period=' + search_period + '&text=' + search_value + '&page=0'  # area=1317 - Пермский край, search_period=30 - период просмотра, page=0 - Номер страницы
    jobs = []

    jobs = hhru_parse(url, headers, search_value)
    print('Данные успешно скачаны')
    hhru_write_db(db_address, db_port, db_name, coll_name, jobs)
    print('Данные успешно обновлены в БД')
    print('Средняя заработная плата по вашему поисковому запросу: ' + str(salary_calc_avg(db_address, db_port, db_name, coll_name, search_value)))
    print('Вы хотите выполнить поиск по другой профессии? Y/N')
    q1 = input()
    if q1 == 'Y':
        flag_country = True
        flag_period = True
    else:
        print('Вы хотите выполнить поиск по всем новым параметрам? Y/N')
        q2 = input()
        if q2 == 'Y':
            flag_country = False
            flag_country = False
        else:
            exit_flag = True
    print('Работа с программой завершена')




