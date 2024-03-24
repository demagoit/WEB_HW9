# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from quote_spyder.items import QuoteSpyderItem, AuthorSpyderItem
import json

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
