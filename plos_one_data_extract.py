import sys
import traceback
import time
import random
import json
import httpx
from bs4 import BeautifulSoup
import re
from DrissionPage import Chromium, ChromiumOptions

from lxml import etree

from util import get_user_agent, get_proxies
from MyMySQL import MyMySQL

# 最开始获取代理IP
# Method for obtaining dynamic IP addresses
proxies = get_proxies()


# 链接mysql数据库
# Linking MySQL database
g_my_mysql = MyMySQL(MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_CHARSET)


# 翻页来获取所有的list页面的数据
# Flipping to retrieve data from all list pages
def send_list_request(task_url, page_now):
    global proxies
    headers = {
        "Accept":"application/json;charset=UTF-8",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Cookie":"_gcl_au=1.1.1896583641.1736229397; _ga=GA1.3.1494395666.1736229398; _ga=GA1.1.1494395666.1736229398; _CEFT=Q%3D%3D%3D; plosCookieConsentStatus=true; hubspotutk=258d3dc22194de9b6a07ab8085de185d; GCLB=CIe15ZSAq86_LhAD; __hssrc=1; cebs=1; __hstc=57028661.258d3dc22194de9b6a07ab8085de185d.1739933638246.1741339817100.1741435939256.16; _ga_EJPREQGMKT=GS1.1.1741435917.26.1.1741436302.0.0.0; _ga_QC8WLNV09G=GS1.1.1741435917.26.1.1741436302.0.0.0; __gads=ID=fac9569adb363e68:T=1736229398:RT=1741436302:S=ALNI_MYnTnDEDaV4qQrhQlnns-IiNdrIeQ; __gpi=UID=00000fd7e1af4fc3:T=1736229398:RT=1741436302:S=ALNI_MbZNahbjQJGnuXzPFgnDQKjWHQwXg; __eoi=ID=7bd06697147229d4:T=1736229398:RT=1741436302:S=AA-AfjajNk1_GwDkLgAbOi_aOkCx; cebsp_=13; _ga_TJKG55MN8J=GS1.1.1741435917.26.1.1741436302.0.0.0; _clck=ige2j%7C2%7Cfu3%7C0%7C1833; _clsk=fyqnw9%7C1741580299995%7C1%7C0%7Ct.clarity.ms%2Fcollect; _ce.s=v~03b21832f1517521794edf5e62bd9fde7d648ec0~lcw~1741580299109~vir~returning~lva~1741436302647~vpv~6~as~false~v11ls~350f5550-ccbc-11ef-8840-f5f88164b7e6~v11.fhb~1741435939349~v11.lhb~1741436122164~v11.cs~400936~v11.s~95273730-fc16-11ef-bf7d-7d1509d6fc68~v11.sla~1741441906190~gtrk.la~m82jxz6t~v11.send~1741580306034~lcw~1741580306034",
        "Newrelic": 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjgwNDI4MyIsImFwIjoiNDAyNzAzNjc0IiwiaWQiOiI5MjFhZmY2OGMzNjEwOTBjIiwidHIiOiI1ZTE3YWEyOTMxOTkwYTI3Y2JlNjJhZmVlODlhZWI3MCIsInRpIjoxNzE3NTAxOTMzNDY3fX0=',
        # "If-Modified-Since":"Thu, 16 May 2024 00:41:58 GMT",
        "Referer":"https://journals.plos.org/plosone/search?filterJournals=PLoSONE&filterArticleTypes=Research%20Article&resultsPerPage=60&unformattedQuery=publication_date%3A%5B2011-01-01T00%3A00%3A00Z%20TO%202023-12-31T23%3A59%3A59Z%5D&q=publication_date%3A%5B2011-01-01T00%3A00%3A00Z%20TO%202023-12-31T23%3A59%3A59Z%5D&page=" + str(page_now),
        "Sec-Ch-Ua":'"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "Sec-Ch-Ua-Mobile":'?0',
        "Sec-Ch-Ua-Platform":'"Windows"',
        "Sec-Fetch-Dest":'empty',
        "Sec-Fetch-Mode":'cors',
        "Sec-Fetch-Site":'same-origin',
        "Traceparent":'00-5e17aa2931990a27cbe62afee89aeb70-921aff68c361090c-01',
        "Tracestate":'804283@nr=0-1-804283-402703674-921aff68c361090c----1717501933467',
        "User-Agent": get_user_agent(),
        "X-Requested-With":'XMLHttpRequest'
    }

    params = {
        'filterJournals': 'PLoSONE',
        'filterArticleTypes': 'Research Article',
        'resultsPerPage': '60',
        'unformattedQuery': 'publication_date:[2011-01-01T00:00:00Z TO 2024-12-31T23:59:59Z]',
        'q': 'publication_date:[2011-01-01T00:00:00Z TO 2024-12-31T23:59:59Z]',
        'page': str(page_now)
    }
    while True:
        try:
            print("正在采集第：" + str(page_now) + "页。   当前采集所用IP:" + str(proxies))
            response = httpx.get(task_url, headers=headers, params=params, proxies=proxies)
            # print(response.status_code)
            # print(response.text)
            if response.status_code == 200:
                return response
            else:
                print(response.status_code)
                print("第：" + str(page_now) + "页采集报错！")
                sys.exit()
        except Exception as e:
            traceback.print_exc()
            proxies = get_proxies()
            print("采集失败，切换动态IP！" + str(proxies))
            pass
        time.sleep(30)


# 获取所有的作者详情数据等
# Obtain all author details and data, etc
def send_authors_detail_request(task_url, id):
    global proxies
    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Cache-Control":"max-age=0",
        "Cookie":"_gcl_au=1.1.566128062.1717488850; _ga=GA1.3.751334661.1717488851; _ga=GA1.1.751334661.1717488851; _CEFT=Q%3D%3D%3D; plosCookieConsentStatus=true; _clck=m4s38f%7C2%7Cfmn%7C0%7C1616; _ga_QC8WLNV09G=GS1.1.1718415215.16.1.1718415234.0.0.0; _ga_EJPREQGMKT=GS1.1.1718415215.16.1.1718415234.0.0.0; __gads=ID=3bc61710ad6ac090:T=1717488850:RT=1718415234:S=ALNI_MZrWLuYNfUUbCcravG9fVWEMYkqug; __gpi=UID=00000e40c21562be:T=1717488850:RT=1718415234:S=ALNI_Mat2p3gYMlE0UmCo3HLwjQjCW78DQ; __eoi=ID=aa85a768fe511fb1:T=1717488850:RT=1718415234:S=AA-AfjaK2MI3NqUQkwkTaMMAx3Qa; _ga_TJKG55MN8J=GS1.1.1718415234.16.0.1718415235.0.0.0; _ce.s=v~4155eddce6f967e9f8561de9e0871138922a5f7c~lcw~1718415249729~lva~1718415236109~vpv~6~as~false~v11.fhb~1717488858261~v11.lhb~1717488867131~v11.cs~400936~v11.s~57424f80-2ab7-11ef-8ec1-fd2781ef61cf~v11.sla~1718415250470~gtrk.la~lxfg2kdz~lcw~1718415250470",
        # "If-Modified-Since":"Thu, 16 May 2024 00:41:58 GMT",
        "Sec-Ch-Ua":'"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "Sec-Ch-Ua-Mobile":'?0',
        "Sec-Ch-Ua-Platform":'"Windows"',
        "Sec-Fetch-Dest":'document',
        "Sec-Fetch-Mode":'navigate',
        "Sec-Fetch-Site":'none',
        "Sec-Fetch-User":'?1',
        "Upgrade-Insecure-Requests":'1',
        "User-Agent": get_user_agent(),
    }

    params = {
        'id': id,
    }
    while True:
        try:
            # print("正在采集id：" + str(id) + "   当前采集所用IP:" + str(proxies))
            print("正在采集id：" + str(id) + "!")

            # response = httpx.get(task_url, headers=headers, params=params, proxies=proxies)
            response = httpx.get(task_url, headers=headers, params=params)

            # print(response.status_code)
            # print(response.text)
            if response.status_code == 200:
                return response
            else:
                print(response.status_code)
                print("id：" + str(id) + "采集报错！")
                sys.exit()
        except Exception as e:
            traceback.print_exc()
            # proxies = get_proxies()
            print("采集失败，切换动态IP！" + str(proxies))
            pass
        time.sleep(30)


# 获取所有的peer_review的数据等
# Retrieve all peer-review data, etc
def send_peer_review_request(id):
    global proxies
    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"zh-CN,zh;q=0.9,zh-HK;q=0.8",
        "Cache-Control":"max-age=0",
        "Cookie":"_gcl_au=1.1.1896583641.1736229397; _ga=GA1.3.1494395666.1736229398; _ga=GA1.1.1494395666.1736229398; _CEFT=Q%3D%3D%3D; plosCookieConsentStatus=true; hubspotutk=258d3dc22194de9b6a07ab8085de185d; GCLB=CIe15ZSAq86_LhAD; __hssrc=1; cebs=1; __hstc=57028661.258d3dc22194de9b6a07ab8085de185d.1739933638246.1741339817100.1741435939256.16; _ga_EJPREQGMKT=GS1.1.1741435917.26.1.1741436302.0.0.0; _ga_QC8WLNV09G=GS1.1.1741435917.26.1.1741436302.0.0.0; __gads=ID=fac9569adb363e68:T=1736229398:RT=1741436302:S=ALNI_MYnTnDEDaV4qQrhQlnns-IiNdrIeQ; __gpi=UID=00000fd7e1af4fc3:T=1736229398:RT=1741436302:S=ALNI_MbZNahbjQJGnuXzPFgnDQKjWHQwXg; __eoi=ID=7bd06697147229d4:T=1736229398:RT=1741436302:S=AA-AfjajNk1_GwDkLgAbOi_aOkCx; cebsp_=13; _ga_TJKG55MN8J=GS1.1.1741435917.26.1.1741436302.0.0.0; _clck=ige2j%7C2%7Cfu3%7C0%7C1833; _clsk=fyqnw9%7C1741580299995%7C1%7C0%7Ct.clarity.ms%2Fcollect; _ce.s=v~03b21832f1517521794edf5e62bd9fde7d648ec0~lcw~1741580299109~vir~returning~lva~1741436302647~vpv~6~as~false~v11ls~350f5550-ccbc-11ef-8840-f5f88164b7e6~v11.fhb~1741435939349~v11.lhb~1741436122164~v11.cs~400936~v11.s~95273730-fc16-11ef-bf7d-7d1509d6fc68~v11.sla~1741441906190~gtrk.la~m82jxz6t~v11.send~1741580306034~lcw~1741580306034",
        # "If-Modified-Since":"Thu, 16 May 2024 00:41:58 GMT",
        "Sec-Ch-Ua":'"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "Sec-Ch-Ua-Mobile":'?0',
        "Sec-Ch-Ua-Platform":'"Windows"',
        "Sec-Fetch-Dest":'document',
        "Sec-Fetch-Mode":'navigate',
        "Sec-Fetch-Site":'same-origin',
        "Sec-Fetch-User":'?1',
        "Upgrade-Insecure-Requests":'1',
        "User-Agent": get_user_agent(),
        "Referer": "https://journals.plos.org/plosone/article/authors?id=" + str(id),
        "Priority": "u=0, i"
    }

    params = {
        'id': id,
    }
    while True:
        try:
            # print("正在采集id：" + str(id) + "   当前采集所用IP:" + str(proxies))
            print("正在采集id：" + str(id) + "!")

            task_url = ""
            task_url = "https://journals.plos.org/plosone/article/peerReview"
            # response = httpx.get(task_url, headers=headers, params=params, proxies=proxies)
            response = httpx.get(task_url, headers=headers, params=params)

            # print(response.status_code)
            # print(response.text)
            if response.status_code == 200:
                return response
            elif response.status_code == 404:
                print("id：" + str(id) + f"没有peer review数据！状态码:{str(response.status_code)}")
                return False
            else:
                print("id：" + str(id) + f"采集报错！状态码:{str(response.status_code)}")
                return False
        except Exception as e:
            traceback.print_exc()
            # proxies = get_proxies()
            print("采集失败，切换动态IP！" + str(proxies))
            pass
        time.sleep(30)



# 获取所有的统计数据的方法
# Methods for obtaining all statistical data
def send_count_drission_page(id):
    retry = 3 # 对于一个网页采集失败时重复尝试获取的次数(重新获取动态ip)
    # 请求头用户信息 从请求头列表中随机获取

    '''模拟浏览器'''
    co = ChromiumOptions()
    co.headless()  # 无头模式
    co.set_argument('--start-maximized') # 设置启动时最大化
    co.set_timeouts(10)
    co.set_retry(1)
    # 参数默认值，防止未知exception导致变量为空，后续程序遭到破坏
    text = ""
    final_url = ""

    # 连接浏览器
    chrome_browser = Chromium(co)
    browser_tab = chrome_browser.latest_tab  # 获取Tab对象

    url = "https://journals.plos.org/plosone/article/metrics?id=" + id

    i = 0
    while i < retry:
        try:
            browser_tab.get(url)
            time.sleep(2) # 给需要进行采集的页面留一个缓冲跳转加载的时间 3S

            text = browser_tab.html
            html = BeautifulSoup(text, "lxml")
            if html.body.text is None:
                raise ConnectionAbortedError("nothing get")


            break # success get html and encoding, break the loop and ready for return
        # 当遇到网址带不开的报错时的异常 “selenium.common.exceptions.TimeoutException: Message: Timeout loading page after 300000ms”处理：
        except Exception:
            traceback.print_exc() # 打印错误信息
            chrome_browser.quit() # 关闭驱动程序，释放内存
            # 重新配置浏览器
            # sleep(1)
            '''模拟浏览器'''
            co = ChromiumOptions()
            co.headless()  # 无头模式
            co.set_argument('--start-maximized') # 设置启动时最大化
            co.set_retry(1)
            co.set_timeouts(10)

            # 连接浏览器
            chrome_browser = Chromium(co)
            browser_tab = chrome_browser.latest_tab  # 获取Tab对象

            i += 1
    chrome_browser.quit()

    return text

# 获取所有待采集的期任务的url
def get_all_issues(task_url, page_now, page_total): # 功能完成
    # 如果已经采集到，直接读取文件
    while page_now <= page_total:
        response = send_list_request(task_url, page_now)
        analysis_all_issues(task_url, response.text)
        time.sleep(random.uniform(15,20))
        page_now = page_now + 1

def analysis_all_issues(task_url, response_json):
    response_data = json.loads(response_json)
    search_result = response_data.get("searchResults")
    docs_data = search_result.get("docs")

    res_list = []
    for doc_data in docs_data:
        alm_facebookCount = doc_data.get("alm_facebookCount")
        alm_mendeleyCount = doc_data.get("alm_mendeleyCount")
        alm_scopusCiteCount = doc_data.get("alm_scopusCiteCount")
        alm_twitterCount = doc_data.get("alm_twitterCount")
        article_type = doc_data.get("article_type")
        author_display = json.dumps(doc_data.get("author_display"), ensure_ascii=False)
        counter_total_all = doc_data.get("counter_total_all")
        eissn = doc_data.get("eissn")
        figure_table_caption = json.dumps(doc_data.get("figure_table_caption"), ensure_ascii=False)
        id = doc_data.get("id")
        journalKey = doc_data.get("journalKey")
        journal_key = doc_data.get("journal_key")
        journal_name = doc_data.get("journal_name")
        link = doc_data.get("link")
        publication_date = doc_data.get("publication_date")
        striking_image = doc_data.get("striking_image")
        title = doc_data.get("title")
        title_display = doc_data.get("title_display")
        authors_link = "https://journals.plos.org/plosone/article/authors?id=" + id
        res_list.append((alm_facebookCount, alm_mendeleyCount, alm_scopusCiteCount, alm_twitterCount, article_type, author_display, counter_total_all, eissn, figure_table_caption, id, journalKey, journal_key, journal_name, link, publication_date, striking_image, title, title_display, authors_link))

    insert_sql = 'INSERT INTO plos_one_full_2011_2024_with_peer_review (alm_facebookCount, alm_mendeleyCount, alm_scopusCiteCount, alm_twitterCount, article_type, author_display, counter_total_all, eissn, figure_table_caption, id, journalKey, journal_key, journal_name, link, publication_date, striking_image, title, title_display, authors_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
    g_my_mysql.executemany(insert_sql, res_list)
    print("当前页面数据入库完成！")

# 获取所有的论文数据的方法
def get_all_article_data():
    # 使用current_issue_url传参来跳过之前已经采集过的期任务，能直接从断点开始进行数据采集
    select_sql = "SELECT no, id, authors_link FROM plos_one_full_2011_2024_with_peer_review where is_get_detail = '0' order by no limit 10;"
    task_list = g_my_mysql.select(select_sql)
    while task_list:
        for task in task_list:
            try:
                no = task['no']
                id = task['id']
                authors_link = task['authors_link']
                response = send_authors_detail_request(authors_link, id)
                soup = BeautifulSoup(response.text, "html.parser")
                # 解析页面元素步骤
                # 进行页面元素解析（此处是对所有刊的列表页面中含有的刊链接的url进行采集）
                license_html = soup.find_all("p", attrs={"id": "licenseShort"})
                license = None
                if license_html:
                    license = license_html[0].text

                abstract_html = soup.find_all("meta", attrs={"name": "citation_abstract"})
                abstract = None
                if abstract_html:
                    abstract = abstract_html[0]["content"]

                keywords_html = soup.find_all("meta", attrs={"name": "keywords"})
                keywords = None
                if keywords_html:
                    keywords = keywords_html[0]["content"]

                firstpage_html = soup.find_all("meta", attrs={"name": "citation_firstpage"})
                firstpage = None
                if firstpage_html:
                    firstpage = firstpage_html[0]["content"]

                issue_html = soup.find_all("meta", attrs={"name": "citation_issue"})
                issue = None
                if issue_html:
                    issue = issue_html[0]["content"]

                volume_html = soup.find_all("meta", attrs={"name": "citation_volume"})
                volume = None
                if volume_html:
                    volume = volume_html[0]["content"]

                publisher_html = soup.find_all("meta", attrs={"name": "citation_publisher"})
                publisher = None
                if publisher_html:
                    publisher = publisher_html[0]["content"]

                pdf_url_html = soup.find_all("meta", attrs={"name": "citation_pdf_url"})
                pdf_url = None
                if pdf_url_html:
                    pdf_url = pdf_url_html[0]["content"]


                author_affiliation = None
                all_metas = soup.find_all("meta",attrs={"name": True})
                af = {}
                for each_meta in all_metas:
                    if each_meta['name'] == 'citation_author':
                        author_now = each_meta['content']
                        af[author_now]=[]
                    if each_meta['name'] == 'citation_author_institution':
                        af[author_now].append(each_meta['content'])
                if af != {}:
                    author_affiliation = json.dumps(af, ensure_ascii=False)

                author_roles = None
                author_roles_section = soup.find("section", class_="article-body content authors",recursive=True)
                author_roles_dl = author_roles_section.find("dl")
                author_roles_dt = author_roles_dl.find_all("dt")
                author_roles_dd = author_roles_dl.find_all("dd")
                ar = {}
                for index, author_dt in enumerate(author_roles_dt):
                    value = author_roles_dd[index].find("p", attrs={"id": "authRoles"})
                    if value:
                        ar[author_dt.text.replace("\n","").strip()] = value.text.replace("\n","").replace("Roles","").strip()
                if ar != {}:
                    author_roles = json.dumps(ar, ensure_ascii=False)

                author_contributions = None
                author_contributions_xpath = '//h2[text()="Author Contributions"]//following-sibling::p[1]'
                author_contributions_etree = etree.HTML(response.text, parser=etree.HTMLParser(encoding="utf-8"))
                html_etree_res = author_contributions_etree.xpath(author_contributions_xpath)
                html_etree_data = ""
                for r in html_etree_res:
                    # 如果xpath中是含有/text()的，则结果直接是string，此时就不能etree.tostring了
                    html_etree_data += etree.tostring(r,encoding="utf-8", pretty_print=True, method="html").decode("utf-8")
                author_contributions_soup = BeautifulSoup(html_etree_data, 'html.parser')
                author_contributions = author_contributions_soup.get_text().strip() if author_contributions_soup.get_text() else None


                sql_data = (license, abstract, keywords, author_affiliation, firstpage, issue, volume, publisher, pdf_url, author_roles, author_contributions, no)
                update_sql = "update plos_one_full_2011_2024_with_peer_review set license=%s, abstract=%s, keywords=%s, author_affiliation=%s, firstpage = %s, issue=%s, volume=%s, publisher=%s, pdf_url=%s, author_roles=%s, author_contributions=%s where no = %s;"
                g_my_mysql.execute(update_sql, sql_data)
                update_sql_valid = "update plos_one_full_2011_2024_with_peer_review set is_get_detail='1' where no = %s;"
                g_my_mysql.execute(update_sql_valid, no)
                print("No：" + str(no) + " ID:" + id + "采集完成！")
            except:
                traceback.print_exc()
                update_sql_valid = "update plos_one_full_2011_2024_with_peer_review set is_get_detail='3' where no = %s;"
                g_my_mysql.execute(update_sql_valid, no)
                print("No：" + str(no) + " ID:" + id + "采集失败！")

            time.sleep(1)
        task_list = g_my_mysql.select(select_sql)

    # update_sql = "update elsevier_journal_data.journal_list_data set is_to_task = 1 where is_to_task = 0"
    # g_my_mysql.update(update_sql)
    # print("任务标识位更新成功！")


def starts_with_number_dot(s):
    return bool(re.match(r'^\d.', s))

def get_all_peer_review_data():
    # 使用current_issue_url传参来跳过之前已经采集过的期任务，能直接从断点开始进行数据采集
    select_sql = "SELECT no, id  FROM plos_one_full_2011_2024_with_peer_review where is_get_peer_review = '0' order by no limit 10;"
    task_list = g_my_mysql.select(select_sql)
    while task_list:
        for task in task_list:
            try:
                no = task['no']
                id = task['id']
                response = send_peer_review_request(id)
                # 解析页面元素步骤
                # 进行页面元素解析（此处是对所有刊的列表页面中含有的刊链接的url进行采集）
                # 使用 BeautifulSoup 解析 HTML
                if response:
                    soup = BeautifulSoup(response.text.replace("\n                           "," "), 'lxml')

                    result_dict = {}

                    # 定位所有的tr元素
                    # tbody_xpath = '//tbody[@class="peer-review-accordion"]'
                    tbody_tag = soup.find_all("tbody", class_="peer-review-accordion")
                    if tbody_tag:
                        tr_tags = tbody_tag[0].find_all("tr")
                        section_name_now = ""
                        for tr_tag in tr_tags:
                            tr_class = tr_tag.attrs
                            if 'class' not in tr_class:
                                section_name = ""
                                section_author = ""
                                section_date = ""
                                section_name_tag = tr_tag.find_all("span", class_="letter__title")
                                if section_name_tag:
                                    section_name =  section_name_tag[0].text.replace("\n","").replace("               "," ").replace(" "," ").strip()
                                    result_dict[section_name] = {}
                                    result_dict[section_name]['section_name'] = section_name
                                    section_name_now = ""
                                    section_name_now = section_name
                                section_date_tag = tr_tag.find_all("span", class_="letter__date")
                                if section_date_tag:
                                    section_date =  section_date_tag[0].text.strip()
                                    result_dict[section_name]['section_date'] = section_date
                            else:
                                content_section = {}
                                content_section_name = ""
                                content_section_date = ""
                                content_section_author = []
                                content_section_name_tag = tr_tag.find_all("div", class_="letter__title")
                                if content_section_name_tag:
                                    content_section_a_tag = content_section_name_tag[0].find_all("a")
                                    if content_section_a_tag:
                                        content_section_name = content_section_a_tag[0].text.replace("\n","").strip()
                                        content_section['content_name'] = content_section_name
                                content_section_date_tag = tr_tag.find_all("time", class_="letter__date")
                                if content_section_date_tag:
                                    content_section_date = content_section_date_tag[0].text.strip()
                                    content_section['content_date'] = content_section_date
                                content_section_author_tag = tr_tag.find_all("span", class_="letter__author")
                                if content_section_author_tag:
                                    content_section_author_tag_all = content_section_author_tag[0].find_all('span')
                                    for content_section_author_tag_one in content_section_author_tag_all:
                                        content_section_author.append(content_section_author_tag_one.text.strip())
                                    content_section['content_author'] = content_section_author

                                content_section_content_tag = tr_tag.find_all("div", class_="peer-review-accordion-content")
                                if content_section_content_tag:
                                    content_body_div = content_section_content_tag[0].find_all("div", class_="letter__body")
                                    if content_body_div:
                                        content_section_content = str(content_body_div[0])
                                        content_section['content_all'] = content_section_content


                                result_dict[section_name_now][content_section_name] = content_section

                    try:
                        analysis_list = []
                        os_dl_content_all = result_dict['Original Submission']['Decision Letter']['content_all'].replace("<p>[NOTE: If reviewer comments were submitted as an attachment file,","<p>**********</p><p>[NOTE: If reviewer comments were submitted as an attachment file")
                        os_dl_content_all_bs = BeautifulSoup(os_dl_content_all, 'lxml').find_all("div", class_="letter__body")
                        analysis_str = ""
                        for os_dl_content_all_bs_one in os_dl_content_all_bs[0].children:
                            if os_dl_content_all_bs_one.text == 'Comments to the Author':
                                result_dict['Original Submission']['Decision Letter']['content'] = analysis_str.replace('Comments to the Author',"").replace("\n\n\n", "\n").replace("\n\n","\n").strip('\n')
                                analysis_str = ""
                            elif "**********" in os_dl_content_all_bs_one.text:
                                analysis_str = analysis_str.strip("\n")
                                if analysis_str:
                                    q_a = {
                                        'question':"",
                                        'information':"",
                                        'answers':[]
                                    }

                                    analysis_str_list = analysis_str.replace("\n\n\n", "\n").replace("\n\n","\n").strip("\n").strip().split("\n")
                                    q_a_str_add = ""
                                    for index, analysis_str_list_one in enumerate(analysis_str_list):
                                        q_a_str_add = q_a_str_add + analysis_str_list_one + "\n"
                                        if index == 0:
                                            q_a['question'] = q_a_str_add.strip()
                                            q_a_str_add = ""
                                        elif index < (len(analysis_str_list)-1):
                                            if "Reviewer #" in analysis_str_list[index+1]:
                                                if q_a['information'] == "" and "Reviewer #" not in analysis_str_list[index]:
                                                    q_a['information'] = q_a_str_add.strip()
                                                    q_a_str_add = ""
                                                else:
                                                    q_a['answers'].append(q_a_str_add.strip("\n").strip())
                                                    q_a_str_add = ""
                                        else:
                                            q_a['answers'].append(q_a_str_add.strip("\n").strip())
                                            q_a_str_add = ""
                                    analysis_list.append(q_a)
                                    analysis_str = ""
                            else:
                                analysis_str = analysis_str + os_dl_content_all_bs_one.text.strip() + "\n"
                        result_dict['Original Submission']['Decision Letter']['other'] = analysis_str.replace("\n\n\n", "\n").replace("\n\n","\n").strip("\n").strip()
                        result_dict['Original Submission']['Decision Letter']['Comments to the Author'] = analysis_list
                        # if starts_with_number_dot(os_dl_content_all_bs_one) and comments_to_the_author:
                        #     q_a = {}
                        #     q_a[os_dl_content_all_bs_one.text.strip().strip('\n')] = []
                        #
                        #     analysis_list.append({"1":analysis_str})
                        #     analysis_str = ""
                        # print(os_dl_content_all_bs_one)

                    except:
                        traceback.print_exc()
                        pass


                    json_data = json.dumps(result_dict, ensure_ascii=False)
                    # 将 BeautifulSoup 对象转换为 lxml 对象
                    tree = etree.HTML(str(soup))



                    sql_data = ('1', json_data, no)
                    update_sql = "update plos_one_full_2011_2024_with_peer_review set is_get_peer_review=%s, peer_review_data=%s where no = %s;"
                    g_my_mysql.execute(update_sql, sql_data)
                    print("No：" + str(no) + " ID:" + id + "采集完成！")
                else:
                    print("No：" + str(no) + " ID:" + id + "采集失败！")
                    update_sql_valid = "update plos_one_full_2011_2024_with_peer_review set is_get_peer_review='3' where no = %s;"
                    g_my_mysql.execute(update_sql_valid, no)
            except:
                traceback.print_exc()
                update_sql_valid = "update plos_one_full_2011_2024_with_peer_review set is_get_peer_review='3' where no = %s;"
                g_my_mysql.execute(update_sql_valid, no)
                print("No：" + str(no) + " ID:" + id + "采集失败！")

            time.sleep(0.5)
        task_list = g_my_mysql.select(select_sql)

def get_all_count_data():
    # 使用current_issue_url传参来跳过之前已经采集过的期任务，能直接从断点开始进行数据采集
    select_sql = "SELECT no, id  FROM plos_one_full_2011_2024_with_peer_review where is_get_count = '0' order by no limit 10;"
    task_list = g_my_mysql.select(select_sql)
    while task_list:
        for task in task_list:
            try:
                no = task['no']
                id = task['id']
                response_html = send_count_drission_page(id)
                # 解析页面元素步骤
                # 进行页面元素解析（此处是对所有刊的列表页面中含有的刊链接的url进行采集）
                # 使用 BeautifulSoup 解析 HTML
                if response_html:

                    html = etree.HTML(response_html)
                    almSaves_li_xpath = '//li[@id="almSaves"]/text()'
                    almCitations_li_xpath = '//li[@id="almCitations"]/text()'
                    almViews_li_xpath = '//li[@id="almViews"]/text()'
                    almShares_li_xpath = '//li[@id="almShares"]/text()'

                    almSaves_li_data = html.xpath(almSaves_li_xpath)[0].replace("\n","").replace(",","").strip()
                    almCitations_li_data = html.xpath(almCitations_li_xpath)[0].replace("\n","").replace(",","").strip()
                    almViews_li_data = html.xpath(almViews_li_xpath)[0].replace("\n","").replace(",","").strip()
                    almShares_li_data = html.xpath(almShares_li_xpath)[0].replace("\n","").replace(",","").strip()

                    sql_data = ('1', almSaves_li_data, almCitations_li_data, almViews_li_data, almShares_li_data, no)
                    update_sql = "update plos_one_full_2011_2024_with_peer_review set is_get_count=%s, almSaves=%s, almCitations=%s, almViews=%s, almShares=%s where no = %s;"
                    g_my_mysql.execute(update_sql, sql_data)
                    print("No：" + str(no) + " ID:" + id + "采集完成！")
                else:
                    print("No：" + str(no) + " ID:" + id + "采集失败！")
                    update_sql_valid = "update plos_one_full_2011_2024_with_peer_review set is_get_count='3' where no = %s;"
                    g_my_mysql.execute(update_sql_valid, no)
            except:
                traceback.print_exc()
                # update_sql_valid = "update plos_one_full_2011_2024_with_peer_review set is_get_peer_review='3' where no = %s;"
                # g_my_mysql.execute(update_sql_valid, no)
                # print("No：" + str(no) + " ID:" + id + "采集失败！")

            time.sleep(0.1)
        task_list = g_my_mysql.select(select_sql)


if __name__ == "__main__":
    try:
        # step 1
        task_url = "https://journals.plos.org/plosone/dynamicSearch"
        page_now = 1
        page_total = 4654
        get_all_issues(task_url, page_now, page_total)  # 获取待采集的期列表

        # step 2
        # Retrieve paper data and store it in the database to obtain corresponding author contribution information data
        get_all_article_data()

        # step 3
        get_all_peer_review_data()

        # step 4
        get_all_count_data()

    except Exception as e:
        traceback.print_exc()
        print("出现异常", e)

    except KeyboardInterrupt:
        print("停止爬取")

