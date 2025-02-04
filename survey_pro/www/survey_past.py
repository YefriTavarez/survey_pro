# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from frappe import _dict

from survey_pro.survey.doctype.survey_master.survey_master import (
    get_sidebar_items
)

# hack! to be able to say frappe.as_dict
frappe.as_dict = _dict


def get_doclist():
    """Get the list of surveys where the current user was invited to."""

    # allow Administrator to see all surveys
    additional_conditions = "And employees.user Is Not Null"

    # allow other users to see only their surveys
    if frappe.session.user != "Administrator":
        additional_conditions = f"And employees.user = {frappe.session.user!r}"

    return frappe.db.sql(
        f"""
            Select
                survey.route,
                survey.survey_title,
                survey.expiration_date,
                If(
                    Exists(
                        Select
                            response.name
                        From
                            `tabUser Response` As response
                        Where
                            response.survey_master = survey.name
                    ), "Completed", "Pending"
                ) As status
            From
                `tabSurvey Master` As survey
            Inner Join
                `tabSurvey Employees` As employees
                On
                    employees.parent = survey.name
                    And employees.parentfield = "employees"
                    And employees.parenttype = "Survey Master"
            Where
                survey.status = "Closed"
                {additional_conditions}
        """, as_dict=True
    )


def get_context(context):
    """Get context for the survey."""

    context.update({
        "doclist": get_doclist(),
        # utils and others
        "is_guess": frappe.session.user == "Guest",
        "show_sidebar": True,
        "sidebar_items": get_sidebar_items(),
        "scrub": frappe.scrub,
        "format": frappe.format,
    })

    return context
