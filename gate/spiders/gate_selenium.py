import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class GateSelenium:
    fields = ['question_meta', 'question',
              'diagram', 'answer', 'options']

    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    @staticmethod
    def print_url(question_url):
        print("\tURL:", question_url)

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
            print("Meta Not Found", e)
            self.print_url(question_url)
            meta = None

        try:
            question = self.driver.find_element_by_css_selector("div.question-body > div").get_attribute("innerHTML")
        except Exception as e:
            print("WARNING!! Question not Scraped", e)
            self.print_url(question_url)
            exit(0)

        """try:
            diagram = self.driver.find_element_by_css_selector("div.question-body > div > img").get_attribute("src")
        except Exception as e:
            print("Diagrams Not Found", e)
            self.print_url(question_url)
            diagram = None"""

        try:
            self.driver.find_element_by_css_selector("div.question-actions.text-center > button").click()
        except Exception as e:
            print("WARNING!! Button Could not be clicked", e)
            self.print_url(question_url)
            exit(0)

        # time.sleep(2)

        try:
            answer = self.driver.find_element_by_css_selector("div.pa-8.text-center>b").text
            if answer == "":
                raise Exception
            print("Subjective Answer Found")
            subjective = True
        except Exception as e:
            try:
                print("Subjective Answer Not found", e)
                answer = self.driver.find_element_by_css_selector(
                    "div.overlay.correct").find_element_by_xpath("..").find_element_by_css_selector(
                    "div.ma-4.flex.flex-center-xs.flex-middle-xs.primary-color-bg.green-500-bg").text
                print("Objective Answer Found")
            except Exception as e:
                print("WARNING!! Answer Could not be Obtained", e)
                self.print_url(question_url)
                exit(0)

        if not subjective:
            top = self.driver.find_element_by_css_selector(
                    "div.overlay.correct").find_element_by_xpath("..").find_element_by_xpath("..")
            try:
                options = top.find_elements_by_css_selector(
                    "div.pa-4>span.mjx-chtml.MathJax_CHTML")
                if len(options) == 0:
                    raise Exception
                options = [option.get_attribute("innerHTML") for option in options]
                print("MathXML Options Found")
            except Exception as e:
                try:
                    options = top.find_elements_by_css_selector(
                        "div.pa-4>img")
                    options = [option.get_attribute("src") for option in options]
                    print("No MathXML options found", e)
                    if len(options) == 0:
                        raise Exception
                    print("Obtained Image options")
                    self.print_url(question_url)
                except Exception as e:
                    try:
                        options = top.find_elements_by_css_selector(
                            "div.pa-4")
                        options = [option.text for option in options]
                        print("No MathXML or Image Options Found", e)
                        print("Obtained Textual options")
                        self.print_url(question_url)
                    except Exception as e:
                        options = []
                        print("WARNING!! No options found", e)
                        self.print_url(question_url)

        scraped_data = {
            "question_meta": meta,
            "question": question,
            #"diagram": diagram,
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
