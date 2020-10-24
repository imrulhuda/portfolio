# -*- coding: utf-8 -*-
import scrapy
import time


class SeekingalphaSpider(scrapy.Spider):
    name = 'seekingalpha'
    allowed_domains = ['seekingalpha.com']
    start_urls = ['https://seekingalpha.com/earnings/earnings-call-transcripts/0']

    def parse(self, response):
        results = response.xpath("//li[@class='list-group-item article']")
        for result in results:
            yield {
                'title': result.xpath("normalize-space(string(.//h3[@class='list-group-item-heading']))").get(),
                'url': result.xpath(".//h3[@class='list-group-item-heading']//a[@class='dashboard-article-link']/@href").get(),
                'desc': result.xpath("normalize-space(string(.//div[@class='article-desc']))").get(),
                'which_page': response.url
            }
        time.sleep(10)
        print("Sleeping...")
        next_page = response.xpath("//li[@class='next']//a/@href").get()
        if next_page:
            yield scrapy.Request(url=f"https://seekingalpha.com{next_page}",callback=self.parse)
