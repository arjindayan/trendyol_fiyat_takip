# -*- coding: utf-8 -*-
import mysql.connector
import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
from datetime import timedelta,datetime


def main():
    print("Trendyol fiyat takip uygulamamıza hoş geldiniz .")
    while True:
        decision=int(input("Lütfen yapmak istediğiniz işlemi seçiniz: \n1-Ürün ekleme\n2-Ürün fiyat güncelleme\n3-Ürün silme\n4-Databasedeki ürünleri göster\n5-Uygulamadan çıkış yap : "))
        if decision==1:
            Append()
        elif decision==2:
            UPDATE()
        elif decision==3:
            Delete()
        elif decision==4:
            show_database()
        else:
            break  
        
        

def Append():
    
    url=input("Lütfen database e eklemek istediğini< ürünün url sini giriniz :")
    
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    html_page = BeautifulSoup(response.content, "html.parser")
        
    ürün_ismi = html_page.find("h1", class_="pr-new-br").find("a").string + " " + html_page.find("h1", class_="pr-new-br").find("span").string
    ürün_fiyat = html_page.find("span", class_="prc-dsc").string
    # ürün_fiyat = float(ürün_fiyat.replace(",", ".").replace(" TL", ""))
    ürün_fiyat = float(ürün_fiyat.replace(".", "").replace(" TL", "").replace(",",".").strip())

    
    
    with open("ürünlink.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    data[ürün_ismi] = url
    
    with open("ürünlink.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
  
    
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="node_app",
        password="Bad.nightmare21"
    )
    cursor = connection.cursor()
    
    sql = "INSERT INTO ürünfiyat(isim,fiyat) VALUES(%s,%s)"

    values=(ürün_ismi,ürün_fiyat)
    cursor.execute(sql,values)
    print("Ürün başarıyla database eklendi.")
    connection.commit()
    print("----------------------------------------------------")
    
    
    
def UPDATE():
    with open("ürünlink.json",encoding="utf-8") as file:
        data = json.load(file)
    print("\n\n")
    
    # print("Ürünlerimiz bunlar : \n")
    # show_database()
    # print("\n\n")

    # isim=input("Lütfen fiyatını güncellemek istediğiniz ürünün ismini giriniz : \n")
    i=0
    liste=[]
    for ürün in data:
        liste.append(ürün)
        print(f"{i}-{ürün}")
        i+=1
    print("\n\n")
    decision=int(input("Lütfen fiyatını güncellemek istediğiniz ürünün numarasını giriniz : "))
    
    if -1<decision<7:
        url=data[liste[decision]]
        headers = {
        "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        html_page = BeautifulSoup(response.content, "html.parser")
        connection=mysql.connector.connect(
        host="localhost",
        user="root",
        database="node_app",
        password="Bad.nightmare21"
        )   
        cursor=connection.cursor()
        
        ürün_ismi = html_page.find("h1", class_="pr-new-br").find("a").string + " " + html_page.find("h1", class_="pr-new-br").find("span").string
        fiyat = html_page.find("span", class_="prc-dsc").string
        # fiyat = float(fiyat.replace(",", ".").replace(" TL", ""))
        fiyat = float(fiyat.replace(".", "").replace(" TL", "").replace(",",".").strip())
        


        sql = "SELECT fiyat FROM ürünfiyat WHERE isim = %s"
        values = (ürün_ismi,)
        cursor.execute(sql, values)
        res = cursor.fetchone()
        
        if res:
            eski_fiyat = res[0]
            if eski_fiyat != fiyat:
                sql2 = "UPDATE ürünfiyat SET fiyat = %s WHERE isim = %s"
                values2 = (fiyat, ürün_ismi)
                cursor.execute(sql2, values2)
                connection.commit()
                print("Fiyat güncellendi.")        
                connection.close()
                
            else:
                print("Fiyat değişikliği yok.")
                print(f"{ürün_ismi} isimli ürünün fiyatı hala {fiyat} Tl")
                
            if fiyat <= 9*eski_fiyat/10:
                print("Üründe güzel bir indirim var")
                connection.close()
        else:
            print("Ürün bulunamadı.")
            connection.close()
        print("---------------------------------------")
    else:
        decision=input("Ürün bulunamadı . Ana menüye dönmek içi (0) ı tekrar arama yapmak için (1) i tuşlayınız : \n")
        if decision =="0":
            main()
        else:
            UPDATE()
            
            
def Update2(isim):
    with open("ürünlink.json", encoding="utf-8") as file:
        data = json.load(file)
    url = data.get(isim)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    html_page = BeautifulSoup(response.content, "html.parser")

    ürün_fiyat = html_page.find("span", class_="prc-dsc").string
    ürün_fiyat = float(ürün_fiyat.replace(".", "").replace(" TL", "").replace(",", ".").strip())

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="node_app",
        password="Bad.nightmare21"
    )
    cursor = connection.cursor()

    sql = "UPDATE ürünfiyat SET fiyat = %s WHERE isim = %s"
    values = (ürün_fiyat, isim)
    cursor.execute(sql, values)
    connection.commit()
    print(f"{isim} adlı ürünün fiyatı başarıyla güncellendi .")


def update_all():
    with open("ürünlink.json",encoding="utf-8") as f:
        data=json.load(f)
        
    for isim in data.keys():
        Update2(isim)




def show_database():
    with open("ürünlink.json",encoding="utf-8")as file:
        data=json.load(file)
    
    for key in data:
        print(f"-{key}")
    
    print("---------------------------------------")
    time.sleep(1)
    

def Delete():
    connection=mysql.connector.connect(
    host="localhost",
    user="root",
    database="node_app",
    password="Bad.nightmare21"
    )   
    cursor=connection.cursor()
    # show_database()
    print("Database deki ürünler bunlar.\n")
    
    
    # name=input("Lütfen database den silmek istediğiniz ürünün ismini giriniz : ")
    with open("ürünlink.json",encoding="utf-8")as file:
        data=json.load(file)
    liste=[]
    
    for key in data:
        liste.append((key))
    if(len(liste)==0):
        print("Silinecek ürün yoktur !!\n\n")
        main()
    i=0
    for ürün in liste:
        print(f"{i}-{ürün}\n")
        i+=1
    
    decision=int(input("Lütfen silmek istediğiniz ürünün numarasını giriniz : "))
    
    data.pop(f"{liste[decision]}")
    
    with open("ürünlink.json","w",encoding="UTF-8") as file:
        json.dump(data,file,ensure_ascii=False)
        
    sql="Delete from ürünfiyat Where isim=%s"
    values=(liste[decision],)
    cursor.execute(sql,values)
    connection.commit()
    print(f"{liste[decision]} isimli ürün database den başarıyla silindi . ")
    print("---------------------------------------")



main()
# schedule.every(12).hours.do(update_all)
# while True:
#     schedule.run_pending()
#     time.sleep(1)

