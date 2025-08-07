user_agents = [
    # Google Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-G990U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.106 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.107 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.103 Safari/537.36",

    # Mozilla Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Linux; Android 13; SM-A717F) Gecko/115.0 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",

    # Apple Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.5 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.5 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.5 Safari/537.36",

    # Microsoft Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36 Edg/114.0.5735.110",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.141 Safari/537.36 Edg/113.0.5672.141",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.101 Safari/537.36 Edg/114.0.5735.101",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.129 Safari/537.36 Edg/113.0.5672.129",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.124 Safari/537.36 Edg/114.0.5735.124",

    # Mobile Chrome
    "Mozilla/5.0 (Linux; Android 14; Pixel 7; rv:114.0) Gecko/114.0 Firefox/114.0",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; AS; IEMobile/11.0; ARM) like Gecko",
    "Mozilla/5.0 (Linux; Android 13; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.98 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A535F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.115 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A215U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.75 Mobile Safari/537.36",

    # Mobile Firefox
    "Mozilla/5.0 (Android 13; Mobile; rv:114.0) Gecko/114.0 Firefox/114.0",
    "Mozilla/5.0 (Android 12; Mobile; rv:115.0) Gecko/115.0 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 13; SM-A517F) Gecko/115.0 Firefox/115.0 Mobile",
    "Mozilla/5.0 (Linux; Android 14; Pixel 6) Gecko/115.0 Firefox/115.0 Mobile",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; AS; IEMobile/11.0; ARM) like Gecko",

    # Mobile Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.1 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.7 Safari/537.36",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.4 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.2 Safari/537.36",

    # Mobile Devices (additional)
    "Mozilla/5.0 (Linux; Android 11; SM-A705F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.79 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; AS; IEMobile/10.0; ARM) like Gecko",
    "Mozilla/5.0 (Linux; Android 11; SM-A515U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.84 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A032F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.97 Mobile Safari/537.36",

    # Tablet Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.120 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.4 Safari/537.36",
    "Mozilla/5.0 (Android 13; Tablet; SM-T865) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.100 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.4 Safari/537.36",
    "Mozilla/5.0 (Android 13; Tablet; SM-T395) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.88 Safari/537.36",

    # Tablet Firefox
    "Mozilla/5.0 (Linux; Android 11; SM-T550) Gecko/113.0 Firefox/113.0",
    "Mozilla/5.0 (Linux; Android 10; SM-T590) Gecko/115.0 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 14; SM-T730) Gecko/115.0 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 13; SM-T870) Gecko/115.0 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/116.0 Safari/537.36"
]
