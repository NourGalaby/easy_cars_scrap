
import pandas as pd 
from time import sleep
from  scrapper  import Customer,Car
import datetime
import sys 
import os 

os.chdir('car_scrapper')


def inititalize_periodic_links_df():
    #load sent notifications or create   new one 
    try:
        links_df = pd.read_csv('periodic_links/links.csv')
        return links_df
    except IOError:
        print('couldnt load links.csv, initialized new one')
        links_df = pd.DataFrame( columns = ['customer_name','link'])
        # links_df.csv('here_here.csv')
        # print sys.path
    return links_df 







#links_df = links_df.append( {'customer_name' : "Koko wawaya", "link" : "https://www.bilbasen.dk/find-en-forhandler/bilforhandler-bilhuset-engmark-as-id8931"}, ignore_index=True )
#links_df = links_df.append( {'customer_name' : "add", "link" : "www.gogo.com"}, ignore_index=True )
def start_schuduler() :
    with open('working.txt', 'w') as f:
        f.write('here we go')
        
    links_df = inititalize_periodic_links_df()
    print(links_df.columns)
    print("Scrapping {} links".format(str(len(links_df))))
    while(True):
        #sleep(60*1)
        links_df.columns = ['customer_name','link']
        print("Daily scrap started")
        for i,row in links_df.iterrows():
            print("Scrapping {}".format(row['customer_name'])) 
            
                
            my_customer=Customer(row['link'])
            my_customer.get_cars_urls()
            my_customer.get_car_info()
            
            # file_data = BytesIO()
            my_customer.to_df()   
            my_customer.df.to_csv( 'scrapped_clients/auto_' + my_customer.customer_name + '.csv' ,encoding='utf8') 
#            app.log_df =  app.log_df.append( {'customer_name' : my_customer.customer_name , 'last_updated' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") }, ignore_index = True)
#            app.log_df.to_csv('scrapped_clients/last_update.csv' , encoding = 'utf8', index = False)
            
#            print row['link']
            sleep(1)
            
        
        #not infinit break
        break
        sleep(60*60*24)
    print("done scrapping")
    
    
if __name__ == "__main__": 
    
    start_schuduler()