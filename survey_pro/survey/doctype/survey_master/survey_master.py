# Copyright (c) 2023, Miguel, Christopher and contributors
# For license information, please see license.txt

import json
import base64

import frappe

from frappe import _, _dict
from frappe.utils import cint

from frappe.utils.nestedset import get_descendants_of
from frappe.website.website_generator import WebsiteGenerator

# hack! to be able to say frappe.as_dict
frappe.as_dict = _dict


class SurveyMaster(WebsiteGenerator):
    def autoname(self):
        self.name = self.get_new_name()

    def after_insert(self):
        self.set_route()

    def validate(self):
        self.is_users_table_empty()

    def before_save(self):
        self.update_notification_sent()

    def set_route(self):
        """Set the route for the survey."""
        route = f"{self.name}"
        self.db_set("route", route)

    def is_published(self):
        """Check if the survey is published."""
        return self.status == "Published"

    def is_closed(self):
        """Check if the survey is closed."""
        return self.status == "Closed"

    def is_draft(self):
        """Check if the survey is closed."""
        return self.status == "Draft"

    def has_already_participated(self):
        """Check if the user has already participated in the survey."""
        doctype = "User Response"
        filters = {
            "survey_master": self.name,
            "user": frappe.session.user,
        }

        return frappe.db.exists(doctype, filters)

    def has_permissions(self):
        """Check if the user has permissions to participate in the survey."""
        current_user = frappe.session.user

        if current_user == "Administrator":
            return True

        return current_user in [d.user for d in self.users]

    def get_new_name(self):
        """Generate a new name base64 for the survey."""
        doctype = self.doctype

        _hash = frappe.generate_hash(length=30)
        base64_hash = base64.b64encode(_hash.encode("utf-8"))
        name = f"survey-{base64_hash.decode('utf-8')}"

        if frappe.db.exists(doctype, name):
            return self.get_new_name()

        return name

    @frappe.whitelist()
    def get_questions_from_template(self):
        """Get questions from the Template."""

        if not self.survey_template:
            return []

        questions = frappe.db.sql(f"""
            SELECT
                question_id,
                question,
                question_type
            FROM
                `tabSurvey Questions`
            WHERE
                parent = {self.survey_template!r}
        """, as_dict=True)

        return questions

    @frappe.whitelist()
    def get_users(self):
        """Get users allowed to participate in the survey."""

        conditions = self.get_users_conditions()

        users = frappe.db.sql(f"""
            SELECT
                name as user,
                full_name
            FROM
                `tabUser`
            WHERE
                {conditions}
        """, as_dict=True)

        return users

    def get_users_conditions(self):
        conditions = list()

        # always on filter
        conditions += ["status = 'Active'"]

        if self.based_on == "Employee Details":
            # additional filters
            if self.client:
                conditions.append(f"client = {self.client!r}")

            if self.vertical:
                conditions.append(f"vertical = {self.vertical!r}")

            if self.campaign:
                conditions.append(f"campaign = {self.campaign!r}")

            if self.branch:
                conditions.append(f"branch = {self.branch!r}")

            if self.department:
                doctype = "Department"
                name = self.department
                departments = (
                    name,
                    *get_descendants_of(doctype, name)
                )

                if len(departments) == 1:
                    conditions.append(f"department = {departments[0]!r}")
                else:
                    conditions.append(f"department In {departments}")

        elif self.based_on == "Training Event":
            users = frappe.db.sql_list(f"""
                SELECT
                    user
                FROM
                    `tabTraining Event Employee`
                WHERE
                    parent = {self.training_event!r}
            """)
            if not users:
                frappe.throw("The training event has no users")

            conditions.append(f"name In {tuple(users)}")
        else:
            frappe.throw("Invalid based on")

        if self.designations:
            designations = (d.designation for d in self.designations)
            designation_list = ", ".join(f"{d!r}" for d in designations)
            conditions.append(f"designation In ({designation_list})")

        return " And ".join(conditions)

    def get_questions(self):
        """Get survey question in a format the HTML template can use."""
        questions = list()

        doctype = "Survey Question"
        for question in self.questions:
            name = question.question_id

            doc = frappe.get_doc(doctype, name)
            doc.set_user_response(self.name)
            questions.append(doc)

        return questions

    def get_context(self, context):
        """Get context for the survey."""
        show_sidebar = self.has_permissions() and (
            self.is_published()
            or self.is_closed()
        )

        context.update({
            # doctype props
            "survey_id": self.name,
            "intro": self.introduction,
            "survey_title": f"{self.survey_title}",
            "is_published": self.is_published(),
            "is_closed": self.is_closed(),
            "is_draft": self.is_draft(),
            "questions": self.get_questions(),
            "survey_status": self.status,

            # utils and others
            "show_sidebar": show_sidebar,
            "allow_participation": self.has_permissions(),
            "has_already_participated": self.has_already_participated(),
            "sidebar_items": get_sidebar_items(),
            "scrub": frappe.scrub,
            "unpublished_message": self.get_unpublish_message(),
        })

    def is_users_table_empty(self):
        if not self.users:
            frappe.throw(
                "The Users Table is empty. You must add at least one user.")

    def update_notification_sent(self):
        """Update notification sent if applies"""
        if not (self.status == "Published"
                and self.db_get("status") == "Draft"):
            return

        for user in self.users:
            if user.notified:
                continue

            self.notify_one(user)

            user.notified = 1
            user.db_update()

    def notify_one(self, user):
        """Send the email to one Employee at a time."""
        ...
        # if not user.user:
        #     return

        # context = frappe.as_dict(doc={
        #     "survey_title": self.survey_title,
        #     "survey_link": f"{frappe.utils.get_url()}/{self.name}",
        #     "user_name": user.user_name,
        # })

        # frappe.sendmail(
        #     recipients=user.user,
        #     subject=f"Survey Invitation | {self.survey_title}",
        #     message=frappe.render_template(
        #         "templates/emails/invitation_to_participate_in_survey.html",
        #         context
        #     ),
        #     reference_doctype=self.doctype,
        #     reference_name=self.name,
        # )

    def get_unpublish_message(self):
        if frappe.session.user == "Guest":
            return "You're not authorized to see this page"

        if not self.has_permissions():
            return "It seems like you were not invited to participate on this survey."

        if self.status == "Draft":
            return """This is a draft survey.<br>
                <small>You cannot participate in this survey yet.</small>"""
        else:
            return "This survey has been closed already."

    @classmethod
    def validate_user_response(cls, survey_id, user_response):
        """Validate user response."""
        if isinstance(user_response, str):
            user_response = json.loads(user_response)

        _user_response = frappe.as_dict(user_response)

        self = frappe.get_doc("Survey Master", survey_id)

        if not self.is_published():
            frappe.throw("This survey is not published.")

        if not self.has_permissions():
            frappe.throw("You're not authorized to participate on this survey")

        if not self.questions:
            frappe.throw("This survey has no questions.")

        # validate this question belongs to this survey
        valid_questions = {q.question_id for q in self.questions}
        for question_id, detail in _user_response.items():
            detail = frappe.as_dict(detail)
            if question_id not in valid_questions:
                frappe.throw(f"Invalid question {detail.question_content!r}")

        # validate for reqd questions
        # all questions have an optional field called "optional"
        # if optional is not set, it is assumed to be False
        # if optional is set to True, it means the question is optional
        # if optional is set to False, it means the question is required
        for question_id, detail in _user_response.items():
            detail = frappe.as_dict(detail)
            question = frappe.get_doc("Survey Question", question_id)
            if not question.optional and not detail.user_response:
                frappe.throw(
                    f"Question {detail.question_content!r} is required.")

    survey_title = str()
    introduction = str()
    expiration_date = str()
    route = str()
    status = str()
    published = bool()
    survey_template = str()
    questions = list()
    based_on = str()
    client = str()
    vertical = str()
    campaign = str()
    training_event = str()
    branch = str()
    designations = list()
    department = str()
    users = list()


@frappe.whitelist()
def save_user_response(survey_id, user_response):
    """This is the first contact the user response will have with the server.
    Then this logs are meant to be processed in a background job."""

    doctype = "Survey Log"

    doc = frappe.new_doc(doctype)
    # _user_response = json.loads(user_response)

    SurveyMaster.validate_user_response(survey_id, user_response)

    doc.update({
        "survey_master": survey_id,
        "user_response": frappe.as_json(user_response),
        "user": frappe.session.user,
    })

    doc.flags.ignore_permissions = True

    try:
        doc.save()
    except:  # pylint: disable=bare-except
        frappe.log_error()
        return """Error: An error has ocurred in the server.
        <br>Most likely this error is not related with you... for now, 
        just inform your <strong>Manager</strong> or the person that gave you this like to participate
        and show them the error."""

    # Todo: Add a background job to process the logs
    method = "process_log"

    frappe.enqueue_doc(
        doc.doctype,
        doc.name,
        method,
        queue="long",
        timeout=300
    )

    return "Info: Your response was saved sucessfully."


def get_sidebar_items():
    return [
        {
            "title": _("Surveys In Progress"),
            "route": "/survey-in-progress",
        },
        {
            "title": _("Past Surveys"),
            "route": "/survey-past",
        },
    ]
