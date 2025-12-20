import requests,json
BASE_URL='http://127.0.0.1:8000/'
ENDPOINT='apipy/'

def get_resource():
    while(True):
        id = input("enter id to be fetched: ")
        if id.strip() == '':
            data = {}
        else:
            data={'id':int(id)}
        resp = requests.get(BASE_URL + ENDPOINT, data=json.dumps(data))
        print(resp.status_code)
        print(resp.json(),type(resp.json()))
        ch=input("do you want to continue (yes/no): ")
        if ch.lower()=='no':
            break

def post_resource():
    while(True):
        tobeinserted_data={
            "username": input("enter username: "),
            "name": input("enter name: "),
            "astrology_message": input("enter astrology_message: "),
            "mobilenumber": int(input("enter mobilenumber: ")),
            "state": input("enter state: ")
        }
        resp=requests.post(BASE_URL+ENDPOINT,data=json.dumps(tobeinserted_data))
        print(resp.status_code)
        print(resp.json(),type(resp.json()))
        ch=input("do you want to continue (yes/no): ")
        if ch.lower()=='no':
            break
        else:
            continue

def put_resource():
    while(True):
        id = int(input("enter id to be updated: "))
        tobeupdated_data={
            "id":id,
            "username": input("enter username: "),
            "name": input("enter name: "),
            "astrology_message": input("enter astrology_message: "),
            "mobilenumber": int(input("enter mobilenumber: "))
        }
        resp=requests.put(BASE_URL+ENDPOINT,data=json.dumps(tobeupdated_data))
        print(resp.status_code)
        print(resp.json(),type(resp.json()))
        ch=input("do you want to continue (yes/no): ")
        if ch.lower()=='no':
            break
        else:
            continue

def delete_resource():
    while(True):
        id = int(input("enter id to be deleted: "))
        data={
                'id':id
            }
        resp=requests.delete(BASE_URL+ENDPOINT,data=json.dumps(data))
        print(resp.status_code)
        print(resp.json(),type(resp.json()))
        ch=input("do you want to continue (yes/no): ")
        if ch.lower()=='no':
            break
        else:
            continue

#mainprogram
while True:
    print("\n====== CRUD MENU ======")
    print("1. Get Resource")
    print("2. Post Resource")
    print("3. Update Resource")
    print("4. Delete Resource")
    print("5. Exit")
    print("=======================\n")

    choice = input("Enter your choice: ")

    if choice == '1':
        get_resource()
    elif choice == '2':
        post_resource()
    elif choice == '3':
        put_resource()
    elif choice == '4':
        delete_resource()
    elif choice == '5':
        print("Exiting...")
        break
    else:
        print("Invalid option. Try again.")