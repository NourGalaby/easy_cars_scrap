from flask import Flask

from flask import request, send_file, send_from_directory,  flash, redirect, render_template, session, abort, url_for
import pandas as pd 
from io import BytesIO
import time
import os 
import sys
# sys.path.insert(0,'.')
from  scrapper  import Customer,Car
import datetime 
# from periodic_run import start_schuduler
# from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
# application  = app
app.config["DEBUG"] = False



# executor = ThreadPoolExecutor(1)
# executor.submit(start_schuduler)


@app.route('/main_page', methods=['GET'])
def main_page():
    return app.send_static_file('index.html')


def inititalize_log_df():
    #load sent notifications or create new one 
    try:
        log_df = pd.DataFrame.from_csv('scrapped_clients/last_update.csv')
    except:
        print('couldnt load last_updated.csv, initialized new one')
        log_df = pd.DataFrame( columns = ['customer_name','last_updated'])
    return log_df 
    
app.log_df = inititalize_log_df()


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('./login.html')
    else:
        return redirect(url_for("./main_page") )

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'cheesecake' and request.form['username'] == 'admin':
      session['logged_in'] = True
    else:
      flash('wrong password!')
    return home()



@app.route('/requestcsv', methods=['GET'])
def request_csv():
    """
    takes link of a client page and returns csv of all scrapped data
    """
    try:
        client_url = request.args.get('link_input', type = str)
        my_customer=Customer(client_url)
        assert client_url is not None
    except Exception as e : 
        Error = "Error getting client link, try again" 

        print Error + str(e) 
        return Error, 400
    
    print('Scrapping link: {}'.format(client_url))
    my_customer=Customer(client_url)
    my_customer.get_cars_urls()
    my_customer.get_car_info()
    
    # file_data = BytesIO()
    my_customer.to_df()  
#    my_customer.df.to_csv('api_' + my_customer.customer_name + ".csv",encoding='utf8')
    # my_customer.df.to_csv(file_data ,encoding='utf8')
    
    my_customer.df.to_csv( 'scrapped_clients/' + my_customer.customer_name + '.csv' ,encoding='utf8')
    # file_data.seek(0)
    # response= send_file(file_data,
    #                  mimetype='text/csv',
    #                  attachment_filename=my_customer.customer_name + ".csv",
    #                  as_attachment=True)
    # response.headers["x-filename"] = my_customer.customer_name + '.csv'
    # response.headers["Access-Control-Expose-Headers"] = 'x-filename'
    
    app.log_df =  app.log_df.append( {'customer_name' : my_customer.customer_name , 'last_updated' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") }, ignore_index = True)
    app.log_df.to_csv('scrapped_clients/last_update.csv' , encoding = 'utf8', index = False)
    
    return "Success"



@app.route('/scrapped_clients/<csv_name>')
def get_saved_csv(csv_name):
        return send_from_directory('scrapped_clients',
                               csv_name, as_attachment=True)



@app.route('/requestcsv_test', methods=['GET'])
def request_csv_test():
    try:
        client_url = request.args.get('link_input', type = str)
        my_customer=Customer(client_url)
        assert client_url is not None
    except Exception as      e : 
        Error = "Error getting client link, try again" 

        print Error + str(e) 
        return Error, 400
#    my_customer=Customer(client_url)
    df = pd.read_csv('allan-hansen-automobiler.csv')
    file_data = BytesIO()
    df.to_csv(file_data ,encoding='utf8')
    response= send_file(file_data,
                     mimetype='text/csv',
                     attachment_filename=my_customer.customer_name + '.csv',
                     as_attachment=True)
    response.headers["x-filename"] = my_customer.customer_name + '.csv'
    response.headers["Access-Control-Expose-Headers"] = 'x-filename'
    time.sleep(3)
    return response
    
@app.route('/test_input', methods=['POST'])
def test_input():
    try:
        client_url = request.form['link_input']
        assert client_url is not None
    except : 
        Error = "Error getting client link, try again" 

        print Error
        return Error, 400
    print client_url
    return ""
    

app.secret_key = os.urandom(12)
# app.run(debug=True)