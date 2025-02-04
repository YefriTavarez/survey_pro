frappe.ready(function () {
    frappe.provide("survey_pro.survey");
    frappe.provide("survey_pro.survey.doc");

    { // setup doc
        const { doc } = survey_pro.survey;
        jQuery("[data-question]").each(function () {
            const jTarget = jQuery(this);
            const { question, questionContent, questionType } = jTarget.data();

            doc[question] = {
                question_content: questionContent,
                question_type: questionType,
                user_response: null,
            };
        });

        survey_pro.survey["survey_id"] = "{{ doc.name }}";
        // doc["survey_id"] = survey_pro.survey["survey_id"];
    };

    let form = document.getElementById("survey-form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const { doc } = survey_pro.survey;
        // const data = new FormData(form);

        fetch("/api/method/survey_pro.survey.save_user_response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": frappe.csrf_token,
            },
            body: JSON.stringify({
                user_response: doc,
                survey_id: survey_pro.survey["survey_id"]
            }),
        })
            .then(response => response.json())
            .then(response => {
                const { message: text } = response;

                if (text) {
                    const [title, message] = text.split(":");
                    const dialog = frappe.msgprint({ message, title });

                    dialog.onhide = () => {
                        window.location.reload();
                    };

                    return message;
                }

                const { _server_messages: errors } = response;
                if (errors) {
                    const message = JSON.parse(errors);
                    frappe.throw(message);
                }
            });
    });

    survey_pro.survey.textarea = function (event) {
        const { target } = event;
        const { value } = target;

        const { doc } = survey_pro.survey;

        const question_id = jQuery(target).attr("data-question");
        doc[question_id]["user_response"] = value;
    }

    survey_pro.survey.yesorno = function (event) {
        const { target } = event;
        const jTarget = jQuery(target);

        const { value } = target;

        const { doc } = survey_pro.survey;
        const question_id = jTarget.attr("data-question");

        let user_response = "";
        if (value === "on") {
            user_response = jTarget.attr("data-value");
        }

        doc[question_id]["user_response"] = user_response;
    }

    survey_pro.survey.checkbox = function (event) {
        const { target: element } = event;
        const target = jQuery(element);
        const parent = target.parents("div.form-check-wrapper");

        // const value = target.val();
        const type = target.prop("type");

        const { doc } = survey_pro.survey;
        const question_id = target.attr("data-question");
        if (type === "checkbox") {
            const checked_values = parent.find("input:checked")
                .map(function () {
                    return jQuery(this).attr("data-value");
                }).toArray();

            // let's separate by comma all checked values
            doc[question_id]["user_response"] = checked_values.join(",");
        } else if (type === "radio") {
            const checked = parent
                .find("input:checked")
                .get(0);

            // default value
            doc[question_id]["user_response"] = null;
            if (checked) {
                const value = jQuery(checked).attr("data-value");

                // let's separate by comma all checked values
                doc[question_id]["user_response"] = value;
            }
        } else {
            return;
        }
    }
});
