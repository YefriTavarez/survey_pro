// Copyright (c) 2023, frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Survey Log', {
	refresh(frm) {
		frm.trigger("add_custom_buttons");
	},
	add_custom_buttons(frm) {
		frappe.run_serially([
			_ => frm.trigger("add_import_button"),
		]);
	},
	add_import_button(frm) {
		const { doc } = frm;
		const label = __("Import Survey Log");
		const action = () => {
			frm.trigger("import_survey_log");
		};

		if (doc.status !== "Imported") {
			frm.add_custom_button(label, action);
		}
	},
	import_survey_log(frm) {
		frm.call("process_log")
			.then(_ => {
				frappe.show_alert({
					message: __("Imported Successfully"),
					indicator: "green"
				});
				frm.reload_doc();
			}, _ => {
				frappe.show_alert({
					message: __("Something went wrong"),
					indicator: "red"
				});
				frm.reload_doc();
			})
	}
});
