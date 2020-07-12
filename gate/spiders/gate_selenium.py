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
            question = self.driver.find_element_by_css_selector("div.question-body > div > p").text
            diagram = self.driver.find_element_by_css_selector("div.question-body > div > img").get_attribute("src")
            answer = self.driver.find_element_by_xpath("div.question-solution-container > div.pa-8.text-center")
            options = self.driver.find_elements_by_css_selector("div.question-body > div.question-options")

            if answer is None:
                options = None
                self.driver.find_element_by_css_selector("div.question-actions.text-center > button").click()
                answer = self.driver.find_element_by_css_selector("div.overlay.correct").parent

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

    url = "https://questions.examside.com/" \
          "past-years/gate/question/" \
          "a-connection-is-made-consisting-of-resistance-a" \
          "-in-series-wi-gate-ece-2017-set-2-" \
          "marks-1-5a00e7c2d6ba4.htm"

    data = gate_instance.scrape_question(question_url=url)

    print(data)
