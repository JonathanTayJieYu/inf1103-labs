inventory = 0
failed_entries = 0
total_unit_processed = 0
delivery_processed = 0
delivery_amount= 0
counter = 1
transaction_history =[]

def load_inventory():
    with open('inventory.txt', 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()
        # Check the prefix to know what kind of data it is
            if line.startswith("INV:"):
             # Strip the 'INV:' tag before storing
             inventory_value = line[4:]
             print("Inventory Count:",inventory_value)
            
            elif line.startswith("TRX:"):
             # Strip the 'TRX:' tag before storing
             transaction_value = line[4:]
             print("Transaction History:",transaction_value)

def save_inventory(inventory,transaction_history):
    with open('inventory.txt', 'a') as file:
    # Save inventory items with an 'INV:' prefix
        file.write("INV:"+str(inventory)+"\n")
    # Save transaction history with a 'TRX:' prefix
        file.write("TRX:"+str(transaction_history))

def get_valid_input():
    user_input= input('enter a stock quantity: ')
    if user_input == 'quit':
        return None
    else:
         return user_input
         
def calculate_tax(amount):
     total= amount*0.1
     return total   

def process_delivery(current_total, new_value):
     total= current_total + new_value
     return total

def generate_report(total_units, failed_attempts):
     print('Total Unit Processed', total_units,"\n", 
                       "Number of Failed/Rejected Entries :", failed_attempts)

while True:
    Stock_value = get_valid_input()
    if Stock_value == None:
            load_inventory()
            save_inventory(inventory,transaction_history)
            generate_report(total_unit_processed,failed_entries)
            break
    elif Stock_value.isdigit():
        inventory+=1
        total_amount=process_delivery(delivery_processed,counter)
        delivery_processed=total_amount
        delivery_amount=calculate_tax(delivery_processed)
        transaction_history.append(Stock_value)
        total_unit_processed += 1
        if total_unit_processed >= 500:
                    print("Alert Total unit process more than 500")
                    print('Total Unit Processed', total_unit_processed)
                    break
    else:
            print('Eror, either you have entered a negative number or a wrong input')
            failed_entries +=1
            
       
    
    
