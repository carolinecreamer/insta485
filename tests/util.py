"""P3 utility functions."""
import re
import bs4
import selenium
import config

INDEX = "index.html"
DREW_PIC = "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg"
JAG_PIC = "/uploads/73ab33bd357c3fd42292487b825880958c595655.jpg"
MIKE_PIC = "/uploads/5ecde7677b83304132cb2871516ea50032ff7a4f.jpg"
JASON_PIC = "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg"
POST_1 = "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg"
POST_2 = "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg"
POST_3 = "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
POST_4 = "/uploads/2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg"

# API ROUTES ########################################
V_1 = '/api/v1/'
V_1P = '/api/v1/p/'

# JavaScript tools ##################################
NODE_MODULES_BIN = "./node_modules/.bin"


def log_in_user(driver, login_url, username=config.AWDEORIO_USER,
                password=config.AWDEORIO_PASS):
    """
    Log in the specified user using the web driver.

    If a user is logged in upon calling, they will be logged out.
    Throws selenium.common.exceptions.WebDriverException if an error occurs
    during login.
    """
    driver.delete_all_cookies()
    try:
        driver.get(login_url)
        name_field = driver.find_element_by_name("username")
        pass_field = driver.find_element_by_name("password")
        name_field.send_keys(username)
        pass_field.send_keys(password)
        submit_button_xpath = "//input[@type='submit' and @value='login']"
        submit_button = driver.find_element_by_xpath(submit_button_xpath)
        submit_button.click()
    except selenium.common.exceptions.WebDriverException as error:
        raise error


def num_links_on_page(driver, link):
    """
    Return the number of links that exist on the current page of the driver.

    If a link does not exist throw
    selenium.common.exceptions.NoSuchElementException.
    """
    try:
        elts = driver.find_elements_by_xpath("//a[@href='{}']".format(link))
    except selenium.common.exceptions.NoSuchElementException:
        return 0
    return len(elts)


def normalize_whitespace(text):
    """Return whitespace-normalized text."""
    return re.sub(r"\s+", " ", text)


def check_for_content(must_contain, must_not_contain, content):
    """Check for content existence and exclusion."""
    passes = True
    for element in must_contain:
        if element not in content:
            passes = False
    for element in must_not_contain:
        if element in content:
            passes = False
    return passes


def get_soup_dict(text):
    """Extract text from soup and normalizes whitespace."""
    soup = bs4.BeautifulSoup(text, "html.parser")

    # Remove style tags
    _ = [s.extract() for s in soup('style')]

    # Parse text, normalizing whitespace
    text = soup.get_text()
    text = normalize_whitespace(text)
    # Check for links
    links = [x.get("href") for x in soup.find_all("a")]
    srcs_a = []
    for anchor in soup.find_all("a"):
        img = anchor.find("img")
        if img:
            srcs_a.append(img.get("src"))
    srcs = [x.get("src") for x in soup.find_all('img')]
    buttons = []
    for button in soup.find_all('form'):
        for submit in button.find_all("input"):
            if submit:
                buttons.append(submit.get("name"))
    soup_dict = {
        "text": text,
        "links": links,
        "srcs": srcs,
        "srcs_a": srcs_a,
        "buttons": buttons
        }
    return soup_dict


def check_header(links):
    """Check for correct header content."""
    # Every page should have these
    passes = False
    if "/" in links and "/explore/" in links and "/u/awdeorio/" in links:
        passes = True
    return passes


def posts_size_page(size_page, num):
    """Return custom url with size, page paremeters."""
    return '{}?{}={}'.format(V_1P, size_page, num)


def posts_comment_like(postid, comment_like=''):
    """Return custom url for post comment."""
    if comment_like:
        return '{}{}/{}/'.format(V_1P, postid, comment_like)
    return '{}{}/'.format(V_1P, postid)


def initialize_errorhandlers(application):
    """Initialize error handlers."""
    from autograder.errorhandler import ERRORS
    application.register_blueprint(ERRORS)
