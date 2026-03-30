from collections import defaultdict

def курс_в_лева(exchange_rates):
    
    exchange_rates_bg = {}
    for key, value in exchange_rates.items():
        if len(key) != 3:
            continue
        exchange_rates_bg[key] = round(1 / value, 4)

    return exchange_rates_bg
    
def валута_към_левчета(*args, **kwargs):

    sums = defaultdict(float)
    for currency, amount in args:
        sums[currency] += amount

    result = []
    for currency, amount in sums.items():
        if currency == "BGN":
            leva = amount
        else:
            rate = kwargs[currency]
            leva = amount / rate
        result.append((currency, round(leva, 4)))

    return result

def е_валиден_лев(num):
    return abs(num - round(num, 2)) < 1e-9

def е_патриотична(amounts, exchange_rates):
    sums = defaultdict(float)
    for currency, amount in amounts:
        sums[currency] += amount

    result = 0
    for currency, amount in sums.items():
        result += amount / exchange_rates[currency]

    return "ПАТРИОТИЧНА!" if е_валиден_лев(result) else "НЕПАТРИОТИЧНА!"

# exchange_rates = {"EUR": 1.9558, "USD": 1.6718, "DKK": 0.2616}
# print(курс_в_лева(exchange_rates))
# print(валута_към_левчета(
#     ("EUR", 1.5),
#     ("USD", 10),
#     ("DKK", 10),
#     ("EUR", 2.5),
#     EUR=0.5,
#     USD=0.8,
#     DKK=7,
# ))
# exchange_rates = {"EUR": 0.5, "USD": 0.6, "DKK": 3.8}
# amount = [("EUR", 1), ("USD", 3), ("DKK", 7.6), ("EUR", 3)]
# print(е_патриотична(amount, exchange_rates)) # ПАТРИОТИЧНА! - 4 / 0.5 + 3 / 0.6 + 7.6 / 3.8 = 15

# amount = [("EUR", 1), ("USD", 2), ("DKK", 7.6), ("EUR", 3)]
# print(е_патриотична(amount, exchange_rates)) # НЕПАТРИОТИЧНА! - 4 / 0.5 + 2 / 0.6 + 7.6 / 3.8 = 13.33, опитват се да ни измамят


