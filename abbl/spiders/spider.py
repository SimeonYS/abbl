import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AabblItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class AabblSpider(scrapy.Spider):
	name = 'abbl'
	start_urls = ['https://abbl.com/news-and-events/']

	def parse(self, response):
		articles = response.xpath('//div[@class="career-service-box"]')
		for article in articles:
			date = article.xpath('.//p[@class="news-date-show"]/text()').get()
			post_links = article.xpath('.//a[@class="more-details-press"]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="singlecontent"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))
		if not content:
			content = "Image in the link"

		item = ItemLoader(item=AabblItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
