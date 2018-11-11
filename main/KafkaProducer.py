from pykafka import KafkaClient
import MySQLdb
import pandas
import datetime

class KafkaProducer():
    def __init__(self):
        self.client = KafkaClient(hosts="10.8.4.8:9092")
        self.topic = self.client.topics['chinarail'.encode()]
        self.producer = self.topic.get_producer(delivery_reports=True)
        self.count = 0

    def checkTopics(self):
        print(self.topic)

    def produce_msg(self, msg):
        with self.topic.get_sync_producer() as producer:
            producer.produce(msg.encode())
            print("Sending Message: " + msg)

    def produce_msglist(self, msglist):
        with self.topic.get_sync_producer() as producer:
            mess = ""
            for content in msglist:
                mess += str(content) + ","
            producer.produce(mess.encode())
            print("Sending Message: " + mess)

class MySQLUtil():
    def __init__(self):
        self.db = MySQLdb.connect("localhost", "root", "1234", "TBJUMS", charset="utf8")
        self.virtualdb = MySQLdb.connect("localhost", "root", "1234", "test", charset="utf8")
        self.cursor = self.db.cursor()
        self.virtual_cursor = self.virtualdb.cursor()

    def execuateSQL(self, sql):
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return pandas.DataFrame(list(results)).values

    def close(self):
        self.db.close()

    def getAllApplyInfoByTime(self, startdate, enddate):
        sql = "SELECT * FROM main_returnapplyinfo WHERE draw_datetime >= '{}' AND draw_datetime <= '{}'".format(startdate, enddate)
        self.virtual_cursor.execute(sql)
        results = self.virtual_cursor.fetchall()
        return pandas.DataFrame(list(results)).values

if __name__ == '__main__':
    kafka_producer = KafkaProducer()
    kafka_producer.checkTopics()

    mysqlUtil = MySQLUtil()
    # sql = "SELECT * FROM YARD_DCTZ LIMIT 30"
    # results = mysqlUtil.execuateSQL(sql)
    # print(results)
    # for row in results:
    #     kafka_producer.produce_msglist(row)

    now = datetime.datetime.now()
    # 获取今天零点
    zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                         microseconds=now.microsecond)
    print(zeroToday)
    datestart = datetime.datetime.strptime("2018-08-03 00:00:00", "%Y-%m-%d %H:%M:%S")
    while (datestart <= zeroToday):
        tom = datestart +  datetime.timedelta(days=1)
        results = mysqlUtil.getAllApplyInfoByTime(datestart.strftime("%Y-%m-%d %H:%M:%S"), tom.strftime("%Y-%m-%d %H:%M:%S"))
        datestart += datetime.timedelta(days=1)
        kafka_producer.produce_msglist(results)


    mysqlUtil.close()