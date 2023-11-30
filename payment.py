from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay

# Токен кошелька
yoomoney_token = ""
wallet_number = "4100110394090835"


def get_token(client_ID, redirect_url):
    Authorize(
        client_id=client_ID,
        redirect_uri=redirect_url,
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop",
               ]
    )


# это для меня по большей части функция, так как с чужими данными не играемся
def check_payment_token(payment_token):
    client = Client(payment_token)
    user = client.account_info()
    print("Account number:", user.account)
    print("Account balance:", user.balance)
    print("Account currency code in ISO 4217 format:", user.currency)
    print("Account status:", user.account_status)
    print("Account type:", user.account_type)
    print("Extended balance information:")
    for pair in vars(user.balance_details):
        print("\t-->", pair, ":", vars(user.balance_details).get(pair))
    print("Information about linked bank cards:")
    cards = user.cards_linked
    if len(cards) != 0:
        for card in cards:
            print(card.pan_fragment, " - ", card.type)
    else:
        print("No card is linked to the account")


def quick_pay(target, price, order_id):
    quickpay = Quickpay(
        receiver=wallet_number,
        quickpay_form="shop",
        targets=target,
        paymentType="SB",
        sum=price,
        label=order_id
    )
    print(quickpay.base_url)
    print(quickpay.redirected_url)
    return quickpay.redirected_url


def check_payment(payment_label):
    client = Client(yoomoney_token)
    history = client.operation_history(label=payment_label)
    print(len(history.operations))
    if len(history.operations) > 0:
        return True
    else:
        return False
