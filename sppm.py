"""Self.Py Progress Migration (SPPM)

"""
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from configparser import ConfigParser
import time
import logging

BASE_URL = 'https://courses.campus.gov.il/'
PAGE_LOAD_WAIT = 3
LONG_WAIT = 10

config = {}
driver: Chrome
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO
)


def campus_il_login():
    driver.get(BASE_URL + 'login')  # ?next=/home%2F'
    driver.find_element_by_id("login-email").send_keys(config['email'])
    password_in = driver.find_element_by_id("login-password")
    password_in.send_keys(config['pass'])
    password_in.send_keys(Keys.RETURN)
    WebDriverWait(driver, LONG_WAIT).until(lambda d: 'לוח בקרה' in d.title)
    logging.debug(f'login done? page_title is: {driver.title}')
    logging.info('Logged in to Campus IL')


def goto_exercise(cycle: str, chapter: str, exercise: str):
    driver.get(
        f'{BASE_URL}courses/course-v1:CS+GOV_CS_selfpy101+{cycle}/progress'
    )
    WebDriverWait(driver, LONG_WAIT).until(lambda d: 'התקדמות' in d.title)
    logging.debug(f'At {cycle}/progress? page_title is: {driver.title}')

    chapter_link = driver.find_element_by_xpath(
        f'//a[contains(text(), "{chapter}")]'
    )
    chapter_link.click()
    logging.debug(f'got to chapter {chapter}? page_title is: {driver.title}')

    exercise_but = driver.find_element_by_xpath(
        f'//button[@data-page-title="תרגיל {exercise}"]'
    )
    exercise_but.click()
    logging.debug(f'got to ex {exercise}? page_title is: {driver.title}')


def submit_answers(exercise: str):
    submit_buttons = driver.find_elements_by_xpath(
        '//div[@class="problem"]//button[@data-value="הגשה" '
        'and @disabled!="disabled"]'
    )
    for i, but in enumerate(submit_buttons):
        but.click()
        logging.info(f'Submitted Ex {exercise} (sub#{i})')


def get_chapter(exercise: str) -> str:
    return exercise[:-2]


def import_select_answers(exercise: str):
    chapter = get_chapter(exercise)
    goto_exercise(config['old_cycle'], chapter, exercise)
    problem_selects = driver.find_elements_by_xpath(
        '//div[@class="problem"]//select'
    )
    selects = [Select(s).first_selected_option.text for s in problem_selects]
    goto_exercise(config['new_cycle'], chapter, exercise)
    for i, answer in enumerate(selects, 1):
        Select(driver.find_element_by_xpath(
            f'(//div[@class="problem"]//select)[{i}]'
        )).select_by_visible_text(answer)
        logging.debug(f'select#{i}: {answer}')

    submit_answers(exercise)


def import_radio_answers(exercise: str):
    chapter = get_chapter(exercise)
    goto_exercise(config['old_cycle'], chapter, exercise)
    problem_radios = driver.find_elements_by_xpath(
        '//div[@class="problem"]//input[@type="radio"]'
    )
    radios = [radio.is_selected() for radio in problem_radios]
    goto_exercise(config['new_cycle'], chapter, exercise)
    for i, answer in enumerate(radios, 1):
        if not answer:
            continue
        driver.find_element_by_xpath(
            f'(//div[@class="problem"]//input[@type="radio"])[{i}]'
        ).click()
        logging.debug(f'radio#{i} clicked')

    submit_answers(exercise)


def import_text_answers(exercise: str):
    chapter = get_chapter(exercise)
    goto_exercise(config['old_cycle'], chapter, exercise)
    problem_inputs = driver.find_elements_by_xpath(
        '//div[@class="problem"]//input[@type="text"]'
    )
    answers = [answer.get_attribute("value") for answer in problem_inputs]
    if max(answers, key=len) == 0:  # no input to import
        return
    goto_exercise(config['new_cycle'], chapter, exercise)
    for i, answer in enumerate(answers, 1):
        cur_input = driver.find_element_by_xpath(
            f'(//div[@class="problem"]//input)[{i}]'
        )
        cur_input.clear()
        cur_input.send_keys(answer)
        logging.debug(f'answer#{i}: {answer}')

    submit_answers(exercise)


def migrate_progression():
    import_text_answers("1.3.1")
    import_select_answers("2.1.1")
    import_radio_answers("2.1.2")
    import_select_answers("2.2.1")
    import_radio_answers("2.3.1")
    import_select_answers("2.3.2")
    import_radio_answers("2.4.1")
    import_text_answers("3.1.1")
    import_text_answers("3.3.1")
    import_text_answers("3.3.2")
    import_text_answers("3.4.1")
    import_text_answers("3.4.4")
    import_select_answers("4.1.1")
    import_text_answers("4.2.1")


def read_config():
    global config
    cp = ConfigParser()
    try:
        cp.read('./conf.ini')
        config['email'] = cp['LOGIN']['EMAIL']
        config['pass'] = cp['LOGIN']['PASSWD']
        config['old_cycle'] = cp['CYCLES']['OLD']
        config['new_cycle'] = cp['CYCLES']['NEW']
    except Exception as ex:
        logging.fatal(f'Missing or invalid conf.ini data - {ex.__repr__()}')
        raise SystemExit

    # logging.debug(f'config {config}')


def main():
    global driver
    read_config()
    driver = Chrome()
    driver.maximize_window()
    campus_il_login()
    migrate_progression()

    time.sleep(15)
    driver.quit()


if __name__ == '__main__':
    main()
