#### Условие задания

Пользователи посещают сайт магазина ```Shop```. 
Они могут приходить из __поисковиков__ (органический трафик), 
приходить по партнерским ссылкам нескольких кэшбек-сервисов: нашего (__Ours__) и других (__Theirs1__, __Theirs2__). 

Примеры логов в БД сервиса Ours, которые собираются скриптом со всех страниц сайта магазина:
1) Органический переход клиента в магазин
```json 
{
	"client_id": "user15",
        "User-Agent": "Firefox 59",
	"document.location": "https://shop.com/products/?id=2",
	"document.referer": "https://yandex.ru/search/?q=купить+котика",
	"date": "2018-04-03T07:59:13.286000Z"
}
```

2) Переход клиента в магазин по партнерской ссылке кэшбек-сервиса
```json 
[
    {
        "client_id": "user15",
        "User-Agent": "Firefox 59",
        "document.location": "https://shop.com/products/?id=2",
        "document.referer": "https://referal.ours.com/?ref=123hexcode",
        "date": "2018-04-04T08:30:14.104000Z"
    },
    {
        "client_id": "user15",
        "User-Agent": "Firefox 59",
        "document.location": "https://shop.com/products/?id=2",
        "document.referer": "https://ad.theirs1.com/?src=q1w2e3r4",
        "date": "2018-04-04T08:45:14.384000Z"
    }
]
```

3) Внутренний переход клиента в магазине
```json 
{
	"client_id": "user15",
	"User-Agent": "Firefox 59",
	"document.location": "https://shop.com/checkout",
	"document.referer": "https://shop.com/products/?id=2",
	"date": "2018-04-04T08:59:16.222000Z"
}
```

Магазин Shop платит кэшбек-сервисам за клиентов, которые перешли по их ссылке, 
оплатили товар и в конце попали на страницу https://shop.com/checkout (“Спасибо за заказ”). 
Комиссия выплачивается по принципу “выигрывает __последний__ кэшбек-сервис, 
после перехода по партнерской ссылке которого клиент __купил__ товар”.

Сервис ```Ours``` хочет по своим логам находить клиентов, которые совершили покупку именно __благодаря ему__. 
Нужно написать программу, которая ищет победившие партнерские ссылки сервиса ```Ours```. 
Учесть различные сценарии поведения клиента на сайте.


ДОПОЛНИТЕЛЬНО (логи):
```json
[
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/",
        "document.referer": "https://referal.ours.com/?ref=0xc0ffee",
        "date": "2018-05-23T18:59:13.286000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/products/?id=10",
        "document.referer": "https://shop.com/",
        "date": "2018-05-23T18:59:20.119000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/products/?id=25",
        "document.referer": "https://shop.com/products/?id=10",
        "date": "2018-05-23T19:04:20.119000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/cart",
        "document.referer": "https://shop.com/products/?id=25",
        "date": "2018-05-23T19:05:13.123000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/checkout",
        "document.referer": "https://shop.com/cart",
        "date": "2018-05-23T19:05:59.224000Z"
    }
]
```

