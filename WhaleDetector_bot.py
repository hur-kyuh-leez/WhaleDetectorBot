#-*- coding: utf-8 -*-
import bs4 as bs
import requests
import urllib
import time
import gmail.gmail as gmail
import re
from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from PRIVATE_INFO import username, password, telegram_url, sender, eth_address


temp_Token_symbol = "Token Symbol: (.+?)Token"
temp_Token_name ="Token Name: (.+?)Token"
temp_amount = "The address %s received (.+?) " % eth_address



def bot():
    g = gmail.login(username, password)

    if g.logged_in:
        print('Mail log in success')


        # 특정 발신자가 보낸 메일 중 읽지 않은 메일을 가져옴,
        unread = g.inbox().mail(unread=True, sender=sender)
        if len(unread) > 0:
            unread[-1].fetch()
            body = unread[-1].body
            body = body.replace("=", "")
            body = body.replace("\r\n", "")
            KR_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')
            Token_symbol = re.findall(temp_Token_symbol, body, flags=0)
            Token_name = re.findall(temp_Token_name, body, flags=0)
            amount = re.findall(temp_amount, body, flags=0)
            Token_symbol = Token_symbol[0]
            Token_name = Token_name[0]
            amount = amount[0]

            for i in range(len(amount)):
                if amount[i].isalpha() == True:
                    print(amount[i])
                    amount = amount.replace(amount[i], '.')
                    print(amount)

            amount = float(amount.replace(",", ""))

            print('Body: ' + body)
            print('Amount:', amount)
            print('Token_symbol: ' + Token_symbol)
            print('Token Name: ' + Token_name)

            # getting coin info
            source = urllib.urlopen("https://coinmarketcap.com/ko/currencies/%s/" % Token_name).read()
            soup = bs.BeautifulSoup(source, 'html.parser')
            findthis = str(soup.select('body > div.container.main-section > div > div.col-lg-10 > div.row.bottom-margin-2x > div.col-sm-8.col-sm-push-4 > div:nth-of-type(4) > div > span'))
            circulating_supply = re.findall('data-format-value="(.+?)"', findthis, re.DOTALL)
            findthis = str(soup.select(
                'body > div.container.main-section > div > div.col-lg-10 > div.details-panel.flex-container.bottom-margin-2x > div.details-panel-item--marketcap-stats.flex-container > div:nth-of-type(3) > div > span'))

            if len(circulating_supply) > 0:

                findthis = str(soup.select('#quote_price'))
                USD_price = re.findall('data-usd="(.+?)"', findthis, re.DOTALL)
                USD_price = float(USD_price[0])

                findthis = str(soup.select('body > div.container.main-section > div > div.col-lg-10 > div:nth-of-type(4) > div.col-xs-6.col-sm-8.col-md-4.text-left > span:nth-of-type(3)'))
                BTC_price = re.findall('data-format-value="(.+?)"', findthis, re.DOTALL)
                BTC_price = float(BTC_price[0])


                circulating_supply = float(circulating_supply[0])
                amount_to_circulating_supply = amount / circulating_supply * 100
                amount_to_circulating_supply = "{0:.2f}".format(amount_to_circulating_supply)

                Total_Bought_in_USD = USD_price * amount
                Suggested_buy_price = BTC_price * .70
                Suggested_sell_price = BTC_price * .90

                string = '%s Seoul Time(서울시간)\n' \
                         'Whale Detected(고래발견)!\n' \
                         'COIN(코인): %s\n' \
                         'Amount Bought(매수량): %s\n' \
                         'Amount to Liquidable Volume(매수량/유동거래량): %s%s\n' \
                         'USD price(달라가격으로): $%s\n' \
                         'BTC price(비트가격으로): %s\n' \
                         'Bought in USD(매수액): $%s\n' \
                         'Suggested Buy Price(추천매수가): BTC %s\n' \
                         'Suggested Sell Price(추천매도가): BTC %s\n' \
                         'telegram(탤래그램) @CryptoWhale_messenger' \
                         % (KR_time, Token_symbol, amount, amount_to_circulating_supply, '%', USD_price, BTC_price,
                            Total_Bought_in_USD, Suggested_buy_price, Suggested_sell_price)

            else:
                string = '%s Seoul Time(서울시간)\n' \
                        'Whale Detected(고래발견)!\n' \
                        'COIN(코인): %s\n' \
                         'Amount Bought(매수량): %s\n' \
                         'telegram(탤래그램) @CryptoWhale_messenger' \
                                 %(KR_time, Token_symbol, amount)
            print(string)
            send_this = '%s%s' % (telegram_url, string)
            print(send_this)
            r = requests.post(send_this)
            print(r.text)
            print(r.status_code)
            unread[-1].read()

        # 종료
        g.logout







def main():
    """Run tick() at the interval of every ten seconds."""
    scheduler = BlockingScheduler()
    scheduler.add_job(bot, 'interval', seconds=3, max_instances=3)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    main()