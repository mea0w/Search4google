import re
import pandas as pd
import requests
import time
from urllib.parse import quote
from urllib.parse import unquote
from fake_useragent import UserAgent

requests.packages.urllib3.disable_warnings()

headers1 = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3)'}
ext_ct = ['application/pdf', 'application/msword']
proxies0 = {'http': 'socks5://127.0.0.1:10808',
            'https': 'socks5://127.0.0.1:10808'}  # 需要启本地梯子的代理端口，v2默认socks5://127.0.0.1:10808
base_url = 'https://www.google.com/search?'
max_num = 300  # 最大爬取结果条数，为100的整数倍，可以自行设置
d_num = 100  # 每页条目，范围1-100，默认爬最大每页100条
d_hl = 'cn'


def ggSearch(query):
    query_u = quote(query, 'utf-8')
    startime = time.time()
    pages = max_num / d_num
    titles = []
    urls = []
    domains = []
    for page in range(0, int(pages)):
        pa = page + 1
        start = page * 100
        url = f'{base_url}num={d_num}&dl={d_hl}&start={start}&q={query_u}'  # 每页为100个，start为页数判断
        print(url)
        ua = UserAgent().random  # 需要国外的api更新
        headerss = {'User-agent': ua,
                    'connection': 'keep-alive',
                    'Accept-Encoding': 'gzip',
                    'referer': base_url}
        # time.sleep(3)  # 作用不大
        resp = requests.get(url, proxies=proxies0, headers=headerss)
        print(resp.text)
        a = re.compile('<div class=".*?">(<a .*?</div></a>)</div>')  # 处理<a>标签中的数据提取url、title、domain
        htmls = a.findall(resp.text)
        print(len(htmls))#当前页的爬取数量，最后一页会小于100
        if len(htmls) > 0:
            print(query + '   语句Google搜索结果第' + str(pa) + '页')
            for html in htmls:
                html = unquote(html, 'utf-8')
                # print(html)  # 输出正则匹配结果块
                title, url, domain = getValue(html)
                if url:
                    print(title + '-----' + url)
                    titles.append(title)
                    urls.append(url)
                    domains.append(domain)
        else:
            print(query + '   语句Google搜索结果为空或已搜索完毕、尝试切换语法或代理')
            break
    createCsv(query, titles, urls, domains)
    stoptime = time.time()
    cost_time = stoptime - startime
    print('任务完成、花费时间' + str(cost_time))
    print('\n')


def createCsv(query, titles, urls, domains):
    datess = pd.DataFrame({'titles': titles, 'urls': urls, 'domains': domains})
    datess.to_csv(f'{getTime()}' + '(' + f'{escapeChar(query)}' + ').csv', encoding='utf_8_sig')


def getTime():
    now = time.strftime("%m%d-%H%M", time.localtime(time.time()))
    return now


# 为输出的文件转义字符
def escapeChar(query):
    if ':' in query:
        query = query.replace(':', '：')
    if '?' in query:
        query = query.replace('?', '？')
    if '<' in query:
        query = query.replace('<', '《')
    if '>' in query:
        query = query.replace('>', '》')
    if '\\' in query:
        query = query.replace('\\', '。')
    if '/' in query:
        query = query.replace('/', '。')
    if '|' in query:
        query = query.replace('|', '。')
    if '*' in query:
        query = query.replace('*', '。')
    if '"' in query:
        query = query.replace('"', '\'')
    return query[0:30]


def getValue(html):
    res = re.compile(';url=(http.*?)&amp;ved=')
    urll = res.findall(html)
    if urll:
        url = urll[0]
    else:
        url = ''
    titlel = re.findall('<h3 class=".*?"><div class=".*?" style=".*?">(.*?)</div></h3>', html)
    if titlel:
        title = titlel[0]
    else:
        title = ''
    domainl = re.findall('</div></h3><div class=".*?" style=".*?">(.*?) › .*</div></a>', html)
    if domainl:
        domain = domainl[0]
    else:
        domain = ''
    return title, url, domain


# # soup读title
# def getWebtitle(url):
#     try:
#         resp = requests.get(url, headers=headers1, timeout=3, verify=False, allow_redirects=True)
#         if resp.headers['Content-Type'] not in ext_ct:
#             soup = BeautifulSoup(resp.content, 'html.parser', from_encoding='utf-8')
#             try:
#                 title = soup.title.string
#                 return title
#             except Exception as e:
#                 pass
#         else:
#             return None
#     except Exception as e:
#         pass


if __name__ == "__main__":
    try:
        data = open("target-gg.txt", 'r', encoding='utf-8')
    except Exception as e:
        data = open("target-gg.txt", 'r', encoding='GBK')
    querys = data.readlines()
    data.close()
    line = 0
    for query in querys:
        line += 1
        print('爬取target-gg.txt第' + str(line) + '行语句：' + query)
        ggSearch(query.strip())
