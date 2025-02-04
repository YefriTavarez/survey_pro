// Copyright (c) 2023, Christopher Martinez and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.form.link_formatters["Employee"] = null;

frappe.query_reports["Survey Wise Details"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        },
        {
            "fieldname": "survey_master",
            "label": "Survey Master",
            "fieldtype": "Link",
            "options": "Survey Master",
        },
    ]
};
