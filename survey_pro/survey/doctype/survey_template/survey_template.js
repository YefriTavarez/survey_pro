// Copyright (c) 2022, Yefri Tavarez and contributors
// For license information, please see license.txt

frappe.ui.form.on("Survey Template", {
	refresh(frm) {
		frappe.run_serially([
			_ => frm.trigger("setup_table_buttons"),
		]);
	},
	setup_table_buttons(frm) {
		const { fields_dict } = frm;

		const { grid } = fields_dict.questions;
		const add_existing = grid.add_custom_button("Add Existing", _ => {
			return new SurveyQuestionDialog({ frm, existing: true });
		});
		add_existing
			.removeClass("btn-default")
			.addClass("btn-secondary")
			.css("margin", "3px")
			;

		const create_new = grid.add_custom_button("Create New", _ => {
			return new SurveyQuestionDialog({ frm, existing: false });
		});

		create_new
			.removeClass("btn-default")
			.addClass("btn-primary")
			.css("margin", "3px")
			;

		// (add_existing || create_new)
		// 	.parent()
		// 	.css({
		// 		"padding-top": "10px",
		// 	});
	},
});

class SurveyQuestionDialog extends frappe.ui.Dialog {
	constructor({ frm, existing = false }) {
		super({
			title: __("Add Question"),
			fields: [
				{
					label: __("Question ID"),
					fieldname: "question_id",
					fieldtype: "Link",
					options: "Survey Question",
					depends_on: `eval:${existing}`,
					reqd: existing,
					change() {
						const { value, doc } = this;
						cur_dialog.fetch_question_details(value, doc);
					}
				},
				{
					label: __("Question"),
					fieldname: "question",
					fieldtype: existing ? "Read Only" : "Data",
					reqd: !existing,
				},
				{
					label: __("Question Type"),
					fieldname: "question_type",
					fieldtype: "Select",
					options: [
						"Yes or No",
						"Open Question",
						"Closed Question",
					],
					reqd: 1,
				},
				{
					label: __("Is Multi-Select?"),
					fieldname: "is_multiselect",
					fieldtype: "Check",
				},
				{
					label: __("Options"),
					fieldname: "options",
					fieldtype: "Table",
					depends_on: `eval:doc.question_type==='Closed Question'`,
					cannot_add_rows: false,
					in_place_edit: false,
					reqd_depends_on: `eval:doc.question_type==='Closed Question'`,
					checkboxColumn: false,
					fields: [
						{
							label: __("Option"),
							fieldname: "option",
							fieldtype: "Data",
							reqd: 1,
							in_list_view: 1,
						},
					],
					get_data() {
						return [];
					},
					// add_row_label: __("Add Option"),
				},
			],
			primary_action_label: __("Add"),
			primary_action: _ => {
				this.add_question(frm);

				this.hide();
			},
		});

		this.frm = frm;
		this.existing = existing;

		this.show();
	}

	fetch_question_details(question, doc) {
		const doctype = "Survey Question";
		const name = question;

		frappe.db.get_doc(doctype, name)
			.then(doc => {
				const { fields_dict } = cur_dialog;

				const {
					question,
					question_type,
					is_multiselect,
					options,
				} = fields_dict;

				question.set_value(doc.question);
				question_type.set_value(doc.question_type);
				is_multiselect.set_value(doc.is_multiselect);

				console.log({ options, doc });
			});
	}

	add_question(frm) {
		const {
			question_id,
			question,
			question_type,
			is_multiselect,
			options
		} = this.get_values();

		frm.add_child("questions", {
			question_id,
			question,
			question_type,
		});

		console.log({
			question_id,
			question,
			question_type,
			is_multiselect,
			options
		})

		frm.refresh_field("questions");
	}
}