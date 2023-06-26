from fuzzywuzzy import fuzz
from unidecode import unidecode
from env import OVERRIDES, EXCLUDES
from datetime import datetime
from decimal import Decimal

CATEGORIES = {
    "ifood": ["ifood", "ifd"],
    "liv up": ["livup", "liv up"],
    "charity": ["apoia", "apoia.se", "apoiase"],
    "fuel": ["auto posto", "posto"],
    "lunch": ["flying sushi"],
    "supermarket": ["mambo", "supermercado"],
    "uber": ["uber"],
    "eccomerce": [
        "shoptime",
        "kabum",
        "mercadolivre",
        "mercadopago",
        "amazon",
        "aliexpress",
        "shopee",
    ],
    "restaurant": [
        "bistro",
        "churrascaria",
        "starbucks",
        "burger king",
        "restaurante",
        "lanche",
        "brilho do sol",
        "embaixada mineira",
        "hirota",
        "tea connection",
    ],
    "hotel": ["airbnb"],
    "drugstore": ["drograria", "drogasil"],
    "phone": ["claro flex"],
    "toll": ["estapar"],
    "services": ["spotify", "tinder"],
}


def normalize_text(txt):
    return unidecode(txt).lower()


def parse_brazilian_date(dt):
    return datetime.strptime(dt, "%d/%m/%Y")


def parse_amount(amount):
    minus_modifier = -1 if "-" in amount else 1

    reais, centavos = amount.split(",")
    reais = "".join([x for x in reais if x.isdigit()])
    centavos = "".join([x for x in centavos if x.isdigit()])

    return minus_modifier * (Decimal(reais) + Decimal(centavos) / Decimal(100))


def parse_installments(txt):
    if "-" in txt:
        return 0, 0
    splitted_installments = txt.split(" de ")
    return int(splitted_installments[0]), int(splitted_installments[1])


def parse_owner(txt):
    if "brenno" in txt.lower():
        return "brenno"
    else:
        return "uknown"


def predict_payment_date(dt_list):
    sorted_list = sorted(dt_list, reverse=True)
    expected_payment_date = sorted_list[0].replace(
        day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    expected_payment_date_score = len(
        [x for x in dt_list if x == expected_payment_date]
    )

    return expected_payment_date, expected_payment_date_score


def classify_text(txt):
    txt = normalize_text(txt)
    if OVERRIDES.get(txt):
        return txt, 100, OVERRIDES.get(txt)

    best_score = 0
    best_category = "other"
    for category, classifier in CATEGORIES.items():
        score = fuzz.partial_ratio(classifier, txt)
        if score > best_score and score >= 40:
            best_score = score
            best_category = category

    return txt, best_score, best_category


def classify_file_data(data):
    expected_payment_date, expected_payment_date_score = predict_payment_date(
        [parse_brazilian_date(x[0]) for x in data]
    )

    final = []
    for row in data:
        dt, txt, owner, amount, installment = row
        parsed_txt, score, category = classify_text(txt)
        if parsed_txt in EXCLUDES:
            continue

        dt = parse_brazilian_date(dt)
        current_installment, total_installments = parse_installments(installment)
        parsed_owner = parse_owner(owner)
        parsed_amount = parse_amount(amount)

        final.append(
            {
                "purchase_date": dt,
                "description": parsed_txt,
                "owner": parsed_owner,
                "amount": parsed_amount,
                "current_installment": current_installment,
                "total_installments": total_installments,
                "score": score,
                "category": category,
                "expected_payment_date": expected_payment_date,
                "expected_payment_date_score": expected_payment_date_score,
            }
        )

    return final, expected_payment_date


if __name__ == "__main__":
    from webdav import get_one_file

    file_path, file_data, file_headers = get_one_file()

    # print(file_headers)

    file_data = classify_file_data(file_data)

    for row in file_data:
        print(row)
