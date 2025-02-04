// Copyright (c) 2023, Miguel Higuera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Survey Summary"] = {
    "filters": [
        {
            "fieldname": "name",
            "label": "Survey Master",
            "fieldtype": "Link",
            "options": "Survey Master"
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": [
                "",
                "Published",
                "Closed",
            ]
        },
    ]
};
