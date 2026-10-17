import json
import os

DATA_FILE = "learn2earn_data.json"

# Persistence
def save_data():
    data = {
        "resources": resources,
        "fellows": fellows,
        "borrow_records": borrow_records,
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {DATA_FILE}.")


def load_data():
    global resources, fellows, borrow_records
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: could not load {DATA_FILE}: {exc}")
        return
    resources = data.get("resources", resources)
    fellows = data.get("fellows", fellows)
    borrow_records = data.get("borrow_records", borrow_records)
    print(f"Data loaded from {DATA_FILE}.")

# Default (starting) data
DEFAULT_RESOURCES = [
    {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
    {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
    {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
]
DEFAULT_FELLOWS = {"F001": "Ada", "F002": "John", "F003": "Grace"}

resources = [dict(r) for r in DEFAULT_RESOURCES]  # deep-ish copy
fellows = dict(DEFAULT_FELLOWS)
borrow_records = []


# Helpers
def find_resource(resource_id):
    for r in resources:
        if r["id"] == resource_id:
            return r
    return None


def find_fellow(fellow_id):
    return fellows.get(fellow_id)


def get_borrowed(fellow_id, resource_id):
    """How many of this resource does this fellow currently have on loan?"""
    total = 0
    for rec in borrow_records:
        if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource_id:
            total += rec["quantity"]
    return total


def add_fellow(fellow_id, name):
    if fellow_id in fellows:
        print(f"Error: Fellow ID {fellow_id} already exists.")
        return False
    if not name.strip():
        print("Error: Fellow name cannot be empty.")
        return False
    fellows[fellow_id] = name.strip()
    print(f"Added fellow {name} ({fellow_id}).")
    return True


def list_fellows():
    if not fellows:
        print("No fellows registered.")
        return
    print(f"{'ID':<6}{'Name':<20}")
    print("-" * 26)
    for fid, name in fellows.items():
        print(f"{fid:<6}{name:<20}")


# Adding and listing resource
def add_resource(resource_id, name, category, total):
    if find_resource(resource_id) is not None:
        print(f"Error: Resource ID {resource_id} already exists.")
        return False
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        print("Error: Total units must be a positive integer.")
        return False
    if not name.strip():
        print("Error: Resource name cannot be empty.")
        return False
    resources.append({
        "id": resource_id,
        "name": name.strip(),
        "category": category.strip() or "Uncategorized",
        "total": total,
        "available": total,
    })
    print(f"Added {name} ({resource_id}) with {total} units.")
    return True


def list_resources():
    if not resources:
        print("No resources in inventory.")
        return
    print(f"{'ID':<6}{'Name':<15}{'Category':<15}{'Total':<8}{'Available':<10}")
    print("-" * 54)
    for r in resources:
        print(
            f"{r['id']:<6}{r['name']:<15}{r['category']:<15}"
            f"{r['total']:<8}{r['available']:<10}"
        )


# Borrowing
def borrow_resource(fellow_id, resource_id, quantity):
    # 1. Validate fellow
    if find_fellow(fellow_id) is None:
        print(f"Error: Fellow ID {fellow_id} not found.")
        return False

    # 2. Validate resource
    resource = find_resource(resource_id)
    if resource is None:
        print(f"Error: Resource ID {resource_id} not found.")
        return False

    # 3. Validate quantity (positive int; reject bools)
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        print("Error: Quantity must be a positive integer.")
        return False

    # 4. Validate stock
    if quantity > resource["available"]:
        print(f"Error: Only {resource['available']} unit(s) of "
              f"{resource['name']} available.")
        return False

    # All checks passed — mutate state
    resource["available"] -= quantity
    borrow_records.append({
        "fellow_id": fellow_id,
        "resource_id": resource_id,
        "quantity": quantity,
    })
    print(f"{find_fellow(fellow_id)} borrowed {quantity} x {resource['name']}.")
    print(f"Available {resource['name']} units = {resource['available']}.")
    return True


# Returning
def return_resource(fellow_id, resource_id, quantity):
    if find_fellow(fellow_id) is None:
        print(f"Error: Fellow ID {fellow_id} not found.")
        return False

    resource = find_resource(resource_id)
    if resource is None:
        print(f"Error: Resource ID {resource_id} not found.")
        return False

    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        print("Error: Quantity must be a positive integer.")
        return False

    on_loan = get_borrowed(fellow_id, resource_id)     # FIXED: correct helper name
    if quantity > on_loan:
        print(f"Error: {find_fellow(fellow_id)} only has "
              f"{on_loan} x {resource['name']} on loan.")
        return False

    # Reduce from borrow_records (may span multiple records)
    remaining = quantity
    for rec in borrow_records:
        if remaining == 0:
            break
        if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource_id:
            take = min(rec["quantity"], remaining)
            rec["quantity"] -= take
            remaining -= take

    # Remove zero-quantity records 
    borrow_records[:] = [rec for rec in borrow_records if rec["quantity"] > 0]

    resource["available"] += quantity
    print(f"{find_fellow(fellow_id)} returned {quantity} x {resource['name']}.")
    print(f"Available {resource['name']} units = {resource['available']}.")
    return True


# Search and filter
def search_by_name(query):
    query = query.strip().lower()
    if not query:
        print("Search query cannot be empty.")
        return []
    results = [r for r in resources if query in r["name"].lower()]
    if not results:
        print(f"No resources match '{query}'.")
    else:
        print(f"Found {len(results)} match(es):")
        for r in results:
            print(f"  {r['id']} - {r['name']} ({r['category']}) "
                  f"available: {r['available']}/{r['total']}")
    return results


def filter_by_category(category):
    category = category.strip().lower()
    if not category:
        print("Category cannot be empty.")
        return []
    results = [r for r in resources if r["category"].lower() == category]
    if not results:
        print(f"No resources in category '{category}'.")
    else:
        print(f"Found {len(results)} resource(s) in '{category}':")
        for r in results:
            print(f"  {r['id']} - {r['name']} "
                  f"available: {r['available']}/{r['total']}")
    return results


# Reporting
def generate_report():
    total_units = sum(r["total"] for r in resources)
    total_available = sum(r["available"] for r in resources)
    total_borrowed = total_units - total_available

    print("\n===== INVENTORY REPORT =====")
    print(f"Total units       : {total_units}")
    print(f"Available units   : {total_available}")
    print(f"Borrowed units    : {total_borrowed}")

    # Low stock (< 3 available)
    low_stock = [r for r in resources if r["available"] < 3]
    if low_stock:
        print("\nLow stock (< 3 available):")
        for r in low_stock:
            print(f"  {r['name']}: {r['available']} available")
    else:
        print("\nNo low-stock resources.")

    if not borrow_records:
        print("\nNo borrowing activity yet.")
        return

    # Sum currently-borrowed quantity per resource
    borrowed_per_resource = {}
    for rec in borrow_records:
        rid = rec["resource_id"]
        borrowed_per_resource[rid] = borrowed_per_resource.get(rid, 0) + rec["quantity"]

    max_borrowed = max(borrowed_per_resource.values())
    leaders = [rid for rid, qty in borrowed_per_resource.items() if qty == max_borrowed]

    print("\nMost borrowed resource(s) currently out on loan:")
    for rid in leaders:
        r = find_resource(rid)
        if r is not None:
            print(f"  {r['name']}: {max_borrowed} unit(s)")


# Menu
def print_menu():
    print("\n===== Learn2Earn Menu =====")
    print("1. List resources")
    print("2. Add resource")
    print("3. Borrow resource")
    print("4. Return resource")
    print("5. Search by name")
    print("6. Filter by category")
    print("7. Generate report")
    print("8. Run demonstration (steps 1-7)")
    print("9. List fellows")
    print("10. Add fellow")
    print("0. Exit")


def get_positive_int(prompt):
    """Keep asking until the user enters a positive integer."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"'{raw}' is not a valid integer. Try again.")
            continue
        if value <= 0:
            print("Please enter a positive integer.")
            continue
        return value


def main():
    load_data() 

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_resources()
        elif choice == "2":
            rid = input("Resource ID: ").strip()
            name = input("Name: ").strip()
            category = input("Category: ").strip()
            total = get_positive_int("Total units: ")
            add_resource(rid, name, category, total)
        elif choice == "3":
            fid = input("Fellow ID: ").strip()
            rid = input("Resource ID: ").strip()
            qty = get_positive_int("Quantity: ")
            borrow_resource(fid, rid, qty)
        elif choice == "4":
            fid = input("Fellow ID: ").strip()
            rid = input("Resource ID: ").strip()
            qty = get_positive_int("Quantity: ")
            return_resource(fid, rid, qty)
        elif choice == "5":
            q = input("Search name: ").strip()
            search_by_name(q)
        elif choice == "6":
            c = input("Category: ").strip()
            filter_by_category(c)
        elif choice == "7":
            generate_report()
        elif choice == "8":
            run_demonstration()
        elif choice == "9":
            list_fellows()
        elif choice == "10":
            fid = input("Fellow ID: ").strip()
            name = input("Fellow name: ").strip()
            add_fellow(fid, name)
        elif choice == "0":
            save_data()  # FIXED: save on exit
            print("Goodbye!")
            break
        else:
            print(f"Unknown option '{choice}'. Please try again.")


# Demonstration (must be defined before main() is invoked)
def run_demonstration():
    print("\n******* DEMONSTRATION *********")
    print("(Demo runs on current in-memory state.)")

    print("\n--- Step 1: F001 borrows 2 laptops ---")
    borrow_resource("F001", "R001", 2)

    print("\n--- Step 2: F002 borrows 3 keyboards ---")
    borrow_resource("F002", "R002", 3)

    print("\n--- Step 3: F001 returns 1 laptop ---")
    return_resource("F001", "R001", 1)

    print("\n--- Step 4: F003 requests 4 headsets (should be rejected) ---")
    borrow_resource("F003", "R003", 4)

    print("\n--- Step 5: F002 tries to return 4 keyboards (should be rejected) ---")
    return_resource("F002", "R002", 4)

    print("\n--- Step 6: Search for 'LAPtop' ---")
    search_by_name("LAPtop")

    print("\n--- Step 7: Generate report ---")
    generate_report()

    print("\n--- Extra: invalid input tests ---")
    borrow_resource("F001", "R001", -3)     
    borrow_resource("F001", "R001", "two")  
    borrow_resource("F001", "R001", True)   

# Entry point
if __name__ == "__main__":
    main()