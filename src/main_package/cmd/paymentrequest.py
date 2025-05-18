from src.main_package.paymentrequest.ackAndPayRequest import sendAckAndPayRequest

people_data = [
    {"guestName": "Mrs Priya Ravikumar", "email": "priyaravikumar2000@yahoo.com", "adultNos": 2, "kidsNos": 2,
     "voluntaryPrice": 100, "raffle": 5, "uniqueRef": "PR1"},
    # {"guestName": "Jane Smith", "email": "ravi.sivaraj@gmail.com", "adultNos": 2, "kidsNos": 0,
    #  "voluntaryPrice": 0, "uniqueRef": "JS001"},
    # {"guestName": "Bob Johnson", "email": "ravi.sivaraj@gmail.com",
    #  "adultNos": 0, "kidsNos": 2, "voluntaryPrice": 100, "uniqueRef": "JD001"
    #  },
]

sendAckAndPayRequest(people_data, "paymentrequest.html")
