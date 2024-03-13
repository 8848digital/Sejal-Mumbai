// Copyright (c) 2024, shyam and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Entry"] = {
	"filters": [
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},

	]
};
