import csv
from datetime import *
import sys

discounts = []
results = []
class TimePeriod:
	def __init__(self, startTime, endTime):
		self.startTime = startTime
		self.endTime = endTime

	def verifyIfInTimePeriod(self,time):
		if time >= self.startTime and time <= self.endTime:
			return True

		else:
			return False



class Discount:
	minBillAmount = 0.0
	discount = 0.0
	maxDiscount = sys.maxint
	def __init__(self,discCode,discType, discount,minBillAmount, maxDiscount, timePeriod, paymentMethod):
		self.discCode = discCode
		self.discType = discType
		self.discount = float(discount)
		self.minBillAmount = float(minBillAmount)
		self.maxDiscount = maxDiscount
		self.timePeriod = timePeriod
		self.paymentMethod = paymentMethod

	def checkMinBillAmount(self,billAmount):
		if billAmount >= self.minBillAmount:
			return True
		else: 
			return False

	def checkTimePeriod(self,orderTime):
		if orderTime is None:
			return False
		if self.timePeriod.verifyIfInTimePeriod(orderTime):
			return True
		else: 
			return False

	def checkPaymentMethod(self,paymentMethod):
		if self.paymentMethod is None :
			return True
		elif self.paymentMethod == paymentMethod:
			return True
		else: 
			return False



	def isValidDiscount(self, listOfAttributesAndValuesToBeChecked):
		for attr in listOfAttributesAndValuesToBeChecked.keys():
			if attr == "minBillAmount":
				if not self.checkMinBillAmount(listOfAttributesAndValuesToBeChecked[attr]):
					return False
			elif attr == "timePeriod":
				if not self.checkTimePeriod(listOfAttributesAndValuesToBeChecked[attr]):
					return False
			elif attr == "paymentMethod":
				if not self.checkPaymentMethod(listOfAttributesAndValuesToBeChecked[attr]):
					return False
			else:
				continue
		return True


			

class Order:
	billAmount = 0

	def __init__(self, orderId, billAmount, orderTime, paymentMethod):
		self.orderId = orderId
		self.billAmount = float(billAmount)
		self.orderTime = orderTime
		self.paymentMethod = paymentMethod

class FinalBillDetails:
	def __init__(self,orderId, discountApplied, discCode):
		self.orderId = orderId
		self.discountApplied = discountApplied
		self.discCode = discCode
	def __str__(self):
		return "OrderId :"+str(self.orderId)+"   Discount Applied:"+ str(self.discountApplied)+"  Discount Code"+str(self.discCode)


def convertStringToTime(timeString):
	timeString.replace(" ","")
	timeString.replace(":",".")
	#The above operarions are done to get it to a standard format
	if "." in timeString:
		time = datetime.strptime(timeString,'%I.%M%p')
	else:
		time = datetime.strptime(timeString,'%I%p')
	return time

def populateDiscounts(fileName):
	
	global discounts
	with open(fileName) as discountFile:
		reader = csv.DictReader(discountFile)
		for row in reader:
			timePeriod = None
			timeOfDay = row['time_of_day']
			if timeOfDay:
				timeArray = timeOfDay.split("-")
				startTime = convertStringToTime(timeArray[0])
				endTime = convertStringToTime(timeArray[1])
				timePeriod = TimePeriod(startTime,endTime)
			else:
				startTime = convertStringToTime('12AM')
				endTime = convertStringToTime('11.59PM')
				timePeriod = TimePeriod(startTime,endTime)
			discounts.append(Discount(row['discount_code'], row['discount_type'], row['discount'], 
				row['min_bill_amount'],row['max_discount'],timePeriod, row['payment_method']))

def populateOrders(fileName):
	orders = []
	with open(fileName) as orderFile:
		reader = csv.DictReader(orderFile)
		for row in reader:
			timeOfDay = row['order_time']
			orderTime = convertStringToTime(timeOfDay)
			orders.append(Order(row['order_id'], row['bill_amount'], orderTime, row['payment_method']))
		return orders
	


def assignDiscount(order):
	global discounts
	global results
	assignedDiscount = None
	discountApplied = 0.0
	listOfAttributesAndValuesToBeChecked = {}
	
	listOfAttributesAndValuesToBeChecked["minBillAmount"] = order.billAmount
	listOfAttributesAndValuesToBeChecked["timePeriod"] = order.orderTime
	listOfAttributesAndValuesToBeChecked["paymentMethod"] = order.paymentMethod

	filteredDiscounts = [x for x in discounts if x.isValidDiscount(listOfAttributesAndValuesToBeChecked)]
	if len(filteredDiscounts) > 0:
		assignedDiscount = filteredDiscounts[0]
	if assignedDiscount is not None:
		if assignedDiscount.discType == "FLAT":
			discountApplied = float(assignedDiscount.discount)
		elif assignedDiscount.discType == "PERCENT":
			discountApplied = (float(assignedDiscount.discount)/100.0) * order.billAmount
		if discountApplied > assignedDiscount.maxDiscount:
			discountApplied = assignedDiscount.maxDiscount
		result = FinalBillDetails(order.orderId, discountApplied, assignedDiscount.discCode)
	else:
		result = FinalBillDetails(order.orderId, 0.0, "")

	results.append(result)

def writeResults():
	global results
	writeFile = open("output.csv", "wb")
	wr = csv.writer(writeFile, delimiter=',')
	for result in results:
		line = [str(result.orderId), str(result.discountApplied), str(result.discCode)]
		wr.writerow(line)
	writeFile.close()
        	


arguements = sys.argv
discFile = ""
orderFile = ""
if len(arguements)!= 3:
	print "There is a mismatch in arguements, please enter the discounts file first, and then the order file"
else:
	discFile = arguements[1]
	orderFile = arguements[2]
	populateDiscounts(discFile)
	orders = populateOrders(orderFile)
	for order in orders:
		assignDiscount(order)
	writeResults()








