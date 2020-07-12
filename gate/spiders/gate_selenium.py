from selenium import webdriver


class GateSelenium:
    fields = ['question_meta', 'question',
              'diagram', 'answer', 'options']

    def __init__(self):
        self.driver = webdriver.Chrome("chromedriver.exe")

    def scrape_question(self, question_url):
        self.driver.get(question_url)
        try:
            meta = self.driver.find_element_by_css_selector("div.question-body > h3").text
            question = self.driver.find_element_by_css_selector("div.question-body > div").get_attribute("innerHTML")
            diagram = self.driver.find_element_by_css_selector("div.question-body > div > img").get_attribute("src")

            self.driver.find_element_by_css_selector("div.question-actions.text-center > button").click()

            answer = self.driver.find_element_by_css_selector("div.pa-8.text-center>b").text
            options = self.driver.find_elements_by_css_selector("div.option-item.flex.ripple.flex-middle-xs>div.pa-4>span.mjx-chtml.MathJax_CHTML")
            options = [option.get_attribute("innerHTML") for option in options]

            if answer is "":
                answer = self.driver.find_element_by_css_selector(
                    "div.overlay.correct").find_element_by_xpath("..").find_element_by_css_selector("div.ma-4.flex.flex-center-xs.flex-middle-xs.primary-color-bg.green-500-bg").text

            scraped_data = {
                "question_meta": meta,
                "question": question,
                "diagram": diagram,
                "options": options,
                "answer": answer
            }

            return scraped_data

        except Exception as e:
            print(e)


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

    print("Selenium on question with no Options")
    data = gate_instance.scrape_question(question_url=no_option_url)
    print(data)

    print("Selenium on question with Options")
    data = gate_instance.scrape_question(question_url=option_url)
    print(data)
