import scrapy
from JD.items import JdItem
import time
import random
import requests
import re
import json
from copy import deepcopy
# ----- 1 导入分布式类
from scrapy_redis.spiders import RedisSpider


# ------2 继承分布式爬虫类
class JdSpider(RedisSpider):
    name = 'jd'

    # -----3 注释start_urls & allowed_domains
    # # allowed_domains = ['jd.com']
    # # 修改起始url
    # start_urls = ['https://book.jd.com/']

    # ----4 设置redis_key
    redis_key = 'py38'

    # --- 5 设置允许域 __init__
    # def __init__(self, *args, **kwargs):
    #     # Dynamically define the allowed domains list.
    #     domain = kwargs.pop('domain', '')
    #     self.allowed_domains = list(filter(None, domain.split(',')))
    #     super(JdSpider, self).__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        data = self.get_data()
        for i in data:

            big_cate = i['categoryName']
            s1 = int(i['fatherCategoryId'])
            s2 = int(i['categoryId'])
            big_cate_link = f'https://channel.jd.com/{s1}-{s2}.html'
            # print(big_cate,big_cate_link)
            small_list = i['sonList']
            for small in small_list:
                item = JdItem()
                small_cate = small['categoryName']
                s3 = int(small['categoryId'])
                s4 = int(small['fatherCategoryId'])
                small_cate_link = f'https://list.jd.com/list.html?cat={s1},{s4},{s3}'
                # print(small_cate,small_cate_link)
                item['big_cate'] = big_cate
                item['big_cate_link'] = big_cate_link
                item['small_cate'] = small_cate
                item['small_cate_link'] = small_cate_link

                yield scrapy.Request(
                    url=item['small_cate_link'],
                    meta={'item': item},
                    callback=self.parse_book_list
                )

    def get_data(self):
        ts = str(int(time.time() * 1000))
        r_num = random.randint(10000, 99999)
        url = 'https://pjapi.jd.com/book/sort'
        callback = f'jsonp_{ts}_{r_num}'
        param = {
            'source': 'bookSort',
            'callback': callback
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.14 Safari/537.36',
            'referer': 'https://book.jd.com/booksort.html',
        }
        data_json = requests.get(url=url, headers=headers, params=param)
        data_json.encoding = 'utf-8'
        data = data_json.content.decode().split('data":')[-1][:-2]
        data = json.loads(data)
        return data

    def parse_book_list(self, response):

        li_list = response.xpath('//ul[@class="gl-warp clearfix"]/li[@ware-type="11"]')
        for li in li_list:
            item = deepcopy(response.meta['item'])
            book_name = li.xpath('./div/div[3]/a/em/text()|.//div[@class="p-name"]/a/em/text()').extract_first()
            author = li.xpath('.//div/div[4]/span[1]//text()').extract()
            author = ''.join(author).replace('\t', '').replace('\n', '').replace('|', '').strip()
            price = li.xpath('./div/div[2]/strong/i/text()|.//div[@class="p-price"]//i/text()').extract_first()
            link = response.urljoin(li.xpath('.//div[@class="p-name"]/a/@href').extract_first())
            item['book_name'] = book_name
            item['author'] = author
            item['price'] = price
            item['link'] = link
            yield item

        # 翻页
        page = re.findall('adv_param={page:"(.*?)",page_count:".*?"', response.body.decode())[0]
        count_page = re.findall('adv_param={page:".*?",page_count:"(.*?)"', response.body.decode())[0]
        if count_page > page:
            page = int(page) + 1
            next_url = response.url + f'&page={page}'
            print(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_book_list,
            )
