"""Field description for the data base in python.
   Drives the import and the web UI. """

import MySQLdb
import base64
import urllib

__author__ = "chris@austin-lane.net"
__version__ = "$Revision: 1.4 $"
__date__ = "$Date: 2008/03/12 14:16:59 $"
__copyright__ = "Copyright (c) 2006 Chris Austin-Lane"
__license__ = "GPLv2"

class DB:
    the_db = {}
    DB = "comment"
    def __init__(self,DB):
        self.DB = DB
        
    def get_db(self,req):
        if self.the_db == {}:
            self.the_db = MySQLdb.connect(host='localhost', user='lanstin', passwd='dcv9zaq', db=self.DB)
        try:
            qqq = self.the_db.cursor()
            d = qqq.execute("show tables");
            self.the_db.commit()
        except MySQLdb.OperationalError:
            self.the_db = MySQLdb.connect(host='localhost', user='lanstin', passwd='dcv9zaq', db=self.DB)
        return self.the_db


def get_c_id(sql_str, db):
    """ Run a SQL query to find out if it has any rows"""
    qqq = db.get_db(0).cursor()
    c_id = -1
    d = qqq.execute(sql_str)
    if d == 1:
        row = qqq.fetchone();
        c_id = row[0]
    qqq.close()
    return c_id


(SQL_INT, SQL_CHAR, SQL_DATE, SQL_NUMERIC, SQL_DOUBLE) = range(5)

(UI_SUMMARY, UI_DETAIL, UI_EDITABLE, UI_HOUSE_INDEX, UI_UTIL, UI_HIDDEN, UI_LINKABLE, UI_ZENDO, UI_PERSON_INDEX, UI_BASE64) = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)

gfields = []
gfields_by_name = {}

gsort_names = {'query': ["c_url","c_name","c_blog", "c_body", "c_subject"]}



def add_field_not_file(name, display_name, sql_type = SQL_INT, table_name="", flags=0):
    
    a = Field(name, display_name, sql_type, table_name, -1, -1, flags)
    return a

def add_field(name, display_name, beginning_field = -1, length=-1, sql_type = SQL_INT, table_name="", flags=0):
    a = Field(name, display_name, sql_type, table_name, beginning_field, length, flags)
    return a

def get_field_by_name(name):
    "get a field by name"
    return gfields_by_name[name]


class Field:
    "Used to define a field in the electoral data system"
    name = ""
    display_name = ""
    sql_type = SQL_INT
    table_name = ""
    flags = 0
    beginning_field = 0
    length = 0
    flags = 0
    default_ui = ""
    db = ()
    def __init__ (self, name, display_name, sql_type = SQL_INT, table_name="", beginning_field = -1, length=-1, flags=0, y2k = 88, db = {}):
        self.name = name
        self.display_name = display_name
        self.sql_type = sql_type
        self.table_name= table_name
        self.beginning_field = beginning_field
        self.length = length
        self.flags = flags
        self.y2k_threshold = 88
        self.y2k_low = 1900
        self.y2k_high = 1800
        self.default_ui_value = ""
        self.db = db
        gfields.append(self)
        gfields_by_name[name] = self
        

    def base64_encode(self):
        self.flags |= UI_BASE64;

    def set_default_ui_value(self, value):
        self.default_ui_value = value

    def get_default_ui_value(self):
        return self.default_ui_value
    
    def get_name(self):
        return self.name

    def get_display_name(self):
        return self.display_name

    def get_flags(self):
        return self.flags

    def get_table_name(self):
        return self.table_name

    def set_y2k_threshold(self, y2k_threshold, y2k_low, y2k_high):
        self.y2k_threshold = y2k_threshold
        self.y2k_low = y2k_low
        self.y2k_high = y2k_high
        
    def sql_type(self):
        return self.sql_type

    def sql_do_string(self, in_str):
        "is field blank"
        skip = False
        if self.sql_type == SQL_INT:
            if (" " * self.length) == in_str:
                skip = True;
        elif self.sql_type == SQL_DATE:
            if in_str[0] == ' ':
                skip = True;
        return skip

    def sql_do(self, line):
        "is field blank"
        return self.sql_do_string(self, line[self.beginning_field : self.length + self.beginning_field])

    def sql_value_string(self, instr, db):
        print "name: " + self.name
        vvv = ""
        if self.sql_type == SQL_INT:
            vvv = str(instr)
        elif self.sql_type == SQL_DATE:
            year  = int(instr[:2]) 
            if year < self.y2k_threshold:
                year = year + self.y2k_low
            else:
                year = year + self.y2k_high
            month = int(instr[2:4])
            day   = int(instr[4:6])
            vvv = "'%04d-%02d-%02d'" % (year, month, day)
        elif self.sql_type == SQL_CHAR:
            vvv = db.escape(instr, db.encoders)
        return vvv
        
    
    def sql_value(self, line, db):
        "get safe sql value"
        return self.sql_value_string(self, line[beginning_field : self.length + self.beginning_field])

    def sql_value_value(self, value, db):
        "get safe sql value"
        # should do this better but at least it's all in _fields
        vvv = "%d" % (self.sql_type,)
        
        if self.sql_type == SQL_INT:
            vvv = value
        elif self.sql_type == SQL_NUMERIC:
            vvv = value
        elif self.sql_type == SQL_DOUBLE:
            vvv = value
        elif self.sql_type == SQL_DATE:
            vvv = value
        elif self.sql_type == SQL_CHAR:
            if self.flags & UI_BASE64:
                value = base64.urlsafe_b64decode(urllib.unquote(value));
            vvv = db.escape(value, db.encoders);
        return vvv

class ListIteratorGen:

    index = 0
    fields = 0

    def __init__(self, list_of_fields):
        self.index = 0
        self.list_of_fields = list_of_fields;

    def __iter__(self):
        return self;
    
    def next(self):
        lf = self.list_of_fields.get_fields_by_number()
        if len(lf) == self.index:
            raise StopIteration
        self.index = self.index + 1
        return lf[self.index - 1]
    

class ListOfFields:

    fields_by_number = []
    fields_by_name = {}
    field_number_by_name = {}

    def __init__(self):
        self.fields_by_number = []
        self.fields_by_name = {}
        self.field_number_by_name = {}

    def __add__(self, other):
        result = ListOfFields()
        result.fields_by_number = self.fields_by_number + other.fields_by_number;
        for k in self.fields_by_name.keys():
            result.fields_by_name[k] = self.fields_by_name[k]
        for k in other.fields_by_name.keys():
            result.fields_by_name[k] = other.fields_by_name[k]
        j = 0
        for i in result.fields_by_number:
            result.field_number_by_name[i.get_name()] = j
            j = j + 1
        return result

    def __iter__(self):
        return ListIteratorGen(self)

    def length(self):
        return len(self.fields_by_number)

    def add_field(self, field):
        self.fields_by_number.append(field)
        self.fields_by_name[field.get_name()] = field
        self.field_number_by_name[field.get_name()] = len(self.fields_by_number) - 1
        
    def add_fields_by_names(self, **args):
        for name in args:
            field = self.fields_by_name[name]
            if field:
                self.add_field(field)

    def field_in_table(self, table_name, field_name):
        if not self.fields_by_name.has_key(field_name):
            return False
        field = self.fields_by_name[field_name];
        return (table_name == field.table_name)
        
    def get_fields_by_number(self):
        return self.fields_by_number

    def get_field_number_by_name(self, name):
        return self.field_number_by_name[name]

    def get_field_by_name(self, name):
        return self.fields_by_name[name]
    
    def show_print(self):
        print "Showing list of fields"
        for g in self:
            print g.get_name()

    def sort(self, sort_name):
        if not gsort_names.has_key(sort_name):
            return
        # must first grab mentioned fields
        new_fields_by_number = []
        for i in gsort_names[sort_name]:
            new_fields_by_number.append(self.fields_by_name[i])
            self.fields_by_number[self.field_number_by_name[i]] = None
        # then remaining fields
        for i in self.fields_by_number:
            if i != None:
                new_fields_by_number.append(i)

        # now rebuild field_number_by_name
        j = 0
        for i in new_fields_by_number:
            self.field_number_by_name[i.get_name()] = j
            j = j + 1
        self.fields_by_number = new_fields_by_number
        return
        
def get_fields_by_table(table_name):
    result = ListOfFields()
    for f in gfields:
        if f.get_table_name() == table_name:
            result.add_field(f)
    return result

def get_fields_by_table_and_flag(table_name, flag):
    result = ListOfFields()
    for f in gfields:
        if (f.get_table_name() == table_name) and (f.get_flags() & flag):
            result.add_field(f)
    return result

def get_fields_by_table_and_not_flag(table_name, flag):
    result = ListOfFields()
    for f in gfields:
        if (f.get_table_name() == table_name) and not (f.get_flags() & flag):
            result.add_field(f)
    return result

add_field_not_file("c_id",      "Comment ID",      SQL_INT,      "comment", 16)
add_field_not_file("c_url",     "Comment URL",     SQL_CHAR,      "comment", 0).base64_encode()
add_field_not_file("c_name",    "Comment Name",    SQL_CHAR,      "comment", 0)
add_field_not_file("c_email",   "Comment Email",   SQL_CHAR,      "comment", 0)
add_field_not_file("c_blog",    "Comment Blog",    SQL_CHAR,      "comment", 0)
add_field_not_file("c_body",    "Comment Body",    SQL_CHAR,      "comment", 0)
add_field_not_file("c_subject", "Comment Subject", SQL_CHAR,      "comment", 0)
add_field_not_file("c_ip",      "Comment IP",      SQL_CHAR,      "comment", 0)
add_field_not_file("c_date",    "Comment Date",    SQL_DATE,      "comment", 0)

# want to add varying value list for drop downs etc.  
        
