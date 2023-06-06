import sys
from PyQt5.QtWidgets import *
from flask import Flask, jsonify, request
import constants
from kiwoom import Kiwoom
from threading import Thread
from router.user import user_bp
from account.account_sender import Kiwoom_Send_Account
from order.trade import Kiwoom_Trade
from market.stick_data_sender import Kiwoom_Price
from flask_restx import Api, Resource, reqparse

app = Flask(__name__)

# api swagger
api = Api(app, version='1.0', title='API 문서', description='Swagger 문서', doc="/api-docs")
test_api = api.namespace('test', description='조회 API')

kiwoom = None
kiwoom_account = None
kiwoom_trade = None
kiwoom_price = None

# api swagger
@test_api.route('/')
class Test(Resource):
    def get(self):
        return 'Hello World!'


# 처음 로그인 요청
@app.route("/login")
def get_login():
    global kiwoom

    if not kiwoom:
        kiwoom = Kiwoom()
    kiwoom.connect_login()
    return jsonify({'result': True})

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 유저 이름, 계좌, id
@app.route("/user/info", methods=['GET'])
def get_user_data():
    global kiwoom

    if not kiwoom:
        return jsonify(0)
    id = kiwoom.get_login_info("USER_ID")
    name = kiwoom.get_login_info("USER_NAME")
    account = kiwoom.get_login_info("ACCNO")

    print(id,name,account)

    if not name and id and account:
        return jsonify({"result" : "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify({"id": id, "name" : name, "account" : account})
# 예수금
@app.route("/user/account/info", methods=['GET'])
def get_user_money():
    result = kiwoom_account.send_detail_account_info(constants.ACCOUNT)

    if not result:
        return jsonify({"result": "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify(result)

# 계좌평가잔고내역요청 - 총수익률,총 매입금액, 수익률
@app.route("/user/account/mystock", methods=['GET'])
def get_user_total_money():
    result = kiwoom_account.send_detail_account_mystock(constants.ACCOUNT)

    if not result:
        return jsonify({"result": "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify(result)


# 계좌별주문체결내역상세요청 - 날짜별 체결내역
@app.route("/user/account/record", methods=['GET'])
def get_user_order_history():
    result = kiwoom_account.send_trading_record(1, constants.ACCOUNT, "1", "0", "")

    if not result:
        return jsonify({"result": "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify(result)

# 계좌수익률요청 - 보유 주식량 확인
@app.route("/user/account/pofit11", methods=['GET'])
def get_user_profit():
    result = kiwoom_account.send_price_earning_ratio(constants.ACCOUNT)

    if not result:
        return jsonify({"result": "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify(result)

# 체결요청
@app.route("/user/account/conclusion", methods=['GET'])
def get_user_conclusion():
    result = kiwoom_account.send_conclude_data(constants.SAMSUNG_CODE,"1","0",constants.ACCOUNT)
    if not result:
        return jsonify({"result": "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify(result)

# 일자별실현손익요청
@app.route("/user/account/day-profit", methods=['GET'])
def get_user_day_profit():
    result = kiwoom_account.send_day_earn_data(constants.ACCOUNT, "20230101", "20230531")
    if not result:
        return jsonify({"result": "정보를 불러오는데 실패했습니다."})
    else:
        return jsonify(result)




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#매매코드


# 매수주문 계좌번호/종목코드/수량/가격/구매타입
@app.route("/order/buy", methods=['POST'])
def send_buy_order():
    data = request.get_json()
    print(data['account'], data['item_code'], data['quantity'],data['price'], data['trading_type'])

    buy_order = kiwoom_trade.send_buy_order(constants.ACCOUNT, constants.LG_CODE, 1, 0, "시장가")

    return jsonify(buy_order)

# 매도주문 계좌번호/종목코드/수량/가격/구매타입
@app.route("/order/sell", methods=['POST'])
def send_sell_order():
    data = request.get_json()
    print(data['account'], data['item_code'], data['quantity'],data['price'], data['trading_type'])

    sell_order =kiwoom_trade.send_sell_order(constants.ACCOUNT, constants.LG_CODE, 1, 0, "시장가")

    return jsonify(sell_order)

# 매수주문 취소
@app.route("/order/cancel/buy", methods=['POST'])
def send_cancel_buy_order():
    data = request.get_json()
    print(data['account'], data['item_code'], data['quantity'],data['price'], data['trading_type'])

    cancel_buy_order = kiwoom_trade.cancel_buy_order(data['account'], data['item_code'], data['quantity'], data['price'], data['trading_type'], data['original_order_num'])

    return jsonify(cancel_buy_order)

# 매도주문 취소
@app.route("/order/cancel/sell", methods=['POST'])
def send_cancel_sell_order():
    data = request.get_json()
    print(data['account'], data['item_code'], data['quantity'],data['price'], data['trading_type'])

    cancel_sell_order = kiwoom_trade.cancel_sell_order(data['account'], data['item_code'], data['quantity'], data['price'], data['trading_type'], data['original_order_num'])

    return jsonify(cancel_sell_order)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@







# Flask 서버 실행
def run_flask_app():
    app.run(debug=True)

# Kiwoom 서버 실행
def run_kiwoom_app():
    global kiwoom
    global kiwoom_account
    global kiwoom_trade
    global kiwoom_price

    app1 = QApplication(sys.argv)  # QApplication 인스턴스 생성
    kiwoom = Kiwoom()
    kiwoom_account = Kiwoom_Send_Account(kiwoom)
    kiwoom_trade = Kiwoom_Trade(kiwoom)
    kiwoom_price = Kiwoom_Price(kiwoom)
    app1.exec_()


if __name__ == "__main__":

    # app1 = QApplication(sys.argv)  # QApplication 인스턴스 생성
    # t = Thread(target=run_flask_app)
    # t.daemon = True  # 백그라운드 스레드로 실행
    # t.start()
    # kiwoom = Kiwoom()
    # app1.exec_()

    t = Thread(target=run_kiwoom_app)
    t.daemon = True  # 백그라운드 스레드로 실행
    t.start()

    run_flask_app()


@app.route("/test")
def start_test():
    # tr 요청
    # kiwoom = get_kiwoom()
    global kiwoom

    if not kiwoom:
        return jsonify(0)
    name = kiwoom.get_master_code_name(constants.SAMSUNG_CODE)

    if not name:
        return jsonify(0)
    else:
        return jsonify(name)

