"""Self.Py Progress Migration (SPPM).

The self.py course has a half-year cycle (summer/winter). At the end of
a cycle, the old course will be archived (viewable, but no longer
active) and a new course will be opened.

Participants of the old cycle course may continue on new cycle course,
but they need to manually re-answer, or copy, all closed-exercises they
done in old cycle to the new one (29 exercises).

Using selenium (with Chrome driver) we'll migrate self.py course's
progress from old cycle to the new one automatically.


Before using do/check these:
    1. Install selenium package. Can be done by this command:
    `pip install -U selenium`

    2. Install WebDriver for Chrome from:
    https://sites.google.com/a/chromium.org/chromedriver/downloads
    And add its location to system's path. Read more about it here:
    https://www.selenium.dev/documentation/en/webdriver/driver_requirements/

    3. Your Campus IL login's email/password should be in conf.ini file
    at same directory as this file.
    You can copy (or move) conf.ini.sample to conf.ini and edit it.
"""
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from configparser import ConfigParser
import logging

BASE_URL = 'https://courses.campus.gov.il/'
PAGE_LOAD_WAIT = 3
LONG_WAIT = 10

config = {}
driver: Chrome


def campus_il_login():
    """Login to Campus IL website."""
    driver.get(BASE_URL + 'login')
    driver.find_element_by_id("login-email").send_keys(config['email'])
    password_in = driver.find_element_by_id("login-password")
    password_in.send_keys(config['pass'])
    password_in.send_keys(Keys.RETURN)
    logging.debug('Login should have been submitted')
    WebDriverWait(driver, LONG_WAIT).until(lambda d: 'לוח בקרה' in d.title)
    logging.debug(f'login done? title is: {driver.title}')
    logging.info('Logged in to Campus IL')


def goto_exercise(cycle: str, exercise: str):
    """Go to given exercise page of given cycle.

    :param cycle: course cycle url-string (e.g. 2021_2).
    :param exercise: exercise name (e.g. "1.3.1").
    :return: None
    """
    chapter = get_chapter(exercise)
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
    """Fine all submit buttons and click them (unless disabled).

    :param exercise: exercise name (e.g. "1.3.1").
    :return: None
    """
    submit_buttons = driver.find_elements_by_xpath(
        '//div[@class="problem"]//button[@data-value="הגשה" '
        'and not(@disabled="disabled")]'
    )
    for i, but in enumerate(submit_buttons):
        but.click()
        logging.info(f'Submitted Ex {exercise} (sub#{i})')


def import_text_answers(exercise: str):
    """Import text input answer from old cycle to new.

    :param exercise: exercise name (e.g. "1.3.1").
    :return: None
    """
    goto_exercise(config['old_cycle'], exercise)
    problem_inputs = driver.find_elements_by_xpath(
        '//div[@class="problem"]//input[@type="text"]'
    )
    answers = [answer.get_attribute("value") for answer in problem_inputs]
    if max(answers, key=len) == 0:  # no input to import
        return
    goto_exercise(config['new_cycle'], exercise)
    for i, answer in enumerate(answers, 1):
        cur_input = driver.find_element_by_xpath(
            f'(//div[@class="problem"]//input)[{i}]'
        )
        cur_input.clear()
        cur_input.send_keys(answer)
        logging.debug(f'answer#{i}: {answer}')

    submit_answers(exercise)


def import_select_answers(exercise: str):
    """Import select-type answer from old cycle to new.

    :param exercise: exercise name (e.g. "1.3.1").
    :return: None
    """
    goto_exercise(config['old_cycle'], exercise)
    problem_selects = driver.find_elements_by_xpath(
        '//div[@class="problem"]//select'
    )
    selects = [Select(s).first_selected_option.text for s in problem_selects]
    goto_exercise(config['new_cycle'], exercise)
    for i, answer in enumerate(selects, 1):
        Select(driver.find_element_by_xpath(
            f'(//div[@class="problem"]//select)[{i}]'
        )).select_by_visible_text(answer)
        logging.debug(f'select#{i}: {answer}')

    submit_answers(exercise)


def import_clicked_answers(exercise: str, input_type: str):
    """Import radio/checkbox input answer from old cycle to new.

    :param exercise: exercise name (e.g. "1.3.1").
    :param input_type: input type - should be "radio" or "checkbox".
    :return: None
    """
    goto_exercise(config['old_cycle'], exercise)
    problem_inputs = driver.find_elements_by_xpath(
        f'//div[@class="problem"]//input[@type="{input_type}"]'
    )
    inputs = [inp.is_selected() for inp in problem_inputs]
    goto_exercise(config['new_cycle'], exercise)
    for i, answer in enumerate(inputs, 1):
        if not answer:
            continue
        driver.find_element_by_xpath(
            f'(//div[@class="problem"]//input[@type="{input_type}"])[{i}]'
        ).click()
        logging.debug(f'{input_type}#{i} clicked')

    submit_answers(exercise)


def migrate_progression():
    """Traverse relevant exercises, get old cycle answers and submit to new."""
    exercises = {
        'text': ["1.3.1", "3.1.1", "3.3.1", "3.3.2", "3.4.1", "3.4.4", "4.2.1"],
        'select': ["2.1.1", "2.2.1", "2.3.2", "4.1.1", "5.2.1", "5.3.3",
                   "6.1.1", "6.2.1", "7.1.3", "8.3.1"],
        'radio': ["2.1.2", "2.3.1", "2.4.1", "7.1.1", "7.1.2", "8.1.1", "9.2.1"],
        'checkbox': ["5.1.1", "5.3.1", "5.3.2", "6.2.2", "7.2.3"],
    }
    for exercise_type in exercises:
        for exercise in exercises[exercise_type]:
            logging.debug(f'migrate_progression of {exercise} '
                          f'(type: {exercise_type})')
            if len(config['last_exercise']) >= 5 \
                    and exercise > config['last_exercise']:
                logging.debug(f'Skipping Ex#{exercise} as after last exercise '
                              f'to import ({config["last_exercise"]})')
                continue
            if exercise_type == 'text':
                import_text_answers(exercise)
            elif exercise_type == 'select':
                import_select_answers(exercise)
            elif exercise_type in ('radio', 'checkbox'):
                import_clicked_answers(exercise, exercise_type)


def get_chapter(exercise: str) -> str:
    """Extract chapter name from exercise name.

    :param exercise: exercise name (e.g. "1.3.1").
    :return: chapter name (e.g. "1.3").
    """
    return exercise[:-2]


def read_config():
    """Read and set configuration values from conf.ini file.

    Mast have all expected values, or script will exit.
    """
    global config
    cp = ConfigParser()
    try:
        cp.read('./conf.ini')
        config['email'] = cp['LOGIN']['EMAIL']
        config['pass'] = cp['LOGIN']['PASSWD']
        config['old_cycle'] = cp['CYCLES']['OLD']
        config['new_cycle'] = cp['CYCLES']['NEW']
        config['last_exercise'] = cp['EXERCISES']['LAST']
    except Exception as ex:
        logging.fatal(f'Missing or invalid conf.ini data - {ex.__repr__()}')
        raise SystemExit


def initialize():
    """Initialize this script.

    1. Set logging config.
    2. Read and set this script's config.
    3. Initialize Selenium's Chrome webdriver.
    4. Maximize Chrome window.
    """
    global driver
    logging.basicConfig(
        format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO
    )
    read_config()
    driver = Chrome()
    driver.maximize_window()


def main():
    initialize()
    campus_il_login()
    migrate_progression()
    driver.quit()


if __name__ == '__main__':
    main()
