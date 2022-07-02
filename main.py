from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import csv

URL = 'https://emex.ru/catalogs2/201?sortMode=Rating&sortDirection=2'
HEADERS = {'User-Agent':UserAgent().chrome}

def get_html(url, params = None):
    html = requests.get(url=url, params = params, headers=HEADERS)
    return html.text

def pars_price(raw_price):
    price = ''
    for num in str(raw_price).replace(' ',''):
        if num in '0123456789':
            price += num
    return int(price)

def get_info_from_card(card):
    cards_href = 'https://emex.ru' + card.find('a', class_ = 'p4ohtbh').get('href')
    soup = BeautifulSoup(get_html(cards_href), 'html.parser')

    link = cards_href.strip()
    name = soup.find('h1', class_ = 'sjy7hcx e-titleH1 e-titleH1--themeDefault')
    raw_priсe = soup.find('div', class_ = 'p11cg3qv')
    count = soup.find('div', class_ = 'a1h7y0t8')

    raw_charact = soup.find_all('div', class_='s8d5625')
    charact = {}
    for i in raw_charact:
        params = i.find_all('div', class_ = 's11qy79b')
        for param in params:
            charact.update({param.find('div', class_ = 'sb1iyvc').get_text() : param.find('div', class_ = 's1e7p4qg').get_text().replace('.',',')})
    
    info = {'link': link}
    if name:
        info.update({'name': name.get_text()})
    if raw_priсe:
        info.update({'price': pars_price(raw_priсe.get_text())})
    if count:
        info.update({'count': pars_price(count.get_text())})
    if charact:
        info.update({'charact': charact})
    return info


def get_charact_keys(info_list):
    all_char = []
    for info in info_list:
        for char in list(info['charact'].keys()):
            if not char in all_char:
                all_char += [char]
    return all_char
        


def save_exel(info_list):
    with open('data.csv', 'w', errors="ignore") as file:
        writer = csv.writer(file, lineterminator = '\n', delimiter=';')

        charact_keys = get_charact_keys(info_list)

        writer.writerow(['Index','Name', 'Price', 'Count', *charact_keys, 'Link'])
        for index,info in enumerate(info_list):
            charact_values = []
            for key in charact_keys:
                try:
                    charact_values += [info['charact'][key]]
                except KeyError:
                    charact_values += [' ']

            writer.writerow([index+1,info['name'], info['price'], info['count'], *charact_values, info['link']])

def get_content(html, count_element):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', class_ = 'w53xd89')
    info_cards = []
    if count_element < len(cards):  
        cards = cards[:count_element]
    for index,card in enumerate(cards):
        print(f"Получение элемента {index} из {len(cards)}...")
        info_cards += [get_info_from_card(card)]
    return info_cards 


def main():
    print("Введите URL:\n")
    url = input(">>> ")
    print('\n')
    if url ==  '':
        url = URL
        print(
            "URL не распознан\n"
             "Будет использован URL поумолчанию\n"
         )
    else:
        print(
            "URL распознан\n"
            "Будет использован введенный URL\n"
        )
            

    print("Сколько собрать элементов?")
    print("\n")
    count_element = input(">>> ")
    print("\n")
    if count_element ==  '':
        count_element = 64
        print(
             "Будет использовано количество элементов по умолчанию\n"
        )
    else:
        count_element = int(count_element)
        print(
            f"Будет проводиться поиск по {count_element} элементов\n"
        )

    html = get_html(url)
    info_cards = get_content(html, count_element)

    print("\nДанне успешно собраны\n")
    save_exel(info_cards)
    print("Данне успешно сохранены\n")


if __name__ == '__main__':
    main()

