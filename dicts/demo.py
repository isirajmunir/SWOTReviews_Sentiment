import csv
import pymysql
pymysql.install_as_MySQLdb()

mydb = MySQLdb.connect(host='localhost',
                       user='siraj',
                       passwd='123',
                       db='bestfoodpk')
cursor = mydb.cursor()

csv_data = csv.reader(file('foodreviews.csv'))
for row in csv_data:
    cursor.execute(
        "INSERT INTO restaurant_review((review_text,review,review_user_id) VALUES(%s, %s, 1)",
        row)

# close the connection to the database.
mydb.commit()
cursor.close()
print ("Done")