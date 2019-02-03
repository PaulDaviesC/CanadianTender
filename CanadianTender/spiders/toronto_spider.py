# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from datetime import datetime

class TorontoSpider(scrapy.Spider):
    name = 'toronto'
    allowed_domains = ['wx.toronto.ca']
    start_urls = ['https://wx.toronto.ca/inter/pmmd/calls.nsf/construction?OpenView']

    def parse(self, response):
      tender_links = response.css("a:contains('View summary')").xpath("@href").getall()
      if len(tender_links) > 0:
        for i in tender_links:
          yield response.follow(i, callback = self.parse_tender)

    def parse_tender(self, response):
      table = pd.read_html(response.body)[6]
      closing_date_string = table[4][3].replace('Noon', 'PM')
      closing_date_string = closing_date_string.replace('Revised', '')
      closing_date_string = closing_date_string.replace('Midnight', 'AM')
      closing_date = datetime.strptime(closing_date_string.strip(), '%B %d, %Y at %I:%M %p')
      yield {
        'closingDate': closing_date,
        'address': table[table[0]=='Email:'][4].values[0],
        'abstract': table[1][2],
        'status': 'Open' if(datetime.now() < closing_date) else 'Closed',
        'linkTo': response.url,
        'organization': table[table[0] == "Client Division:"][1].values[0],
        'categories': table[1][1].split(', ')
      }
