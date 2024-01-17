import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver import ActionChains

# Парсим все картинки с окна просмотра Вконтакте
def parse_img(browser):
    # Сначала даем прогрузиться странице
    time.sleep(2.5)
    # Пытаемся узнать на старте, какое максимальное количество картинок и текущее кол-во картинок
    try:
        count_text_raw = browser.find_element(By.CLASS_NAME, 'pv_counter')
        count_text = count_text_raw.text
        count_massive = count_text.split(' ')
        current_count = int(count_massive[0])
        max_count = int(count_massive[2])
    except:
        current_count = 1
        max_count = 318
    print(f'current_count: {current_count}, max_count: {max_count}')
    # парсим все картинки и сохраняем на компьютер
    while current_count <= max_count:
        time.sleep(0.5)
        src_image = browser.find_element(By.TAG_NAME, 'img').get_attribute('src')
        img_data = requests.get(src_image).content
        image_name_raw = src_image.split('/')[-1]
        jpg_int = image_name_raw.find('.jpg')
        image_name = image_name_raw[0:jpg_int]
        # Сохраняем на компьютер
        with open(image_name + '.jpg', 'wb') as handler:
            handler.write(img_data)
        # Останавливаемся
        if current_count == max_count:
            break
        # переключаем на следующую картинку
        current_count += 1
        need_picture = browser.find_element(By.ID, 'pv_photo')
        need_picture.click()
        time.sleep(1.5)

def parse_all_images_main(browser, action):
    # Окно браузера во весь экран
    browser.maximize_window()
    # Дергаем контейнер с динамической прокруткой для картинок
    whole_wall = browser.find_element(By.CLASS_NAME, 'post_media')
    # Узнаем ее длину
    old_height = whole_wall.size['height']
    time.sleep(2)
    # Скроллим до самого конца, т.е. когда высота контейнера после прокрутки не меняется
    while True:
        action.scroll_by_amount(delta_x=0, delta_y=2000).perform()
        time.sleep(2)
        current_wall = browser.find_element(By.CLASS_NAME, 'post_media')
        new_height = current_wall.size['height']
        if new_height == old_height:
            break
        old_height = new_height
    # дергаем все картинки на странице для счетчика
    all_pictures = browser.find_elements(By.CLASS_NAME, 'photos_photo_small')
    count_images = len(all_pictures)
    return count_images

need_page = 'https://vk.com/im?sel=c80&w=historyc80_photo'

with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install())) as browser:
    action = ActionChains(browser)
    # Открываем страницу
    need_url = need_page
    browser.get(need_url)
    # Задержка в 30 секунд нужна для авторизации через qr. К сожалению, я не нашел актуального способа авторизации
    time.sleep(30)
    # Узнаем кол-во картинок
    count_images = parse_all_images_main(browser, action)
    # Парсим сначала первые 300 картинок
    first_picture = browser.find_element(By.CLASS_NAME, 'photos_photo_small')
    first_picture.click()
    time.sleep(15)
    parse_img(browser)
    # Возвращаемся на страницу с картинками
    browser.get(need_url)
    max_global_count = int(count_images / 318)+1
    current_global_count = 1
    # считываем циклом картинки по 300+ страниц
    while current_global_count < max_global_count:
        found_img_index = current_global_count * 318
        all_pictures = browser.find_elements(By.CLASS_NAME, 'photos_photo_small')
        all_pictures_count = len(all_pictures)
        # Циклом прокручиваем до новых 300+ картинок
        while all_pictures_count <= found_img_index:
            action.scroll_by_amount(delta_x=0, delta_y=2000).perform()
            time.sleep(2)
            all_pictures = browser.find_elements(By.CLASS_NAME, 'photos_photo_small')
            all_pictures_count = len(all_pictures)
            time.sleep(2)
        # Находим 300+ картинку для парсинга новой порции
        all_pictures = browser.find_elements(By.CLASS_NAME, 'photos_row')
        all_pictures[(current_global_count*318)-1].click()
        time.sleep(15)
        parse_img(browser)
        browser.get(need_url)
        current_global_count+=1

