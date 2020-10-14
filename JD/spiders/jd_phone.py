import scrapy
from JD.items import JdItem
import re


class JdPhoneSpider(scrapy.Spider):
    name = 'jd_phone'
    # allowed_domains = ['www.xx.com']
    start_urls = ['https://list.jd.com/list.html?cat=9987,653,655']

    def parse(self, response,**kwargs):
        li_list = response.xpath('//ul[@class="gl-warp clearfix"]/li')
        for li in li_list:
            item = JdItem()
            phone_desc = li.xpath('.//div[@class="p-name p-name-type-3"]/a/em/text()').extract_first().strip()
            phone_price = li.xpath('.//div[@class="p-price"]//i/text()').extract_first()
            phone_link = response.urljoin(li.xpath('.//div[@class="p-name p-name-type-3"]/a/@href').extract_first())
            from_phone = li.xpath('.//span[@class="J_im_icon"]/a/text()').extract_first()
            item['phone_desc'] = phone_desc
            item['phone_price'] = phone_price
            item['phone_link'] = phone_link
            item['from_phone'] = from_phone

            yield item

        # 翻页
        page = int(re.findall('adv_param={page:"(.*?)",page_count:".*?"', response.body.decode())[0])
        count_page = int(re.findall('adv_param={page:".*?",page_count:"(.*?)"', response.body.decode())[0])
        if count_page > page:
            page = page + 1
            next_url = self.start_urls[0] + f'&page={page}'
            print(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse
            )