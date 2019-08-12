
# function for checking name input in Courses collection
def set_name(name):
    if len(name) < 3 or len(name) > 15:
        return False
    else:
        return name

# function for checking description input in Courses collection
def set_description(description):
    if len(description) < 10 or len(description) > 150:
        return False
    else:
        return description

# function for checking price input in Courses collection
def set_price(price):
    float_price  = float(price)
    if float_price < 1 or float_price > 10000:
        return False
    else:
        return price

# function for checking quantity input in Courses collection
def set_quantity(quantity):
    int_quantity  = int(quantity)
    if int_quantity > 50:
        return False
    else:
        return quantity