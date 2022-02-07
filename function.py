import mysql.connector
import config as db

class Return_list:
  def list_payment(self, payment_user_results):
    payment_results = []
    for payment_user_result in payment_user_results:
        payment_dict = dict(payment_user_result)
        payment_results.append([str(payment_dict["user_id"]), int(payment_dict["payment_id"]), int(payment_dict["trip_id"]), int(payment_dict["price"]), str(payment_dict["place"]), str(payment_dict["event_name"])])
    return payment_results

  def list_user(self, user_id_and_name):
    user_results = []
    for number in range(len(user_id_and_name)):
        user_results.append([user_id_and_name[number].user_id, user_id_and_name[number].user_name])
    return user_results
