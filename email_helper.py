import csv


def email_body(course):
        if "description" not in course.keys():
            course.update({"description": "Field not inserted"})
        if "image" not in course.keys():
            course.update({"image": "Field not inserted"})
        if "quantity" not in course.keys():
            course.update({"quantity": "Field not inserted"})
        

        with open('courses.csv',"w", newline='') as csvfile:
                fieldnames = ["name", "price", "description", "quantity","image", "teacher"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({
                        "name":course["name"], 
                        "price":course["price"], 
                        "description":course["description"],
                        "quantity":course["quantity"] ,
                        "image":course["image"] , 
                        "teacher":course["teacher"]
                        })
def old_receivers(teachers_list):
    f = open("./receivers.txt", "a")
    for teacher in teachers_list:
        f.write(teacher+"\n")
    f.close()

                    
def receivers(admin):
    f = open("./receivers.txt", "a")
    f.write(admin+"\n")
    f.close()

    

def delete_receiver(teacher):
    with open("./receivers.txt", "r") as f:
            lines = f.readlines()
    with open("./receivers.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != teacher:
                    f.write(line)
