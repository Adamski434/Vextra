import dearpygui.dearpygui as dpg
import mysql.connector

global inputDict 
inputDict ={}
global mycursor
global mydb
global TheactiveUser # Holds The User Id of the current sessions User
TheactiveUser = -50
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "DV1663_prod",
    database = "DV1663_project"
)
mycursor = mydb.cursor()

dpg.create_context()
dpg.create_viewport(title='Växtra', width=600, height=300)
dpg.setup_dearpygui()

#-------------------------------------------------------------------------------------------------

def show_window(window_tag):
    
    dpg.configure_item(window_tag, show=True)
    dpg.focus_item(window_tag)
    
def show_window_and_close( sender, app_data, window_tag): #sender är widget_id från knappen som trycks
    
    window_to_close = dpg.get_item_parent(sender) #parent is the window

    dpg.configure_item(window_to_close,show=False)
    dpg.configure_item(window_tag,show=True)
    dpg.focus_item(window_tag)
    
#------------------------------------------------------------------------------------------------------------------
def update_transactionsTable():
    global inputDict
    statement = "SELECT u.user_id, u.user_name, p.plant_name, t.seller_id,t.plant_id, t.buyer_id FROM User u, Transactions t, plant p WHERE p.plant_id = t.plant_id AND (u.User_ID = t.Buyer_ID OR u.User_ID = t.seller_ID)"
    mycursor.execute(statement)
    result = mycursor.fetchall()
    if dpg.does_item_exist("trans_table"):
        dpg.delete_item("trans_table",children_only= True)
        dpg.add_table_column(label="user_ID",parent="trans_table")
        dpg.add_table_column(label ="Username",parent= "trans_table")
        dpg.add_table_column(label="plant name",parent="trans_table")
        dpg.add_table_column(label = "seller_ID",parent="trans_table")
        dpg.add_table_column(label="plant_ID",parent="trans_table")
        dpg.add_table_column(label="buyer_ID",parent="trans_table")
        for x in range(len(result)): 
            with dpg.table_row(parent="trans_table"):
                for data in range(6):
                    dpg.add_text(result[x][data]) 

    show_window("transactions_win")
    inputDict["transactions"] = result

def update_upforsaletable():
    print("updating")
    global inputDict
    statement = "SELECT Plant_Name,Plant_Family,plant.Plant_ID, upforsale.Seller_ID FROM PLANT INNER JOIN UpForSale ON UpForSale.Plant_ID = Plant.Plant_ID "
    mycursor.execute(statement)
    result = mycursor.fetchall()
    if dpg.does_item_exist("UFS_table"):
        dpg.delete_item("UFS_table",children_only=True)
        dpg.add_table_column(label="Plant Name",parent="UFS_table")
        dpg.add_table_column(label="Plant Family",parent="UFS_table")
        dpg.add_table_column(label="Plant ID",parent="UFS_table")
        dpg.add_table_column(label="Seller_ID",parent="UFS_table")
        for x in range(len(result)):
            with dpg.table_row(parent="UFS_table"):
                for data in range(4):
                    dpg.add_text(result[x][data])
    


    show_window("UpForSale_win")
    inputDict["upforsale"] = result
#-----------------------------------------------------------------------------------------------------------

def buy():
    plant_ID = inputDict["Plant_ID_Buy"]
    global TheactiveUser
    print(" in buy:",plant_ID)
    statement =f"CALL Buy({plant_ID},{TheactiveUser})"
    mycursor.execute(statement)
    mydb.commit()
    update_upforsaletable()

def sell():
    global inputDict
    pN = inputDict["Plant_Name"]
    pF = inputDict["Plant_Family"]

    print(pN,pF)
    print(TheactiveUser)
    statement = " INSERT INTO Plant(Plant_Name,Plant_Family) VALUES(%s,%s)"
    mycursor.execute(statement,(pN,pF))
    mydb.commit()
    plant_ID = mycursor.lastrowid
    statement2 = "INSERT INTO UpForSale(Plant_ID,Seller_ID) VALUES(%s,%s)"
    mycursor.execute(statement2,(plant_ID,TheactiveUser))
    mydb.commit()
    dpg.set_value(item="sale_head",value="Succesful sale!")
    show_sell()

def show_sell():
    statement = f"SELECT COUNT(Seller_ID) FROM Transactions WHERE Seller_ID = {TheactiveUser}"
    mycursor.execute(statement)
    count = mycursor.fetchone()
    count = count[0]
    print(count)
    dpg.set_value("sales",f"You have made {count} sales")
    show_window("sell_win")

def on_input(sender, app_data, user_data):
    inputDict[user_data] = app_data

# -------------------------------------------------------------------------------------------------------------------------------------------------
#variation of show window and close, skriv in Id för att logga in
def perform_login(sender, app_data):
    window_to_close = dpg.get_item_parent(sender)
    user_ID = inputDict.get("username_login")
    print(user_ID)
    global TheactiveUser
    try:
        statement = f"SELECT * FROM User WHERE User_ID = {user_ID}"
        mycursor.execute(statement)
        result = mycursor.fetchall()
        username = result[0][1]
    
        if not result:
            dpg.configure(sender, label = "Cannot find user, sign in")      
        else: 
            dpg.configure_item(window_to_close, show= False)
            TheactiveUser = user_ID
            dpg.set_value("ID_text", f"Welcome {username}\nYour User ID is {TheactiveUser}")
        dpg.configure_item("home_win",show= True)
        dpg.focus_item("home_win")
    except:
        dpg.configure_item(sender,label = "Something went wrong")  
                        
   


def perform_SignIn(sender,app_data):
    window_to_close = dpg.get_item_parent(sender)
    dpg.configure_item(window_to_close, show= False)
    global TheactiveUser
   
    username = inputDict.get("username_login")
    statement = "INSERT INTO user(User_Name) VALUES(%s)"
                 
    mycursor.execute(statement,(username,))
    mydb.commit()

    #select shit
    insert_ID = mycursor.lastrowid
    getter_statement = f"SELECT * FROM User WHERE User_ID = {insert_ID}"
    mycursor.execute(getter_statement)
    result = mycursor.fetchall()

    TheactiveUser = result[0][0]
    
    dpg.set_value("ID_text", f" Welcome {username}\n Your User ID is {TheactiveUser}")
    dpg.configure_item("home_win",show= True)
    dpg.focus_item("home_win")

#------------------------------------------------------------------------------------------------------------------


with dpg.window(label = "Transactions",tag = "transactions_win",width= 400,height = 300,show= False):
    dpg.add_text("Transactions")
    update_transactionsTable()
    transactions = inputDict["transactions"]

    with dpg.table(tag="trans_table",header_row=True,borders_innerH=True, borders_outerH=True,borders_innerV=True, borders_outerV=True, row_background=True, resizable=True,policy=dpg.mvTable_SizingFixedFit):
        dpg.add_table_column(label="user_ID")
        dpg.add_table_column(label ="Username")
        dpg.add_table_column(label="plant name")
        dpg.add_table_column(label = "seller_ID")
        dpg.add_table_column(label="plant_ID")
        dpg.add_table_column(label="buyer_ID")
        for x in range(len(transactions)): 
            with dpg.table_row():
                for data in range(6):
                    dpg.add_text(transactions[x][data])


    dpg.add_button(label = "Close",callback = lambda: dpg.configure_item("transactions_win",show= False))


#-------------------------------------------------------------------------------------------------------

with dpg.window(label = "UpForSale",tag = "UpForSale_win",width= 400,height = 300,show=False):
    dpg.add_text("UpforSale Table, ska kunna köpa grejer")

    update_upforsaletable()
    UpForSale  = inputDict["upforsale"]
    
    with dpg.table(tag= "UFS_table",header_row=True,borders_innerH=True, borders_outerH=True,borders_innerV=True, borders_outerV=True, row_background=True, resizable=True,policy=dpg.mvTable_SizingStretchProp):
        dpg.add_table_column(label="Plant Name")
        dpg.add_table_column(label="Plant ID")
        dpg.add_table_column(label="Plant Family")
        dpg.add_table_column(label="Seller_ID")

        for x in range(len(UpForSale)):
            with dpg.table_row(parent="UFS_table"):
                for data in range(4):
                    dpg.add_text(UpForSale[x][data])

    dpg.add_input_text(label="Plant_ID", callback=on_input, user_data= "Plant_ID_Buy")                
    dpg.add_button(label = "buy", callback=buy)
    dpg.add_button(label = "Close",callback = lambda: dpg.configure_item("UpForSale_win",show= False))

#----------------------------------------------------------------------------------------------------------------

with dpg.window(label="Sell",tag="sell_win",width=400,height=300,show=False):
    dpg.add_text(tag="sale_head",default_value="Sell a plant")
    dpg.add_text(tag="sales",default_value=" njnjn")
    dpg.add_input_text(label="Plant Name",callback=on_input,user_data="Plant_Name")
    dpg.add_input_text(label="Plant Family",callback=on_input,user_data="Plant_Family")
    dpg.add_button(label="$$ Sell $$", callback=sell)
    dpg.add_button(label="Close",callback = lambda: dpg.configure_item("sell_win",show=False))

#--------------------------------------------------------------------------------------------------------
with dpg.window(label = "Home",tag ="home_win",width = 400, height = 300,show= False):
    dpg.add_text(tag="ID_text", default_value=f"Your User ID is {TheactiveUser}")
    dpg.add_button(label = "See transactions", callback=update_transactionsTable)
    dpg.add_button(label = "Shop ", callback= update_upforsaletable)
    dpg.add_button(label = "Sell", callback=show_sell)

#--------------------------------------------------------------------------------------------------------
#log/sign in page
with dpg.window(label= " Log in ", tag = "LogIn_win", width=400,height=300, show= True):
    dpg.add_input_text(label = "Log in with ID", callback=on_input, user_data= "username_login")
    dpg.add_button(label= "login", callback= perform_login)
    dpg.add_separator()
    dpg.add_input_text(label= "Sign in", callback=on_input, user_data="username_login")
    dpg.add_button(label= "Sign In", callback= perform_SignIn)
#start_window

    

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()