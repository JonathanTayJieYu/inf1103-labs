import json
inventory ={
    "P001": {
        "id":"P001",
        "name": "Laptop",
        "price": 1200.00,
        "stock": 45
    },
    "P002": {
        "id":"P002",
        "name": "Mouse",
        "price": 25.50,
        "stock": 20
    },  
    "P003": {
        "id":"P003",
        "name": "Keyboard",
        "price": 45.00,
        "stock": 20
    } 

}

def load_inventory():
    with open('inventory.json', 'r') as f:
        inventory = json.load(f)
        print("Inventory loaded successfully from inventory.json.")
        return inventory
    
inventory= load_inventory()

def display_all():
    print('Current Inventory')
    print('-------------------------------------------------')
    for id in inventory:
        all_value=inventory[id]
        print('ID:', all_value['id'],'| Name:',all_value['name'],'| Price:',all_value['price'],'| Stock Quantity:', all_value['stock'])
    print('-------------------------------------------------')


def add_product():
    id=input('Product ID:')
    product_Name=input('Product Name:')
    Price=input('Price:')
    Stock=input('Stock:')
    inventory[id]={
        "id": id,
        "name":product_Name,
        "price":Price,
        "stock":Stock,
    }
    print("Product Added Successfully")
    display_all()
    return

def update_stock():
    id=input('Product ID:')
    if id not in inventory:
        print('Product not found')
    else:
        print('Product Found:\n')
        for id_label in inventory:
            if id_label==id:
                current_value=inventory[id_label]
                print("Product ID:", current_value['name'])
                print('Current Stock:',current_value['stock'])
        print('\n')
        new_stock_quantity=input('New Stock Quantity:')
        inventory[id]['stock']= new_stock_quantity
        print('\nStock updated Sucessfully! \n')
        display_all()
    return


def search_product():
    print("Search Product")
    user_input= input("Enter Product ID:")
    if user_input in inventory:
        current_value = inventory[user_input]
        print('\nProduct Found')
        print('------------------------')
        print("ID:", current_value['id'])
        print("Name:", current_value['name'])
        print("Price:", current_value['price'])
        print("Stock:", current_value['stock'])
        print('------------------------')
    else:
        print(f"\nProduct ID '{user_input}' not found in inventory.")

    return

def save_inventory():
    print('Saving inventory....')
    with open('inventory.json', 'w') as f:
        json.dump(inventory,f)
    print('Inventory saved successfully to inventory.json.')
    return

def menu_Page():
    print('-----------------------------------------')
    print('INVETORY MANAGEMENT SYSTEM')
    print('-----------------------------------------')
    print('-----------Menu------------------')
    print('1.Display All Products')
    print('2.Add Product')
    print('3.Update Stock')
    print('4.Search Product')
    print('5.Save Inventory')
    print('6.Quit')
    print('------------------------------\n')
    userinput=input('Enter Option:')
    return userinput

while True:
    userinput=menu_Page()
    if userinput == "1":
        display_all()
    elif userinput =="2":
        add_product()
    elif userinput =="3":
        update_stock()
    elif userinput =="4":
        search_product()
    elif userinput =="5":
        save_inventory()
    elif userinput =="6":
        print('Saving inventory before exit....\nInventory Saved successfully.\n\nThank you for using Inventory Management System.\nPrograme Terminated.')
        save_inventory()
        break
    
    else:
        print('An error occured. Please try again')
    
        




