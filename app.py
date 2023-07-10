from flask import Flask
from flask import request
from twilio.rest import Client
import os
import pandas as pd
import random
import gspread
from gspread_dataframe import set_with_dataframe

sa=gspread
sa = gspread.service_account("./AppData/Roaming/gspread/service_account.json")
sh = sa.open("Home Pantry")

app=Flask(__name__)

ACCOUNT_ID=os.environ.get('TWILIO_ACCOUNT')
TWILIO_TOKEN=os.environ.get('TWILIO_TOKEN')
print(ACCOUNT_ID)
client=Client(ACCOUNT_ID,TWILIO_TOKEN)
TWILIO_NUMBER='whatsapp:+14155238886'

intro=False
item_selection=False
item=''
menu = {
    "1" : 100,
    "2" : 200,
    "3" : 300,
    "4" : 400
    }
amount=0
count={
    "1":0,
    "2":0,
    "3":0,
    "4":0
}

data = {}
df = pd.DataFrame(data, columns=['Token Number', 'Sushi', 'Pizza', 'Sushi Big', 'Pizza Big', 'Total Amount', 'Payment Screenshot'])


    

def process_msg(msg,img_url):
    global intro
    global item_selection
    global item
    global amount
    global count
    global df
    
    response=""
    if msg=='hi' or msg=='Hi' or msg=='HI':
        intro=True
        for it in count:
            count[it]=0
        amount=0
        item_selection=False
        item=''
        response="hello, welcome to home pantry! \n We have 4 options in the menu: \n 1: Sushi-Rs 100 \n 2: Pizza- Rs 200 \n 3: Sushi Big-Rs 300 \n 4: Pizza Big-Rs 400 \n Please type 1 for Sushi, 2 for Pizza, 3 for big Sushi and 4 for Big Pizza " 
    elif intro==True and item_selection==False and msg in menu :
        item_selection=True
        item=msg
        response="Please enter the quantity"
        
    elif item_selection and intro :
        amount+=int(msg)*menu[item]
        count[item]+=int(msg)
        response="Your total amount is"+str(amount)+"\nDo you wish to order something else \nType y for yes and n for no"
        item_selection=False
    elif intro and msg=='n' or msg=='N':
        response="Please send the payment screenshot"
    elif intro and msg=='y' or msg=='Y':
        item=""
        response="hello, welcome to home pantry! \nWe have 3 options in the menu: \n 1: Sushi-Rs 100 \n 2: Pizza- Rs 200 \n 3: Sushi Big-Rs 300 \n 4: Pizza Big-Rs 400 \n  Please type 1 for Sushi, 2 for Pizza, 3 for big Sushi and 4 for Big Pizza "
    elif msg=='Completed':
        intro=False
        token_number = random.randint(0, 999)
        sushi_count = count['1']
        pizza_count = count['2']
        sushi_big_count = count['3']
        pizza_big_count = count['4']
        total_amount = amount
        payment_screenshot = img_url

        new_row = pd.DataFrame({
            'Token Number': [token_number],
            'Sushi': [sushi_count],
            'Pizza': [pizza_count],
            'Sushi Big': [sushi_big_count],
            'Pizza Big': [pizza_big_count],
            'Total Amount': [total_amount],
            'Payment Screenshot': [payment_screenshot]
        })
        response="thank you for your order, your order number is "+str(token_number)

                # Append the new row to the DataFrame
        df = pd.concat([df, new_row], ignore_index=True)
        # Convert DataFrame to list of lists
        values = df.values.tolist()

    # Write the values to the sheet
        # Select the first sheet in the spreadsheet
        sheet = sh.get_worksheet(0)

    # Clear the existing sheet
        sheet.clear()
        # sheet.update('A1', values)
        set_with_dataframe(sheet, df)
        print(df)

        for it in count:
            count[it]=0
        amount=0
    else:
        response="Please type hi to get started"
    return response

def send_msg(msg,recipient):
    
    client.messages.create(
        from_=TWILIO_NUMBER,
        body=msg,
        to=recipient
    )

@app.route("/webhook",methods=["POST"])
def webhook():
    # import pdb
    # pdb.set_trace()
    f=request.form
    msg=f['Body']
    sender=f['From']
    img_url='ugh'
    if('MediaUrl0' in f and f['MediaUrl0']!=None):
        img_url=f['MediaUrl0']
        msg="Completed"
    response=process_msg(msg, img_url)
    
    send_msg(response,sender)
    return "OK",200


