# Copyright (c) 2023, Miguel Higuera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_columns():
    return [
        "Title:Data:200",
        "Status:Data:100",
        "User Count:Int:120",
        "Responses:Int:100",
        "Expiration Date:Date:150",
        "ID:Link/Survey Master:100",
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql(f"""
        Select
            survey.survey_title,
            survey.status,
            Count(Distinct users.user),
            Count(Distinct response.user),
            survey.expiration_date,
            survey.name
        From
            `tabSurvey Master` As survey
        Inner Join
            `tabSurvey Users` As users
            On
                users.parent = survey.name
                And users.parentfield = "users"
                And users.parenttype = "Survey Master"
        Left Join
            `tabUser Response` As response
            On
                response.survey_master = survey.name
        Where
            {conditions}
        Group By
            survey.name
    """, as_list=True)

    return data


def get_conditions(filters):
    conditions = []

    if filters.name:
        conditions.append(f"survey.name = {filters.name!r}")

    if filters.status:
        conditions.append(f"survey.status = {filters.status!r}")
    else:
        conditions.append("survey.status In ('Published', 'Closed')")

    return " And ".join(conditions)
