# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 10:46:02 2018

@author: Carolina
"""

import scrapy
import os
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from google.cloud import storage

class InsideAirbnbSpider(scrapy.Spider):
    name = 'blogspider'
    # Podeis cambiar la url inicial por otra u otras paginas
    start_urls = ['http://insideairbnb.com/get-the-data.html']

    def parse(self, response):
        # Aqui scrapeamos los datos y los imprimimos a un fichero
        for href in response.css('table.madrid tbody tr:not([class="archived"]) td a::attr(href)').extract():
            if 'listings.csv.gz' in href:
                yield Request(
                url=response.urljoin(href),
                callback=self.save_file
            )
        
        
    def save_file(self, response):
        self.logger.info('Saving File %s', response.url)
        client = storage.Client()
        bucket_name = os.environ.get('BUCKET_NAME')
        bucket = client.get_bucket(bucket_name)
        with open('/tmp/airbnb.csv.gz', 'wb') as f:	
            f.write(response.body)
        f.close()
        blob2 = bucket.blob('airbnb.csv.gz')
        blob2.upload_from_filename(filename='/tmp/airbnb.csv.gz')

def main(request): 
    process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    
    process.crawl(InsideAirbnbSpider)
    process.start()
    