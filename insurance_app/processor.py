from .classes import *

class Processor():

    def update_company(self):
        db_obj = DatabaseAccess()
        obj = Updates()
        modify_obj = DataModify()
        data = db_obj.get_update_data()
        print(1)
        tuple_obj = obj.parser()
        rows = Company.objects.filter(update_date=data)
        modify_obj.modify_company(tuple_obj[0])
        obj.compare(rows, tuple_obj[0])
        print(db_obj.upypload_companies(tuple_obj[0]) + '1')

    def load_company(self):
        db_obj = DatabaseAccess()
        obj = Updates()
        modify_obj = DataModify()
        print(2)
        tuple_obj = obj.parser()
        modify_obj.modify_company(tuple_obj[0])
        print(db_obj.upload_companies(tuple_obj[0]) + '2')