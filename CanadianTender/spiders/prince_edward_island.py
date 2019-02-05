# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class PrinceEdwardIslandSpider(scrapy.Spider):
    name = 'prince-edward-island'
    allowed_domains = ['www.princeedwardisland.ca']
    start_urls = ["https://www.princeedwardisland.ca/en/tenders"]

    def parse(self, response):
      tender_links = response.css(".view-tender-view div .item-list li a").xpath("@href")
      for i in tender_links:
        yield response.follow(i, callback = self.parse_tender)

      next_page_url = response.css(".pager-next a").xpath("@href").extract_first()
      if next_page_url is not  None:
        yield scrapy.Request(response.urljoin(next_page_url), callback = self.parse)

    def parse_tender(self, response):
      title = response.css(".pane-page-title h1::text").getall()[0]
      date_string = response.css(".field-name-field-t-closing-date .date-display-single::text").getall()[0]
      closing_date = datetime.strptime(date_string.strip(), '%A, %B %d, %Y - %I:%M%p')
      abstract = response.css(".field-name-field-t-notes .field-item p::text").getall()
      organization = response.css(".field-name-field-t-organization .field-item::text").getall()[0]
      categories = response.css(".pane-node-field-t-gsin .field-item::text").getall()
      yield {
        'title': title,
        'closingDate': closing_date,
        'abstract': abstract[0] if len(abstract) > 0 else 'N/A',
        'status': 'Open' if(datetime.now() < closing_date) else 'Closed',
        'linkTo': response.url,
        'organization': organization,
        'categories': categories[0] if len(categories) > 0 else 'N/A'
      }
