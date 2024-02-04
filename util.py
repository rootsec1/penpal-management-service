def clean_phone_number(phone_number):
    phone_number = str(phone_number).replace(" ", "")
    if phone_number.startswith("+91"):
        phone_number = phone_number.replace("+91", "")
    if phone_number.startswith("+1"):
        phone_number = phone_number.replace("+1", "")
    return phone_number
