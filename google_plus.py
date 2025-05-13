#!/usr/bin/env python3
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import argparse

# конфиг
END_RESULTS_WORD = 'ничего не найдено'
FILTERS = [
    'google',  # обязательный фильтр, иначе сами ссылки гугла тоже будут парсится
    'rambler',
    'rutube',
    'habr',
    'alfabank',
    'aliexpress',
    'amazon',
    'apple.com',
    'avito',
    'dropbox',
    'dzen',
    'ebay',
    'facebook',
    'gitlab',
    'gosuslugi.ru',
    'linkedin',
    'mail.ru',
    'microsoft',
    'nalog.gov.ru',
    'ozon',
    'paypal',
    'rkn.gov.ru',
    'sber',
    'stripe',
    't.me',
    'tbank',
    'telegram',
    'tiktok',
    'twitter',
    'vk.com',
    'vk.ru',
    'vtb.ru',
    'wildberries',
    'ya.ru',
    'yandex',
    'youtube',
]

BANNER = r'''
   __________  ____  ________    ______   
  / ____/ __ \/ __ \/ ____/ /   / ____/__ 
 / / __/ / / / / / / / __/ /   / __/__/ /_
/ /_/ / /_/ / /_/ / /_/ / /___/ /__/_  __/
\____/\____/\____/\____/_____/_____//_/   
'''

def init_driver():
    options = webdriver.FirefoxOptions()
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override",
                         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Firefox(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []


def extract_domains():
    try:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        unique_domains = set()
        for link in links:
            if not link.startswith(('http://', 'https://')):
                continue
            try:
                parsed = urlparse(link)
                if parsed.netloc:
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    unique_domains.add(base_url)
            except Exception as e:
                print(f"Ошибка при парсинге URL: {e}")
                continue
        return sorted(list(unique_domains))
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def google_request(dork, page_num):
    try:
        if page_num == 1:
            url = f'https://www.google.com/search?q={dork}'
        else:
            url = f'https://www.google.com/search?q={dork}&start={(page_num-1)*10}'
        
        driver.execute_script(f"window.location = '{url}'")
        
        # Ожидание ввода пользователя
        input(f"\033[1;34mPress <ENTER> to continue -> \033[0m")
        print("\x1b[1A\x1b[2K", end='')  # Очистка предыдущей строки
        
        if END_RESULTS_WORD in driver.page_source:
            return False
        return True
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False


def filter_domains(domains):
    filtered_domains = []
    for domain in domains:
        if not any(filter_ in domain for filter_ in FILTERS):
            filtered_domains.append(domain)
    return filtered_domains


def main():
    parser = argparse.ArgumentParser(description="Google parser")
    parser.add_argument("--dorks", help="Файл с дорками", required=True)
    parser.add_argument("--output", help="Файл для вывода (опционально)")
    parser.add_argument("--filter", action="store_true", help="Включить фильтрацию")
    args = parser.parse_args()

    global driver
    driver = init_driver()
    
    try:
        print(f"\033[1;34m{BANNER}\033[0m")
        driver.get("https://www.google.com")
        dorks = read_file(args.dorks)
        if not dorks:
            print("Нет дорков для обработки")
            return

        output_file = args.output if args.output else None
        
        for dork in dorks:
            print(f"Обработка дорка: {dork}")
            for page_num in range(1, 31):
                if not google_request(dork, page_num):
                    break
                
                domains = extract_domains()
                if args.filter:
                    domains = filter_domains(domains)
                
                for domain in domains:
                    print(domain)
                
                if output_file:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        for domain in domains:
                            f.write(f"{domain}\n")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
