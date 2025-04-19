from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Card prefixes for common Brazilian card brands (Visa, Mastercard, Elo)
CARD_PREFIXES = {
    "Visa": ["4"],
    "Mastercard": ["51", "52", "53", "54", "55"],
    "Elo": ["4011", "4312", "4389", "4514", "4576", "5041", "5066", "5067", "509", "6277", "6362", "6363", "650", "6516", "6550"]
}

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def generate_luhn_valid_number(prefix, length=16):
    number = prefix
    while len(number) < (length - 1):
        number += str(random.randint(0,9))
    checksum = luhn_checksum(int(number) * 10)
    check_digit = (10 - checksum) % 10
    return number + str(check_digit)

def generate_cvv():
    return f"{random.randint(0, 999):03d}"

def generate_expiration_date():
    today = datetime.today()
    future_date = today + timedelta(days=random.randint(365, 5*365))  # 1 to 5 years in future
    return future_date.strftime("%m/%y")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_card():
    brand = request.form.get('brand')
    if brand not in CARD_PREFIXES:
        return jsonify({"error": "Invalid card brand"}), 400
    prefix = random.choice(CARD_PREFIXES[brand])
    card_number = generate_luhn_valid_number(prefix)
    cvv = generate_cvv()
    expiration = generate_expiration_date()
    # Fake balance for demonstration
    balance = round(random.uniform(100, 10000), 2)
    return jsonify({
        "card_number": card_number,
        "cvv": cvv,
        "expiration": expiration,
        "balance": balance,
        "brand": brand
    })

def validate_luhn(card_number):
    try:
        digits = [int(d) for d in card_number]
    except ValueError:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

@app.route('/verify', methods=['POST'])
def verify_card():
    card_number = request.form.get('card_number', '').replace(' ', '')
    if not card_number.isdigit():
        return jsonify({"valid": False, "message": "Card number must contain only digits."})
    is_valid = validate_luhn(card_number)
    message = "Card number is valid for online purchases." if is_valid else "Card number is invalid."
    return jsonify({"valid": is_valid, "message": message})

if __name__ == '__main__':
    app.run(debug=True)
