
import sys
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

def get_chrome_options():
    """
    Добавление опции headless если в файле headless записано True
    :return: Экземпляр опций
    """
    options = webdriver.ChromeOptions()
    with open('headless.txt', 'r', encoding='utf-8') as file:
        status = file.read()
        if status == 'True':
            options.add_argument('--headless')
    return options


def get_cat_links(options):
    """
    Cобирает ссылки на подкатегории объявлений
    :return: list Список ссылок на подкатегории
    """
    url = 'https://www.petitesannonces.ch/'  # Главная страница сайта
    category_links = []
    print("[+][+][+] В РАБОТЕ [+][+][+]")
    print('Сбор ссылок на подкатегории')
    with webdriver.Chrome(options=options) as browser:
        browser.get(url)
        div_cat = browser.find_element(By.CSS_SELECTOR, 'div.csl').find_element(By.TAG_NAME, 'ul').find_elements(
            By.TAG_NAME, 'li')
        for cat in div_cat:
            cat_link = cat.find_element(By.TAG_NAME, 'a').get_attribute('href')
            with webdriver.Chrome(options=options) as browser1:
                browser1.get(cat_link)
                try:
                    browser1.find_element(By.CSS_SELECTOR, 'ol.rl')
                    button = browser1.find_elements(By.TAG_NAME, 'p')[-1].find_element(By.TAG_NAME, 'a')
                    button.click()
                except:
                    print()
                uls = browser1.find_elements(By.CSS_SELECTOR, 'ul.r')
                try:
                    uls.remove(uls[-1])
                except:
                    category_links.append(cat_link)
                for ul in uls:
                    category_link = ul.find_element(By.TAG_NAME, 'li').find_element(By.TAG_NAME, 'a').get_attribute(
                        'href')
                    category_links.append(category_link)
                    print(f"Собрано {len(category_links)} ссылок подкатегорий")
    print(f"Собрано {len(category_links)} ссылок подкатегорий")
    return category_links


def get_number(category_links, options):
    """
    Собирает номера телефонов из объявлений
    Записывает телефоны в csv файл
    :param category_links: Список ссылок из функции get_cat_links
    :return: None
    """
    count = 0
    print("Cбор номеров из объявлений")
    with open('phones.json', 'r',
              encoding='utf-8') as file:  # открываю файл с сохраненными телефонами и присваиваю в переменную phones
        phones = json.load(file)
    with webdriver.Chrome(options=options) as browser:
        for url in category_links:
            browser.get(url)
            try:
                pages = int(browser.find_elements(By.CSS_SELECTOR, 'a.psc')[
                                -1].text)  # Получает количество страниц из подкатегории
            except:
                pages = 1
            for page in range(1, pages + 1):
                if page == 1:
                    link = url
                else:
                    link = f"{url}?p={page}"
                browser.get(link)
                ads = browser.find_elements(By.CSS_SELECTOR, 'div.ele')
                with webdriver.Chrome(options=options) as browser1:
                    for adv in ads:
                        ad_link = adv.find_element(By.CLASS_NAME, 'elm').find_element(By.TAG_NAME,
                                                                                      'a').get_attribute(
                            'href')
                        browser1.get(ad_link)
                        try:
                            browser1.get(ad_link)
                            button = \
                                browser1.find_element(By.CLASS_NAME, 'cnt').find_elements(By.TAG_NAME,
                                                                                          'tr')[
                                    4].find_elements(By.TAG_NAME, 'td')[1].find_element(By.TAG_NAME, 'a')
                            button.click()
                            phone = \
                                browser1.find_element(By.CLASS_NAME, 'cnt').find_elements(By.TAG_NAME,
                                                                                          'tr')[
                                    4].find_elements(By.TAG_NAME, 'td')[1].find_element(By.TAG_NAME,
                                                                                        'span').text
                            phone = phone.strip().strip('\n')
                            phones_list = phone.split('/n')
                            try:
                                name = \
                                    browser1.find_element(By.CLASS_NAME, 'cnt').find_elements(By.TAG_NAME,
                                                                                              'td')[
                                        2].text
                            except:
                                name = '-'
                            try:
                                location = \
                                    browser1.find_element(By.CLASS_NAME, 'cnt').find_elements(By.TAG_NAME,
                                                                                              'td')[
                                        6].text
                            except:
                                location = '-'
                            for phone in phones_list:
                                if phone not in phones:
                                    phones[phone] = f"{name} {location}"
                                    with open('phones.json', 'w',
                                              encoding='utf-8') as file:  # открываю файл с сохраненными телефонами и присваиваю в переменную phones
                                        json.dump(phones, file, indent=4, ensure_ascii=False)
                                    with open('phones.json', 'r',
                                              encoding='utf-8') as file:  # открываю файл с сохраненными телефонами и присваиваю в переменную phones
                                        phones = json.load(file)
                                    with open('result.csv', 'a', newline='', encoding='utf-8-sig') as file:
                                        writer = csv.writer(file, delimiter=';')
                                        writer.writerow([phone, name, location])
                                    print(phone)
                                else:
                                    continue
                        except:
                            continue

if __name__ == '__main__':
    with open('logging.txt', 'a', encoding='utf-8') as file:
        try:
            options = get_chrome_options()  # Присваивание опций хрома в переменную options
            links = get_cat_links(options)
            get_number(links, options=options)
        except Exception:
            print(sys.exc_info())
            file.write(str(sys.exc_info()))
