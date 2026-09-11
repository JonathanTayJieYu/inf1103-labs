inventory = 0
failed_entries = 0
total_unit_processed = 0

while True:
    Stock_value = input('enter a stock quantity: ')
    
    if Stock_value.isdigit():
        inventory+=1
        total_unit_processed += 1
        if total_unit_processed >= 500:
                    print("Alert Total unit process more than 500")
                    print('Total Unit Processed', total_unit_processed)
                    break
    elif Stock_value=="quit":
        print('Total Unit Processed', total_unit_processed,"\n", 
              "Number of Failed/Rejected Entries :", failed_entries)
        break
    else:
        print('Eror, either you have entered a negative number or a wrong input ')
        failed_entries +=1
