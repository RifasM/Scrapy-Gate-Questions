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

    def parse(self, response):
        for course in response.css("div.pa-8-top"):
            branch = course.css("div.text-center.pa-4.ma-4-top-bottom::text").extract_first()
            link = course.css("a.no-link.text-bold.pa-8-top-bottom.purple-600.flex-col-xs-6.red-500-hover-bg.round::attr(href)").extract_first()

            yield scrapy.Request(response.urljoin(link), callback=self.parse_topic)

    def parse_topic(self, response):
        for topics in response.css("div.content>ul"):
            topic = topics.css("li>div.title::text").extract_first()
            for sub_topic in topics.css("li"):
                sub_topic_link = sub_topic.css("a::attr(href)").extract_first()
                sub_topic_name = sub_topic.css("a>div::text").extract()
                yield scrapy.Request(response.urljoin(sub_topic_link), callback=self.parse_questions)

    def parse_questions(self, response):
        for questions in response.css("div.pa-8 > div.flex-row-wrap > div.flex-col-xs-12.flex-col-sm-6.flex-col-4.flex-col-lg-4.flex-col-xlg-4>div"):
            link = questions.css("div.text-right.pa-4>a::attr(href)").extract_first()
            link = response.urljoin(link)
            if re.match(self.interesting_url, str(link)):
                print(">>> Matched\n\tYielding")
                yield {
                    "link": link
                }



