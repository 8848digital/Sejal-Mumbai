import frappe
from frappe import _


# Post Client API
@frappe.whitelist(allow_guest=True)
def create_stock_entry(kwargs):
    try:
        posting_date = kwargs.get("posting_date")
        custom_locations = kwargs.get("custom_locations")
        stock_entry_type = kwargs.get("stock_entry_type")
        items = kwargs.get("items")

        client = frappe.new_doc("Stock Entry")
        client.posting_date = posting_date
        client.custom_locations = custom_locations
        client.stock_entry_type = stock_entry_type

        for item in items:
            s_warehouse = item.get("s_warehouse")
            t_warehouse = item.get("t_warehouse")
            item_code = item.get("item_code")
            qty = item.get("qty")
            allow_zero_valuation_rate = item.get("allow_zero_valuation_rate")

            client.append("items", {
                "s_warehouse": s_warehouse,
                "t_warehouse": t_warehouse,
                "item_code": item_code,
                "qty": qty,
                "allow_zero_valuation_rate":allow_zero_valuation_rate
            })

        client.insert(ignore_permissions=True)

        response_data = {
            "status": "success",
            "message": "Stock Entry created successfully.",
            "client_id": client.name,
        }
        return {"status": "success", "data": response_data}
    except Exception as e:
        frappe.logger("error").exception(e)
        return error_response(str(e))

def error_response(message):
    return {"status": "failed", "message": message}



@frappe.whitelist(allow_guest=True)
def get_stock_entry(kwargs):
    try:
        data = frappe.db.sql(
            f"""
            SELECT
                se.name,
                se.posting_date,
                se.custom_locations,
                se.docstatus,
                sed.s_warehouse,
                sed.t_warehouse,
                sed.item_code
            FROM
                `tabStock Entry` AS se
                LEFT JOIN `tabStock Entry Detail` AS sed ON sed.parent = se.name
            WHERE
                (se.docstatus = 0 or se.docstatus = 1 or se.docstatus = 2)
                AND se.name NOT IN (SELECT amended_from FROM `tabStock Entry` WHERE amended_from IS NOT NULL)
            ORDER BY
                se.modified desc
            """,
            as_dict=True,
        )
        return build_response("success", data=data)
    except Exception as e:
        frappe.log_error(title=_("API Error"), message=str(e))
        return build_response("error", message=_("An error occurred while fetching data."))

def build_response(status, data=None, message=None):
    response = {"status": status}

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    return response



@frappe.whitelist(allow_guest=True)
def name_specific_stock_entry(kwargs):
    name = kwargs.get("name")
    conditions = get_conditions(name)
    try:
        data = frappe.db.sql(
            f"""
            SELECT
                se.name,
                se.posting_date,
                se.custom_locations,
                se.docstatus,
                sed.s_warehouse,
                sed.t_warehouse,
                sed.item_code,
                sed.qty
            FROM
                `tabStock Entry` AS se
                LEFT JOIN `tabStock Entry Detail` AS sed ON sed.parent = se.name
            WHERE
                se.docstatus IN (0, 1, 2)
                AND se.name NOT IN (SELECT amended_from FROM `tabStock Entry` WHERE amended_from IS NOT NULL)
                {conditions}
            ORDER BY
                se.modified DESC
            """,
            as_dict=True,
        )

        
        items = [{"s_warehouse": item["s_warehouse"], "t_warehouse": item["t_warehouse"], "item_code": item["item_code"]} for item in data]

        return build_response("success", data=data, items=items, exec_time="0.0008 seconds")
    except Exception as e:
        frappe.log_error(title=_("API Error"), message=str(e))
        return build_response("error", message=_("An error occurred while fetching data."))

def get_conditions(name=None):
    conditions = ""
    if name:
        conditions += f' AND se.name = "{name}"'

    return conditions

def build_response(status, data=None, items=None, message=None, exec_time=None):
    response = {"status": status}

    if data is not None:
        # Modify data to exclude 's_warehouse', 't_warehouse', and 'item_code'
        modified_data = [{"name": item["name"], "posting_date": item["posting_date"], "custom_locations": item["custom_locations"], "docstatus": item["docstatus"]} for item in data]
        response["data"] = modified_data

    if items is not None:
        response["items"] = items

    if message is not None:
        response["message"] = message

    if exec_time is not None:
        response["exec_time"] = exec_time

    return response
