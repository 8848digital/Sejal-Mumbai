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
            s_warehouse = item.get("source_warehouse")
            t_warehouse = item.get("target_warehouse")
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
def put_stock_entry(kwargs):
    try:
        name = kwargs.get("name")
        posting_date = kwargs.get("posting_date")
        custom_locations = kwargs.get("custom_locations")
        stock_entry_type = kwargs.get("stock_entry_type")
        items = kwargs.get("items")
       
        # Get the Stock Entry document
        client = frappe.get_doc("Stock Entry", name)
        client.posting_date = posting_date
        client.custom_locations = custom_locations
        client.stock_entry_type = stock_entry_type

        # Clear existing items before appending new ones
        client.items = []
        
        # Append new items
        for item in items:
            s_warehouse = item.get("source_warehouse")
            t_warehouse = item.get("target_warehouse")
            item_code = item.get("item_code")
            qty = item.get("qty")
            allow_zero_valuation_rate = item.get("allow_zero_valuation_rate")

            client.append("items", {
                "s_warehouse": s_warehouse,
                "t_warehouse": t_warehouse,
                "item_code": item_code,
                "qty": qty,
                "allow_zero_valuation_rate": allow_zero_valuation_rate
            })

        # Save the Stock Entry document after all items are appended
        client.save()
        response_data = {
            "status": "success",
            "message": "Stock Entry updated successfully.",
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
                se.docstatus
            FROM
                `tabStock Entry` AS se
            WHERE
                (se.docstatus = 0 or se.docstatus = 1 or se.docstatus = 2)
                AND se.name NOT IN (SELECT amended_from FROM `tabStock Entry` WHERE amended_from IS NOT NULL)
            ORDER BY
                se.modified desc
            """,
            as_dict=True,
        )
        response = {
            "status": "success",
            "data": data
        }
    except Exception as e:
        response = {
            "status": "error",
            "message": str(e)
        }
        
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
                sed.idx,
                sed.s_warehouse AS source_warehouse, 
                sed.t_warehouse AS target_warehouse,
                sed.item_code,
                sed.qty,
                sed.allow_zero_valuation_rate
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

        items = [{"source_warehouse": item["source_warehouse"], "target_warehouse": item["target_warehouse"], "item_code": item["item_code"], "qty": item["qty"], "allow_zero_valuation_rate": item["allow_zero_valuation_rate"]} for item in data]

        return build_response("success", data=data, items=items, exec_time="0.0008 seconds")
    except Exception as e:
        frappe.log_error(title=_("API Error"), message=str(e))
        return build_response("error", exec_time="0.0038 seconds")

def get_conditions(name=None):
    conditions = ""
    if name:
        conditions += f' AND se.name = "{name}"'

    return conditions

def build_response(status, data=None, items=None, message=None, exec_time=None):
    response = {"status": status}

    if data is not None:
        modified_data = []
        for item in data:
            modified_item = {
                "name": item["name"],
                "posting_date": item["posting_date"],
                "custom_locations": item["custom_locations"],
                "docstatus": item["docstatus"],
                "items": [{"idx": item["idx"], "source_warehouse": item["source_warehouse"], "target_warehouse": item["target_warehouse"], "item_code": item["item_code"], "qty": item["qty"], "allow_zero_valuation_rate": item["allow_zero_valuation_rate"]}]
            }
            modified_data.append(modified_item)
        response["data"] = modified_data

    if exec_time is not None:
        response["exec_time"] = exec_time

    if message is not None:
        response["error"] = message

    return response



@frappe.whitelist(allow_guest=True)
def list_warehouse(kwargs):
    try:
        data = frappe.db.sql(
            f"""
            SELECT
            w.name     
            FROM
                `tabWarehouse` AS w
            ORDER BY
                w.modified desc
            """,
            as_dict=True,
        )
        response = {
            "status": "success",
            "data": data
        }
    except Exception as e:
        response = {
            "status": "error",
            "message": str(e)
        }
        
    return response
