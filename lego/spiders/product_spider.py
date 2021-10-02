from json import load
import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from lego.items import LegoItem
from lego.settings import ITEM_PIPELINES
from ..database import db_connect, load_product_urls


class AvailabilitySpider(scrapy.Spider):
    name = "availability"
    custom_settings = {
        'ITEM_PIPELINES': {
            'lego.pipelines.AvailabilityPipeline': 200,
        }
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)

    def start_requests(self):
        urls = load_product_urls(db_connect())
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: scrapy.http.Response, **kwargs):
        page = response.url
        self.log(page)
        if 'de-de/product' in page:
            if response.css('.eqJexe .hlipzx::text').get():
                self.log('############# Product page: ' +
                         page + ' #############')

                if not 'Altes Produkt' in response.css(".ejRirH .hlipzx::text").get():
                    loader = ItemLoader(item=LegoItem(), response=response)
                    loader.add_css('name', '.eqJexe .hlipzx::text')
                    loader.add_css('price', '.eGdbAY::text')
                    loader.add_css(
                        'product_id', '.ProductDetailsstyles__ProductID-sc-16lgx7x-10.bIKuiP::text')
                    loader.add_css('availability', '.ejRirH .hlipzx::text')
                    loader.add_value('url', response.url)
                    yield loader.load_item()


class LegoProductSpider(scrapy.Spider):
    name = "products"
    custom_settings = {
        'ITEM_PIPELINES': {
            'lego.pipelines.DuplicatesPipeline': 200,
            'lego.pipelines.LegoPipeline': 300,
        }
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.num_of_requests = 0
        self.link_extractor = LinkExtractor(
            allow=[".*lego\.com/de-de.*"], deny=[r".*lego\.com(.*)(\.\w{1,3})$", ".*@lego\.com.*"])

    def start_requests(self):
        urls = [
            'https://www.lego.com/de-de/themes'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: scrapy.http.Response, **kwargs):

        page = response.url
        self.log(page)
        if 'de-de/product' in page:
            if response.css('.eqJexe .hlipzx::text').get():
                self.log('############# Found product page: ' +
                         page + ' #############')

                if not 'Altes Produkt' in response.css(".ejRirH .hlipzx::text").get():
                    loader = ItemLoader(item=LegoItem(), response=response)
                    loader.add_css('name', '.eqJexe .hlipzx::text')
                    loader.add_css('price', '.eGdbAY::text')
                    loader.add_css(
                        'product_id', '.ProductDetailsstyles__ProductID-sc-16lgx7x-10.bIKuiP::text')
                    loader.add_css('availability', '.ejRirH .hlipzx::text')
                    loader.add_value('url', response.url)
                    yield loader.load_item()

        # for next_page in response.css('a::attr(href)').getall():
        for next_page in self.link_extractor.extract_links(response):
            yield response.follow(next_page, self.parse)

        # product name: .eqJexe .hlipzx::text
        # price: .eGdbAY::text
        # product id: response.css('.ProductDetailsstyles__ProductID-sc-16lgx7x-10.bIKuiP::text').get()
        # product url: response.url
        # https://www.lego.com/de-de/product/scrooge-mcduck-huey-dewey-louie-40477
        # Jetzt verfügbar Text: response.css('.ProductOverviewstyles__AvailabilityStatus-sc-1a1az6h-11 .Markup__StyledMarkup-ar1l9g-0.hlipzx::text').get()
        # oder: response.css('.ejRirH .hlipzx::text').getall()

        # >>> response.css(".ejRirH .hlipzx::text").getall()
        # ['Jetzt verfügbar']

        # >>> response.css(".ejRirH .hlipzx::text").getall()
        # ['Vorübergehend nicht auf Lager']

        # .ejRirH .hlipzx::text ['Altes Produkt']

        # de-de
        # keine Dateiendung .pdf

        # .*lego\.com(.*)(\.\w{1,3})$
