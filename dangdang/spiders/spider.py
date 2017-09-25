import scrapy
import requests
from scrapy import Selector
from lxml import etree
from ..items import DangdangItem


class DangDangSpider(scrapy.Spider):
    name = 'dangdangspider'
    redis_key = 'dangdangspider:urls'
    allowed_domains = ['dangdang.com']
    start_urls = 'http://category.dangdang.com/cp01.00.00.00.00.00.html'


    def start_requests(self):
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        headers = {'User-Agent': user_agent}
        yield scrapy.Request(url=self.start_urls, headers=headers, method='GET', callback=self.parse)


    def parse(self, response):
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        headers = {'User-Agent': user_agent}
        lists = response.body.decode('gbk')
        goodslists = response.selector.xpath('//*[@id="navigation"]/ul/li[1]/div[2]/div[1]/div/span')
        for goods in goodslists:
            try:
                category_big = goods.xpath('a/@title').extract()[0] # 大种类
                category_big_id = goods.xpath('a/@href').extract()[0].split('.')[1]  # id
                category_big_url = "http://category.dangdang.com/pg1-cp01.{}.00.00.00.00.html".format(str(category_big_id))
                yield scrapy.Request(url=category_big_url, headers=headers, callback=self.second_parse, meta={"ID1": category_big_id, "ID2": category_big})
            except Exception:
                pass

    def second_parse(self, response):
        '''
        ID1:一级分类ID   ID2:一级分类名称   ID3:二级分类ID  ID4:二级分类名称
        '''
        url = 'http://category.dangdang.com/pg1-cp01.{}.00.00.00.00.html'.format(response.meta["ID1"])
        category_small_content = requests.get(url).content.decode('gbk')
        contents = etree.HTML(category_small_content)
        goodslist = contents.xpath('//*[@id="navigation"]/ul/li[1]/div[2]/div[1]/div/span')
        for goods in goodslist:
            try:
                category_small_name = goods.xpath('a/text()').pop().replace(" ", "").split('(')[0]
                category_small_id = goods.xpath('a/@href').pop().split('.')[2]
                category_small_url = "http://category.dangdang.com/pg1-cp01.{}.{}.00.00.00.html".format(str(response.meta["ID1"]), str(category_small_id))
                yield scrapy.Request(url=category_small_url, callback=self.detail_parse, \
                                     meta={"ID1": response.meta["ID1"], "ID2": response.meta["ID2"], \
                                           "ID3": category_small_id, "ID4": category_small_name})
            except Exception:
                pass

    def detail_parse(self, response):
        for i in range(1, 101):
            url = 'http://category.dangdang.com/pg{}-cp01.{}.{}.00.00.00.html'.format(str(i), response.meta["ID1"], response.meta["ID3"])
            try:
                contents = etree.HTML(requests.get(url).content.decode('gbk'))
                goodslist = contents.xpath('//ul[@class="bigimg"]/li')
                for goods in goodslist:
                    item = DangdangItem()
                    try:
                        item['title'] = goods.xpath('p[1]/a/text()').pop()
                        item['comments'] = goods.xpath('p[5]/a/text()').pop()
                        item['price'] = goods.xpath('p[3]/span[1]/text()').pop()
                        item['discount'] = goods.xpath('p[3]/span[3]/text()').pop().replace('\xa0(', '').replace(')','')
                        item['time'] = goods.xpath('p[6]/span[2]/text()').pop().replace("/", "")
                        item['category_one'] = response.meta["ID2"]  # 种类(大)
                        item['category_two'] = response.meta["ID4"]  # 种类(小)
                    except Exception:
                        pass
                    yield item
            except Exception:
                pass
