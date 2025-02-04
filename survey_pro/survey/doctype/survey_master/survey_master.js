// Copyright (c) 2022, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Survey Master', {
	refresh(frm) {
		frm.trigger("setup_queries");
	},
	validate(frm) {
		frm.trigger("validate_user_on_participants");
	},

	survey_template(frm) {
		frm.trigger("fetch_questions");
	},

	fetch_questions(frm) {
		const { doc } = frm;

		if (!doc.survey_template) {
			return "No survey template selected... skipping";
		}

		frm.call("get_questions_from_template")
			.then(response => {
				const { message: questions_template } = response;

				if (doc.survey_template) {
					frm.set_value("questions", questions_template);
				}
			});
	},

	get_participants(frm) { // button handler
		const { doc } = frm;

		frm.call("get_employees")
			.then(response => {
				const { message: participants } = response;
				doc.employees = new Array();

				if (participants == null) {
					frm.refresh_field('employees');
					frappe.show_alert({
						message: __("No participants found for these filters"),
						indicator: "warning",
					});
				} else {
					for (const participant of participants) {
						frm.add_child("employees", participant);
					}
					frm.refresh_field('employees');
				}
			});
	},

	validate_user_on_participants(frm) {
		const { doc } = frm;

		const msg_template = "User not specified for employee {0} at row #{1}";
		for (const employee of doc.employees) {
			const { employee_name, idx } = employee;

			const errmsg = __(msg_template, [employee_name, idx]);
			if (!employee.user) {
				frappe.msgprint(errmsg);
				validated = false;
			}
		}
	},

	setup_queries(frm) {
		// const { doc } = frm;

		frappe.run_serially([
			() => frm.trigger("set_client_query"),
			() => frm.trigger("set_vertical_query"),
			() => frm.trigger("set_campaign_query"),
			() => frm.trigger("set_training_event_query"),
		]);
	},

	set_client_query(frm) {
		const { doc } = frm;

		frm.set_query("client", () => {
			const filters = {
				"is_client": true,
			};

			return { filters };
		});
	},
	set_vertical_query(frm) {
		const { doc } = frm;

		frm.set_query("vertical", () => {
			const filters = {
				"parent_operations_client": doc.client
			};

			return { filters };
		});
	},
	set_campaign_query(frm) {
		const { doc } = frm;

		frm.set_query("campaign", () => {
			const filters = {
				"parent_operations_client": doc.vertical
			};

			return { filters };
		});
	},
	set_training_event_query(frm) {
		const { doc } = frm;

		frm.set_query("training_event", () => {
			const filters = {
				"docstatus": 1,
			};

			return { filters };
		});
	},

});
