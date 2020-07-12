import urllib
import os
import signal
from datetime import datetime

import scrapy
import re
from gate.spiders.gate_selenium import GateSelenium
import pymongo


class GateSpider(scrapy.Spider):
    name = 'gate'
    allowed_domains = ['questions.examside.com']
    start_urls = [
        "https://questions.examside.com",
    ]
    interesting_url = re.compile("https://questions.examside.com"
                                 "/past-years/gate/"
                                 "question/[\\w-]+.htm")

    selenium_instance = GateSelenium()

    client = pymongo.MongoClient(
        "mongodb+srv://"+os.environ["MONGO_USER"]+":"
        + urllib.parse.quote_plus(os.environ["MONGO_PASSWORD"]) +
        "@"+os.environ["MONGO_HOST"]+"/gate?retryWrites=true&w=majority")
    db = client.gate

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
                    print("Error in Scraping through Selenium on link", link)
                    print(">> Dumping Current Data to log.")

                    with open("data_at-" + datetime.today().strftime("%Y_%m_%d_%H_%M_%S") + ".txt", "w") as dump_file:
                        data = {
                            "branch": branch,
                            "topic": topic,
                            "sub_topic_name": sub_topic[0],
                            "questions": links
                        }
                        dump_file.write(str(data))

                    os.kill(os.getpid(), signal.SIGINT)

                print(">>> Matched\n\tRunning!!")
                links.append(data)

        if len(links) == 0:
            print("ERROR!! No questions on link: ", response.urljoin())
            os.kill(os.getpid(), signal.SIGINT)

        print("\t\t>>> Completed\n\tSending!!")
        data = {
            "branch": branch,
            "topic": topic,
            "sub_topic_name": sub_topic[0],
            "questions": links
        }
        self.db.questions.insert_one(data)
