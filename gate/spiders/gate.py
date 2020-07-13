import time
import urllib
import os

from datetime import datetime
import logging
import logging.handlers
import scrapy
import re
from gate.spiders.gate_selenium import GateSelenium
import pymongo


class GateSpider(scrapy.Spider):
    name = 'gate'
    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):
        # super().__init__(self, *args, **kwargs)
        self.allowed_domains.append('questions.examside.com')
        self.start_urls.append("https://questions.examside.com")

        self.interesting_url = re.compile("https://questions.examside.com"
                                          "/past-years/gate/"
                                          "question/[\\w-]+.htm")

        self.selenium_instance = GateSelenium()

        client = pymongo.MongoClient(
            "mongodb+srv://" + os.environ["MONGO_USER"] + ":"
            + urllib.parse.quote_plus(os.environ["MONGO_PASSWORD"]) +
            "@" + os.environ["MONGO_HOST"] + "/gate?retryWrites=true&w=majority")
        self.db = client.gate

        if not os.path.isdir("logs"):
            os.mkdir("logs")
            os.mkdir("logs/scrapy")
            os.mkdir("logs/selenium")

        handler = logging.handlers.WatchedFileHandler(
            os.environ.get("LOGFILE", "logs/scrapy/gate-scraper-at-" +
                           datetime.now().strftime("%Y-%m-%d %H-%M-%S") +
                           ".log"))
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        handler.setFormatter(formatter)
        self.root = logging.getLogger("gate-logger")
        self.root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        self.root.addHandler(handler)

    def parse(self, response):
        for course in response.css("div.pa-8-top"):
            branch = course.css("div.text-center.pa-4.ma-4-top-bottom::text"). \
                extract_first()
            link = course.css(
                "a.no-link.text-bold.pa-8-top-bottom.purple-600.flex-col-xs-6."
                "red-500-hover-bg.round::attr(href)").extract_first()

            request = scrapy.Request(response.urljoin(link), callback=self.parse_topic)

            request.cb_kwargs["branch"] = branch

            yield request

    def parse_topic(self, response, branch):
        for topics in response.css("div.content>ul"):
            topic = topics.css("li>div.title::text").extract_first()
            for sub_topic in topics.css("li"):
                sub_topic_link = sub_topic.css("a::attr(href)").extract_first()
                sub_topic_name = sub_topic.css("a>div::text").extract()

                request = scrapy.Request(response.urljoin(sub_topic_link),
                                         callback=self.parse_questions)

                request.cb_kwargs["branch"] = branch
                request.cb_kwargs["topic"] = topic
                request.cb_kwargs["sub_topic"] = sub_topic_name

                yield request

    def parse_questions(self, response, branch, topic, sub_topic):
        links = []
        for questions in response.css(
                "div.pa-8 > div.flex-row-wrap > div.flex-col-xs-12.flex-col-sm-6."
                "flex-col-4.flex-col-lg-4.flex-col-xlg-4>div"):
            link = questions.css("div.text-right.pa-4>a::attr(href)").extract_first()
            link = response.urljoin(link)

            if re.match(self.interesting_url, str(link)):
                data = self.selenium_instance.scrape_question(link)

                if not data:
                    data = {
                        "branch": branch,
                        "topic": topic,
                        "sub_topic_name": sub_topic[0],
                        "questions": links
                    }
                    self.db.fallback.insert_one(data)
                    self.root.exception("Data Scrape Failed on " + str(link) + "\nData sent to fallback")

                    exit(1)

                print(">>> Matched\n\tRunning!!")
                links.append(data)

        if len(links) == 0:
            self.root.error("ERROR! No questions on link: "+str(response.urljoin()))
            exit(1)

        print("\t\t>>> Completed\n\tSending!!")
        data = {
            "branch": branch,
            "topic": topic,
            "sub_topic_name": sub_topic[0],
            "questions": links
        }
        self.db.questions.insert_one(data)
        # time.sleep(1)
