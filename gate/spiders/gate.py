import scrapy
import re


class GateSpider(scrapy.Spider):
    name = 'gate'
    allowed_domains = ['questions.examside.com']
    start_urls = [
        "https://questions.examside.com",
    ]
    interesting_url = re.compile("https://questions.examside.com"
                                 "/past-years/gate/"
                                 "question/[\\w-]+.htm")

    # links = []

    def parse(self, response):
        anchor = response.css("a::attr(href)").getall()
        for link in anchor:
            link = self.start_urls[0] + link
            if re.match(self.interesting_url, str(link)):
                print(">>> Link found!\n\tAppending")
                # self.links.append(link)
                yield link

        for next_page in anchor:
            yield response.follow(self.start_urls[0] + next_page, self.parse)


# TODO: Implement Callback
#  Reference https://github.com/scrapy/booksbot/blob/master/books/spiders/books.py
