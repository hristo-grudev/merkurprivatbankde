import scrapy

from scrapy.loader import ItemLoader

from ..items import MerkurprivatbankdeItem
from itemloaders.processors import TakeFirst


class MerkurprivatbankdeSpider(scrapy.Spider):
	name = 'merkurprivatbankde'
	start_urls = ['https://www.merkur-privatbank.de/online-bank/newsletter-archiv.html']

	def parse(self, response):
		post_links = response.xpath('//tbody/tr')
		for post in post_links:
			url = post.xpath('.//a[@class="Stil1"]/@href').get()
			date = post.xpath('.//a[@class="Stil1"]/text()').get()
			title = post.xpath('.//td[@headers="inhalt"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		next_page = response.xpath('//ul[@class="weiterul"]/li/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, title, date):
		description = response.xpath('//div[@class="newsletterContainer"]//p//text()[normalize-space() and not(ancestor::p[@class="buttonContainer"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=MerkurprivatbankdeItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
