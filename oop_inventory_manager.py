import json
class Product:
    def __init__(self, product_id, name, price, stock):
        self._product_id = product_id
        self._name = name
        self._price = float(price)
        self._stock = int(stock)
    
    def update_stock(self, quantity):
        self._stock = int(quantity)

    def display_information(self):
        print(f"ID: {self._product_id} | Name: {self._name} | Price: {self._price} | Stock: {self._stock}")

    def to_dict(self):
        return {
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock
        }

class Inventory:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def search_product(self, product_id):
        for product in self.products:
            if product._product_id == product_id:
                return product
        return None

    def display_all(self):
        print('Current Inventory')
        print('-------------------------------------------------')
        for product in self.products:
            product.display_information()
        print('-------------------------------------------------')


def load_inventory():
    with open('inventory.json', 'r') as f:
        file_data = json.load(f)
        print("Inventory loaded successfully from inventory.json.")
        return file_data
    

def save_inventory(inventory_obj):
    data_to_save = []
    print('Saving inventory....')

    # Convert each product object to a dictionary using its own method
    for product in inventory_obj.products:
        product_dict = product.to_dict()
        data_to_save.append(product_dict)

    # Write to JSON file
    with open('inventory.json', 'w') as f:
        json.dump(data_to_save, f, indent=4)

    print('Inventory saved successfully to inventory.json.')

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
    print('-------------------------------\n')
    userinput=input('Enter Option:')
    return userinput

loading_inventory= load_inventory()
inventory = Inventory()
for item in loading_inventory:
     product= Product(item['product_id'],item['name'],item['price'],item['stock'])
     inventory.add_product(product)


while True:
    userinput=menu_Page()
    if userinput == "1":
        inventory.display_all()

    elif userinput =="2":
        id=input('Product ID:')
        product_Name=input('Product Name:')
        Price=input('Price:')
        Stock=input('Stock:')
        product= Product(id,product_Name,Price,Stock)
        inventory.add_product(product)
        print("Product Added Successfully")
        inventory.display_all()

    elif userinput =="3":
        id=input('Product ID:')
        result = inventory.search_product(id)
        if result == None:
            print('Product not found')
        else:
            print('Product Found:\n')
            print(f"Product ID: {result._product_id}")
            print(f"Current Stock: {result._stock}\n")
            new_stock_quantity=input('New Stock Quantity:')
            result.update_stock(new_stock_quantity)
            print('\nStock updated Sucessfully! \n')
            inventory.display_all()

    elif userinput =="4":
        id=input('Enter Product ID:')
        result = inventory.search_product(id)
        if result == None:
            print('Product not found')
        else:
            print('Product Found:\n')
            #calling the display_information as after searching in the inventory it returns the object product which is the object we created using the class Product
            # its function and everything is also brough into the results variable. Therefore, we can use the function display_information
            result.display_information() 
    elif userinput =="5":
        save_inventory(inventory)
    elif userinput =="6":
        print('Saving inventory before exit....\nInventory Saved successfully.\n\nThank you for using Inventory Management System.\nPrograme Terminated.')
        save_inventory(inventory)
        break
    
    else:
        print('An error occured. Please try again')
    
        




