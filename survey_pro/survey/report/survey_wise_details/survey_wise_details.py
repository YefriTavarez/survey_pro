# Copyright (c) 2023, Christopher Martinez and contributors
# For license information, please see license.txt

import frappe
from frappe import _


# rushed code
# don't blame the developer

def execute(filters=None):
    idxs = set()
    columns = list()

    set_columns(columns)
    data = get_data(filters, columns, idxs)
    
    # # Pad rows with None values to match the number of columns
    # for row in data:
    #     while len(row) < len(columns):
    #         row.append(None)
    
    # frappe.throw(f"columns {len(columns)} data {len(data[0])}")
    
    return columns, data
    

def set_columns(columns):
    columns.extend([
        # Survey
        _('Survey ID:Link/Survey Master:110'),
        _('Title:Data:200'),
        _('Status:Data:150'),
        _('Expiration Date:Date:150'),
        # Response
        _('User ID:Link/User:70'),
        _('Full Name:Data:150'),
        _('Count:Int:100'),
        # repeatable
        # _('Response Date:Date:160'),
        # _('Question ID:Link/Survey Question:150'),
        # _('Question:Data:250'),
        # _('Response Value:Data:250'),
        # _('Response ID:Link/User Response:150'),
    ])

def get_data(filters, columns, idxs):
    conditions = get_conditions(filters)

    resultset = frappe.db.sql(f"""
        Select
            response.user As user,
            user.full_name As full_name,
            (
                Select
                    Count(1)
                From
                    `tabSurvey Questions` As questions
                Where
                    questions.parent = survey.name
                    And questions.parenttype = 'Survey Master'
                    And questions.parentfield = 'questions'
            ) As question_count,
            response.response_date As response_date,
            response.question As question_id,
            response.question_content As question_content,
            response.response_value As response_value,
            response.name As response_id,
            survey.name As survey_id,
            survey.survey_title As survey_title,
            survey.status As survey_status,
            survey.expiration_date As survey_expiration_date
        From
            `tabSurvey Master` As survey
        Inner Join
            `tabUser Response` As response
            On
                response.survey_master = survey.name
        Inner Join
            `tabUser` As user
            On
                user.name = response.user
        Where 
            {conditions}
        Order By
            response.user,
            response.question
    """, as_dict=True)

    users_details = dict()
    survey_details = dict()
    by_survey_and_users = dict()
    for row in resultset:
        # repeat this for each question
        # response_date, question_id, question, response_value, response_id
        by_survey_and_users.setdefault((row.survey_id, row.user), []).append((
            row.response_date,
            row.question_id,
            row.question_content,
            row.response_value,
            row.response_id
        ))
        
        users_details.setdefault(row.user, row)
        survey_details.setdefault(row.survey_id, row)
        
    out = list()
    for key, rows in by_survey_and_users.items():
        survey_id, user = key

        for idx, _ in enumerate(rows, start=1):
            add_repeatable_columns_if_not_added(idx, idxs, columns)
            
        _row = [
            survey_details[survey_id]["survey_id"],
            survey_details[survey_id]["survey_title"],
            survey_details[survey_id]["survey_status"],
            survey_details[survey_id]["survey_expiration_date"],
            users_details[user]["user"],
            users_details[user]["user_name"],
            len(rows),
        ]
        
        for row in rows:
            # (
            #     response_date,
            #     question,
            #     question_content,
            #     response_value,
            #     response_id
            # ) = row
                
            _row.extend(row)

        out.append(_row)

    return out


def add_repeatable_columns_if_not_added(idx, idxs, columns):
    # column set template
    additional_cols = (
        "Response Date {idx}:Date:160",
        "Question ID {idx}:Link/Survey Question:150",
        "Question {idx}:Data:250",
        "Response Value {idx}:Data:250",
        "Response ID {idx}:Link/User Response:150",
    )
    
    for template in additional_cols:
        col = template.format(idx=idx)
        if idx not in idxs:
            columns.append(col)
        
    idxs.add(idx)


def get_conditions(filters):
    conditions = list()

    # always on filter
    conditions.append("survey.status != 'Draft'")

    if filters.from_date:
        conditions.append(
            f"survey.expiration_date >= {filters.from_date!r}"
        )

    if filters.to_date:
        conditions.append(
            f"survey.expiration_date <= {filters.to_date!r}"
        )

    if filters.survey_master:
        conditions.append(
            f"survey.name = {filters.survey_master!r}"
        )

    return " And ".join(conditions)
