import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import logging
import logging.handlers
from datetime import datetime


class GateSelenium:
    fields = ['question_meta', 'question',
              'diagram', 'answer', 'options']

    def __init__(self):
        options = Options()
        options.headless = True

        # Normal Start
        # self.driver = webdriver.Chrome()

        # Headless Start
        self.driver = webdriver.Chrome(options=options)

        if not os.path.isdir("logs"):
            os.mkdir("logs")
            os.mkdir("logs/scrapy")
            os.mkdir("logs/selenium")

        handler = logging.handlers.WatchedFileHandler(
            os.environ.get("LOGFILE", "logs/selenium/gate-selenium-at-" +
                           datetime.now().strftime("%Y-%m-%d %H-%M-%S") +
                           ".log"))
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        handler.setFormatter(formatter)
        self.root = logging.getLogger("selenium-logger")
        self.root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        self.root.addHandler(handler)

    def scrape_question(self, question_url):
        self.driver.get(question_url)

        meta = None
        question = None
        diagrams = None
        options = None
        answer = None
        subjective = False

        try:
            meta = self.driver.find_element_by_css_selector("div.question-body > h3").text
        except Exception as e:
            self.root.exception("Meta not Found for: " + str(question_url) + "\nCause: " + str(e))
            meta = None

        try:
            question = self.driver.find_element_by_css_selector("div.question-body > div").get_attribute("innerHTML")
        except Exception as e:
            self.root.error("Questions Could Not be scraped at:" + str(question_url) + "\nCause:" + str(e))
            return False

        """try:
            diagram = self.driver.find_element_by_css_selector("div.question-body > div > img").get_attribute("src")
        except Exception as e:
            print("Diagrams Not Found", e)
            self.print_url(question_url)
            diagram = None"""

        try:
            self.driver.find_element_by_css_selector("div.question-actions.text-center > button").click()
        except Exception as e:
            self.root.error("Button Could Not be clicked at:" + str(question_url) + "\nCause:" + str(e))
            return False

        time.sleep(0.5)

        try:
            try:
                answer = self.driver.find_element_by_css_selector("div.pa-8.text-center>b").text
            except Exception:
                answer = self.driver.find_element_by_css_selector("div.question-solution-container>div.pa-8").text
            if answer == "" or answer is None:
                raise Exception
            self.root.log(logging.INFO, "Subjective Answer Found for " + str(question_url))
            subjective = True
        except Exception as e:
            try:
                self.root.log(logging.INFO,
                              "Subjective Answer  Not Found for " + str(question_url) + "\nCause: " + str(e))
                answer = self.driver.find_element_by_css_selector(
                    "div.overlay.correct").find_element_by_xpath("..").find_element_by_css_selector(
                    "div.ma-4.flex.flex-center-xs.flex-middle-xs.primary-color-bg.green-500-bg").text
                self.root.log(logging.INFO, "Objective Answer Found for " + str(question_url))
            except Exception as e:
                self.root.error("Answer Could not be Obtained at " + str(question_url) + "\nCause: " + str(e))
                return False

        if not subjective:
            top = self.driver.find_element_by_css_selector(
                "div.overlay.correct").find_element_by_xpath("..").find_element_by_xpath("..")
            try:
                options = top.find_elements_by_css_selector(
                    "div.pa-4>span.mjx-chtml.MathJax_CHTML")
                if len(options) == 0:
                    raise Exception
                options = [option.get_attribute("innerHTML") for option in options]
                self.root.log(logging.INFO, "MathXML Options Obtained at " + str(question_url))
            except Exception as e:
                try:
                    options = top.find_elements_by_css_selector(
                        "div.pa-4>img")
                    options = [option.get_attribute("src") for option in options]
                    self.root.log(logging.INFO,
                                  "No MathXML Options Obtained at " + str(question_url) + "\nCause: " + str(e))
                    if len(options) == 0:
                        raise Exception
                    self.root.log(logging.INFO, "Image Options Obtained at " + str(question_url))
                except Exception as e:
                    try:
                        options = top.find_elements_by_css_selector(
                            "div.pa-4")
                        options = [option.text for option in options]
                        self.root.log(logging.INFO, "No MathXML or Image Options Found at " +
                                      str(question_url) +
                                      "\nCause: " + str(e) + "\nObtained Textual options Instead")
                    except Exception as e:
                        options = []
                        self.root.warning("WARNING!! No options found at " + str(question_url) + "\nCause: " + str(e))

        scraped_data = {
            "question_meta": meta,
            "question": question,
            # "diagram": diagram,
            "options": options,
            "answer": answer
        }

        return scraped_data


if __name__ == "__main__":
    gate_instance = GateSelenium()

    no_option_url = "https://questions.examside.com/" \
                    "past-years/gate/question/" \
                    "a-connection-is-made-consisting-of-resistance-a" \
                    "-in-series-wi-gate-ece-2017-set-2-" \
                    "marks-1-5a00e7c2d6ba4.htm"

    option_url = "https://questions.examside.com/" \
                 "past-years/gate/question/" \
                 "in-the-circuit-shown-below-vs-is-a-constant-voltage-" \
                 "source-a-gate-ece-2016-set-2-marks-1" \
                 "-5a05775344abf.htm"

    image_option_url = "https://questions.examside.com/" \
                       "past-years/gate/question/" \
                       "which-one-of-the-following-diagrams-shows-correctly" \
                       "-the-dist-gate-me-1990-marks-1-1oig1ef8ehgstiub.htm"

    text_option_url = "https://questions.examside.com/" \
                      "past-years/gate/question/" \
                      "let-a-be-a-square-matrix-size-n-times-n-consider-" \
                      "the-followi-gate-cse-2014-set-3-marks-1-" \
                      "mzuuovj1fgknvxkg.htm"

    case_1_option_url = "https://questions.examside.com/" \
                        "past-years/gate/question/" \
                        "a-square-waveform-as-shown-in-the-figure-is-" \
                        "applied-across-1-gate-ece-1987-marks-2-" \
                        "5a021c95a2098.htm"

    print("Selenium on question with no Options")
    data = gate_instance.scrape_question(question_url=no_option_url)
    print(data)

    print("Selenium on question with Options")
    data = gate_instance.scrape_question(question_url=option_url)
    print(data)

    print("Selenium on question with Image Options")
    data = gate_instance.scrape_question(question_url=image_option_url)
    print(data)

    print("Selenium on question with Text Options")
    data = gate_instance.scrape_question(question_url=text_option_url)
    print(data)

    print("Selenium on question with Case 1 Options")
    data = gate_instance.scrape_question(question_url=case_1_option_url)
    print(data)
