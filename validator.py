from Teachers import eml_check
from helpers import set_name, set_description, set_price, set_quantity
def pswd_check(pswd):
    if 5>=len(pswd)>=25:
        num, low, upp = 0, 0, 0
        for i in pswd:
            if i.isalpha(): num = 1
            if i.islower(): low = 1
            if i.isupper(): upp = 1
            if num and low and upp: return True
    return False
            

def valid(data):
    try:
        if "username" in data.keys() and "password" in data.keys() and "email" in data.keys() and "role" in data.keys():
            if type(data["username"]) == str and type(data["password"]) == str and type(data["email"]) == str and type(data["role"]) ==  int and 3<=len(data["username"])<=20 and pswd_check(data["password"]) and eml_check(data["email"]) and (data["role"] == 0 or data["role"] == 1):
                if "course" in data.keys():
                    for elem in data["course"]:
                        print(elem)
                        if "name" in elem.keys() and "price" in elem.keys() :
                            if set_name(elem["name"]) and set_price(elem["price"]):
                                if "description" in elem.keys():
                                    if not set_description(elem["description"]): return False 
                                
                                if "quantity" in elem.keys():
                                    if not set_quantity(elem["quantity"]): return False
                                
                                return True
                            
                            else:
                            
                                return False
                        else:
                            return False
                
                return True
            else:
                return False

        else:
            return False
    except:
        return False
'''
date = {
    "username" : "fiki",
    "password" : "32rrrAAr",
    "email" : "aaaaaa",
    "role" : 1

}
print(date)
print(valid(date))
'''