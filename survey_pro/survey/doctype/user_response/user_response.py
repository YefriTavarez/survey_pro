# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UserResponse(Document):
	pass

def on_update():
	frappe.db.sql_ddl(
		"""
			ALTER TABLE `tabUser Response`
			ADD COLUMN unique_survey_title VARCHAR(255) GENERATED ALWAYS AS (
				CONCAT(survey_title, ' ', survey_master)
			) STORED

		"""
	)
