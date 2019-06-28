from bs4 import BeautifulSoup
import urllib2  as urllib
import os
import datetime
import pandas as pd
import settings
import requests 
import re 

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class Car:
    def __init__(self,url):
        self.name=""
        self.title_description=""
        self.price=""
        self.milage=""
        self.model = ''
        self.equipment=[]
        self.description=[]
        self.facts=[]
        self.images_urls=[]
        self.url=url
        self.date=datetime.datetime.now()
    def print_attrs(self):
        for a in self.__dict__.iteritems(): 
            print a

    def __str__(self):
        s=[]
        for a in self.__dict__.iteritems(): 
            s.append(a)
            return str(len(s))
        
        

    def get_page(self,url):
        car_id=str(url.split('/')[-1] ) # get car id from URL ex 3490332
        path="cars/" + car_id +".html"
#        if  os.path.exists(path):
        if False : #disabled caching 
            with open(path , 'r+' ) as f:
                r = f.read()
#            print "here"
            return r
        else :
            r = requests.get(url , headers= headers)
            if r.status_code != 200:
               raise Exception('Error accessing site')
            
            f = file( "cars/" + car_id + ".html", "w")
            f.write(r.content)
            f.close()
#            print "there"
            return r.content
        
        
    def  extract_info(self):
        page = self.get_page(self.url)
        
        soup = BeautifulSoup(page, 'html.parser')
    
        name_tag=soup.find('h1',{'id':'bbVipTitle'})
#        print name_tag
#        print ""
#        print len(page)
        self.name= name_tag.find('span').text
        
        imgs_s = soup.find_all('meta' , {'property' : 'og:image'})
        for images_s in imgs_s:

                image_url = images_s['content']
                if settings.download_high_resolution_pics:
                    image_url = image_url.split('?')[0] #get the url without cropping.. #comment for lower resolution
                    image_filename = image_url.split('/')[-1]
                else:
                    #image url stays the same
                    image_filename = image_url.split('?')[0].split('/')[-1]
                #image_urls.append(image_url) #optional

                if "bilbasen-200x200.png" in image_url: #skip logo image
                    continue 
                
                self.images_urls.append( image_url)
                #if image exists skip
                if os.path.exists(image_filename):
                    print("image already saved, skipping...")
                    continue
            
        self.images_urls = ", ".join(self.images_urls)
           
           
        #Save images             
#                f = open (' cars/' + self.car_id + '/' + image_filename, 'wb')
#                f.write(requests.get(image_url).content)
#                f.close()


     ##### END IF FIND IMAGES #########3

        start= len(self.name) + 1 
        all_desc=name_tag.text
        self.title_description=all_desc[start::]
        
        x=soup.find('p' , {'id':'bbVipPricePrice' })
        self.price=x.find('span',{'class' : 'value' } ).text
        
        
        x=soup.find('section' , {'id':'bbVipMileage' })
        self.milage=x.find('span',{'class' : 'value' } ).text.strip()
        
        #Equipment
        x=soup.find('section' , {'id':'bbVipEquipment' })
        equipment_list=list( x.find_all('li') )
        for e in equipment_list:
            self.equipment.append(e.text)
            
        self.equipemnt = ', '.join(self.equipment)
        #Description
        x=soup.find('section' , {'id':'bbVipDescription' })
        mylist=x.text.strip().split(',')
        
        for s in mylist:
            if 'Lever' in s:
                self.Levering = float(s[  s.find('Levering') : s.find('Farve') ].split(':')[1])
                self.Farve = s[  s.find('Farve') : ].split(':')[1].strip()
            else  :
                self.description.append(s.strip()) 
            
        self.description = ', '.join(self.description)

        
        #factsx
        
        x=soup.find('ul' , {'id':'bbVipDescriptionFacts' })
        facts=list(x.find_all('li')) 
        for f in facts:
            try:
                k,v = f.text.split(':')
                self.facts.update( {k : v} )
            except:
                continue
        table=soup.find('div', {'class': 'accordion-b'} )
        specs=table.find_all('tr')
        
        self.specs={}
        for s in specs[1::] :
            try:
                value=s.find('td',{'class' : 'selectedcar'}).text
                key=s.find('td').text
                self.specs[key] =  value  
            except:
                continue
            
            
        
        table=soup.find('table',{'class': 'margin-n' } )
        pp=table.find_all('tr')
        value=pp[1].find('td', {'class' : "alignright" } ).text.strip()
        self.owner_fees=value
        
        self.model = soup.find('div' , {'class' : 'car-model-year'} ).find('span' , {'class' : 'value'} ).text
        
        return 
    
    
class Customer:
    
    def __init__(self,url):
        self.url=url
        self.cars=[]    
        self.customer_name = re.findall('handler-(.+)-id',url)[0]
        
    def get_cars_urls(self):
        print self.url
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


        r =requests.get(self.url, headers=headers )
        if r.status_code != 200:
            raise Exception('Error accessing website')
            
        r = r.text
        soup = BeautifulSoup(r, 'html.parser')
        cars_url_soup=soup.find_all('a',{'class': 'listing-heading darkLink' })
        
        cars_url=[]
        for c in cars_url_soup:
             cars_url.append("https://www.bilbasen.dk"+c['href'] )
    
        self.cars_url=cars_url
        return
    
    
    def get_car_info(self):
        for url in self.cars_url:
            new_car=Car(url)
            new_car.extract_info()
            self.cars.append(new_car)
            
            
            
    def to_df(self):
        mylist=[]
        for c in self.cars:
            mylist.append(dict(c.__dict__) )
            
        self.df = pd.DataFrame(mylist)
        
        #expand nested:
        nested_keys = ['facts','specs']
        for kk in nested_keys:
            xx = pd.DataFrame(list(self.df[kk]))
            self.df = self.df.merge( xx, right_index=True , left_index=True)
            self.df.drop(kk, axis = 1, inplace = True)
            
        
        self.df['Farve'] = self.df.description.str.extract('Farve: (.+)')
        self.df['Synet'] = self.df.description.str.extract('Synet:(.+)')
        
        cols = ['milage', 'owner_fees', 'price', u'Max. p\xe5h\xe6ng', 'Nypris']
        for col in cols :
            self.df[col] = self.df[col].str.replace('.','')
            
            
        
    def export_csv(self):
        self.df.to_csv("bilhuset-engmark-as-id8931.csv", encoding='utf8')
        
        
#        : df['milage'].str.replace('.','')

#URL="https://www.bilbasen.dk/brugt/bil/toyota/avensis/20-d-4d-tx-stcar-5d/3490832"
#r = urllib.urlopen(URL).read()
#f = file("page.html", "w")
#f.write(r)
#f.close()



#mycar=car("https://www.bilbasen.dk/brugt/bil/toyota/avensis/20-d-4d-tx-stcar-5d/3490832")
#mycar.extract_info()
#mycar.print_attrs()
#
#mycar=car("https://www.bilbasen.dk/brugt/bil/audi/a6/20-tdi-170-avant-5d/3468051")
#mycar.extract_info()
#mycar.print_attrs()

if __name__ == '__main__':
    customer_url="https://www.bilbasen.dk/find-en-forhandler/bilforhandler-bilhuset-engmark-as-id8931"
    my_customer=Customer(customer_url)
    my_customer.get_cars_urls()
    my_customer.get_car_info()
    
    my_customer.to_df()
    my_customer.export_csv()