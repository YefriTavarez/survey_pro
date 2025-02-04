# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SurveyQuestion(Document):
    def on_update(self):
        self.update_refs()

    def set_user_response(self, survey_master):
        """Set the user response for a survey master"""
        self.survey_master = survey_master

    @property
    def answer(self):
        """Get the answer for a survey master for current user"""
        if not self.survey_master:
            frappe.throw(
                """Please set survey_master property first using the
                set_user_response method."""
            )

        return frappe.db.get_value(
            "User Response",
            {
                "survey_master": self.survey_master,
                "question": self.name,
                "user": frappe.session.user,
            },
            "response_value",
        )

    def update_refs(self):
        """Update the details in other doctypes"""
        frappe.db.sql(f"""
            Update
                `tabSurvey Questions` As childtable
            Inner Join
                `tabSurvey Question` As master
                On
                    childtable.question_id = master.name
            Set
                childtable.question = master.question,
                childtable.question_type = master.question_type
            Where
                master.name = {self.name!r}
                And childtable.parenttype = "Survey Template"
                Or (
                    childtable.parenttype = "Survey Master"
                    And childtable.parent In (
                        Select
                            survey.name
                        From
                            `tabSurvey Master` As survey
                        Where
                            survey.status != "Closed"
                    )
                )
        """)

    survey_master: str
