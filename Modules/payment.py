import asyncio

from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay

# Токен кошелька
yoomoney_token = "4100118467972256.C27F91C9CE80D37B999ACBB65564FB8221BEF41D3462A7270535A0741952D3D2AC4CF6E813323E5277AEB29D8D72AADBE1393F6CD82C5197592BD518ACEB6C746CF45836FB2EECD5551C331DFE095F7C5FA4780BCEA37CFC3CE4E32068CACBBF2D8150C0FB978FCEBC10C1523C81D0C0D55E37A82AB5975A28498A2DCAA2DD4B"
wallet_number = "4100118467972256"


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


async def quick_pay(target, price, order_id):
    quickpay = await asyncio.to_thread(
    Quickpay,
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


async def check_payment(payment_label):
    # return True

    client = Client(yoomoney_token)
    history = await asyncio.to_thread(client.operation_history,
                                      label=payment_label)
    print(len(history.operations))
    if len(history.operations) > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    # get_token("13A1B279E7E93DE71356A31E1A70EF8A667A41F1F8562FC019CB9BB61FF46E19", redirect_url="http://site.ru")
    # check_payment_token(yoomoney_token)
    ...
