# Copyright (c) 2023, Yefri Tavarez and Contributors
# See license.txt

import json

import frappe
import unittest

from .survey_master import SurveyMaster


class TestSurveyMaster(unittest.TestCase):
    def setUp(self):
        self.doc = self.get_test_survey_master()

    def get_test_survey_master(self):
        doctype = "Survey Master"
        name = "survey-YjE3NDhkZjI5MWU5ZjNjYTVkMjBkYTllNDYyOWVl"

        if frappe.db.exists(doctype, name):
            frappe.delete_doc(doctype, name, force=True)

        with open(f"{get_dir()}/survey_master_test.json", encoding="utf-8") as f:
            docdict = json.load(f)

        doc = frappe.get_doc(docdict)

        doc.flags.ignore_links = True
        doc.flags.ignore_permissions = True
        doc.db_insert()

        for child in doc.get_all_children():
            child.flags.ignore_links = True
            child.flags.ignore_permissions = True
            child.parent = doc.name
            child.db_insert()

        doc.reload()

        return doc

    def tearDown(self):
        doctype = self.doc.doctype
        name = self.doc.name

        frappe.delete_doc(doctype, name, force=True)

    def test_update_notification_sent(self):
        self.doc.status = "Published"
        self.doc.update_notification_sent()

        self.assertEqual(
            all([d.employee for d in self.doc.employees]), True)

    doc: SurveyMaster = None


def get_dir():
    return frappe.get_app_path(
        "survey_pro",
        "survey",
        "doctype",
        "survey_master",
    )
