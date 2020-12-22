# -*- coding: utf-8 -*-
# Copyright (c) 2018, libracore and contributors
# For license information, please see license.txt
#
# call the API from
#   /api/method/icalfeed.icalfeed.utils.calendar.download_calendar?secret=[secret]
#

from icalendar import Calendar, Event
from datetime import datetime
import frappe

def get_calendar(secret):
    # check access
    enabled = frappe.db.get_value("iCal Feed Settings", "iCal Feed Settings", "enabled")
    if float(enabled) == 0:
        return
    erp_secret = frappe.db.get_value("iCal Feed Settings", "iCal Feed Settings", "secret")
    if not secret == erp_secret:
        return
        
    # initialise calendar
    cal = Calendar()

    # set properties
    cal.add('prodid', '-//iCalFeed module//libracore//')
    cal.add('version', '2.0')

    # get data
    sql_query = """SELECT * FROM `tabEvent` WHERE `event_type` = 'Public'"""
    events = frappe.db.sql(sql_query, as_dict=True)
    # add events
    for erp_event in events:
        event = Event()
        event.add('summary', erp_event['subject'])
        event.add('dtstart', erp_event['starts_on'])
        if erp_event['ends_on']:
            event.add('dtend', erp_event['ends_on'])
        event.add('dtstamp', erp_event['modified'])
        event.add('description', erp_event['description'])
        # add to calendar
        cal.add_component(event)
    
    return cal

@frappe.whitelist(allow_guest=True)
def download_calendar(secret):
    frappe.local.response.filename = "calendar.ics"
    calendar = get_calendar(secret)
    if calendar:
        frappe.local.response.filecontent = calendar.to_ical()
    else:
        frappe.local.response.filecontent = "No access"
    frappe.local.response.type = "download"