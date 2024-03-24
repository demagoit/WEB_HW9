import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
import json

# items.py
class QuoteSpyderItem(scrapy.Item):
    tags  = scrapy.Field()
    author = scrapy.Field()
    quote = scrapy.Field()

class AuthorSpyderItem(scrapy.Item):
    fullname = scrapy.Field()
    born_date = scrapy.Field()
    born_location = scrapy.Field()
    description = scrapy.Field()

# pipelines.py
class QuoteSpyderPipeline:
    def open_spider(self, spyder):
        self.authors = []
        self.quotes = []

    def close_spider(self, spider):
        with open('authors.json', 'w', encoding='utf-8') as fh:
            json.dump(self.authors, fh, indent=4)

        with open('quotes.json', 'w', encoding='utf-8') as fh:
            json.dump(self.quotes, fh, indent=4)
        
    def process_item(self, item, spider):
        if isinstance(item, QuoteSpyderItem):
            self.quotes.append(item.__dict__['_values'])

        if isinstance(item, AuthorSpyderItem):
            self.authors.append(item.__dict__['_values'])

        return item

# quotes.py
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    custom_settings = {'ITEM_PIPELINES':{QuoteSpyderPipeline: 300}}

    def author_parser(self, response):

        item = AuthorSpyderItem(
                fullname = response.xpath('//h3/text()').get().strip(),
                born_date = response.xpath('//span[@class="author-born-date"]/text()').get().strip(),
                born_location = response.xpath('//span[@class="author-born-location"]/text()').get().strip(),
                description = response.xpath('//div[@class="author-description"]/text()').get().strip()
        )
        yield item
        
    def parse(self, response):
        authors = []
        for div in response.xpath('//div[@class="quote"]'):

            quote = div.xpath('span[@class="text"]/text()').get().strip()
            author = div.xpath('span/small[@class="author"]/text()').get().strip()
            tags = div.xpath('div[@class="tags"]/a/text()').getall()
            item = QuoteSpyderItem(quote=quote, author=author, tags=tags)
            yield item

            if author not in authors:
                author_link = self.start_urls[0] + div.xpath('span/a[text()="(about)"]/@href').get()
                yield scrapy.Request(author_link, callback=self.author_parser)
                
                authors.append(author)
        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            yield scrapy.Request(self.start_urls[0] + next_page)

if __name__ == '__main__':
    proccess = CrawlerProcess()
    proccess.crawl(QuotesSpider)
    proccess.start()