# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    # define the fields for your item here like:
    big_cate = scrapy.Field()
    big_cate_link = scrapy.Field()
    small_cate = scrapy.Field()
    small_cate_link = scrapy.Field()

    book_name = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()

    phone_desc = scrapy.Field()
    phone_price = scrapy.Field()
    phone_link = scrapy.Field()
    from_phone = scrapy.Field()

