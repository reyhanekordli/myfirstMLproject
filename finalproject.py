import requests
from bs4 import BeautifulSoup
import mysql.connector
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn import tree



#connecting to MySQL (enter your password if have any):
data = mysql.connector.connect(user = "root" , password = "")
cursor = data.cursor()

#creating database:
cursor.execute("CREATE DATABASE Computer_data;")
cursor.execute("USE Computer_data;")
cursor.execute("CREATE TABLE laptops (CPU VARCHAR(20) , RAM VARCHAR(20) , GPU VARCHAR(20) , Price VARCHAR(20));")

n = 1
m = 1
while (n < 200):
#getting info from main site:
    URL = ("https://www.kalaoma.com/category-laptop?PageNumber=%s&ShowStockProductsOnly=true" %(str(m)))
    re = requests.get(URL)
    soup = BeautifulSoup(re.text , "html.parser")
    laptops = soup.find_all("div" , attrs = {"class" : "km-product km-theme-5"})

#getting info from every laptop page:
    for item in laptops:
        finding = item.find("a" , attrs = {"target" : "_blank"})
        address = finding["href"]
        URL_new = "https://www.kalaoma.com" + address
        req = requests.get(URL_new)
        soup1 = BeautifulSoup(req.text , "html.parser")
        more = soup1.find("ul" , attrs = {"class" : "detailsProductInfo"})
        details = more.find_all("span" , attrs = {"class" : "products-attribute-value"})
        cpu = details[1].text
        ram = details[2].text
        gpu = details[4].text
        price = (soup1.find("span" , attrs = {"itemprop" : "price"})).text
        cursor.execute("INSERT INTO laptops VALUE (%s , %s , %s , %s);" , (str(cpu) , str(ram) , str(gpu) , str(price)))
        n += 1
    m += 1

#finishing the process of inserting data to database:
data.commit()
data.close()


#ML part:


#importing the data from database that we created (enter password if have any):
mydata = mysql.connector.connect(user = "root" , password = "" , database = "Computer_data")
myhandle = mydata.cursor()
myhandle.execute("SELECT * FROM laptops;")
myresult = myhandle.fetchall()

#Turning all data into csv (enter the address ypu want):
with open("C:\\Users\\myresult.csv" , "w") as file:
    file.write("CPU")
    file.write(",")
    file.write("RAM")
    file.write(",")
    file.write("GPU")
    file.write(",")
    file.write("Price")
    file.write("\n")

    for item in myresult:
        file.write(item[0])
        file.write(",")
        file.write(item[1])
        file.write(",")
        file.write(item[2])
        file.write(",")

        x = item[3][1:]
        x1 = x.split(",")
        x1 = "".join(x1)
        file.write(x1)
        file.write("\n")

file.close()


#reading data from csv with pandas (enter your address of csv):
data = pd.read_csv("C:\\Users\\myresult.csv")
data.shape
data["RAM"] = data["RAM"].str.replace(" گیگابایت" , "")
data["RAM"] = data["RAM"].astype("int32")
data["Price"] = data["Price"].astype("int32")

#turning str data into int32:
enc = LabelEncoder()
enc.fit(data["CPU"])
data["CPU"] = enc.transform(data["CPU"])

enc.fit(data["GPU"])
data["GPU"] = enc.transform(data["GPU"])

#creating X , y for regression:
X = data[["CPU" , "RAM" , "GPU"]]
y = data["Price"]

reg = tree.DecisionTreeRegressor()
reg.fit(X , y)

#input cpu , ram , gpu (enter ram with only number (NO گیگابایت)):
cpu = input("Enter cpu_data : ")
ram = int(input("Enter ram_data : "))
gpu = input("Enter gpu_data : ")
new_data = [[cpu , ram , gpu]] 

df = pd.DataFrame(data = new_data)
enc.fit(df[0])
df[0] = enc.transform(df[0])

enc.fit(df[2])
df[2] = enc.transform(df[2])


#finally predicting price:
my_regg = reg.predict(df)
print(my_regg)