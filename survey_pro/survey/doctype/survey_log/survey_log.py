# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document

from frappe import _dict

# hack! to be able to say frappe.as_dict
frappe.as_dict = _dict


class SurveyLog(Document):
    @frappe.whitelist()
    def process_log(self):
        """Process the logs and save the user responses."""
        doctype = "User Response"

        user_responses = frappe.as_dict(
            json.loads(self.user_response)
        )

        self.validate_if_response_exists()
        for question_id, response in user_responses.items():
            if not isinstance(response, dict):
                continue  # skip non dict items

            doc = frappe.new_doc(doctype)

            doc.update({
                "response_date": self.creation,
                "survey_master": self.survey_master,
                "user": self.user,
                "full_name": frappe.utils.get_fullname(self.user),
                "question": question_id,
                "question_content": response.get("question_content"),
                "response_value": response.get("user_response"),
                "question_type": response.get("question_type"),
                "survey_log": self.name,
            })

            try:
                doc.insert(ignore_permissions=True)
            except:  # pylint: disable=bare-except
                frappe.log_error(
                    frappe.get_traceback(),
                    "Survey Log: Error while inserting Survey Response"
                )
                self.status = "Errored"
                self.error_log = frappe.get_traceback()
                self.db_update()
            else:
                self.db_set("status", "Imported")

    def validate_if_response_exists(self):
        """Validate if the response already exists."""
        doctype = "User Response"
        filters = {
            "survey_master": self.survey_master,
            "user": self.user,
        }

        if frappe.db.exists(doctype, filters):
            frappe.db.rollback()

            error_message = f"User Response already exists for {self.survey_master!r}"
            self.status = "Errored"
            self.error_log = error_message
            self.db_update()
            frappe.db.commit()

            frappe.throw(error_message)

    status: str
    user: str
    survey_master: str
    user_response: str
    error_log: str
