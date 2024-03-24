import scrapy
from quote_spyder.items import QuoteSpyderItem, AuthorSpyderItem

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

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
