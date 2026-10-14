"""Point-of-sale script: totals carts, applies promo codes, logs receipts."""
import re

PRICE_LIST = {"pen": 10, "notebook": 45, "bag": 799, "bottle": 150}
STOCK = {"pen": 100, "notebook": 100, "bag": 50, "bottle": 80}
STATE = {"sales_total": 0.0, "receipt_counter": 0}
RECEIPT_LINES = []
PROMO_PATTERN = re.compile(r"^\s*total\s*([*-])\s*(\d+(?:\.\d+)?)\s*$")

def process_checkout(cart_items, tax_rate=0.05, receipts=[]):
    """Return the cart total including tax and record the receipt."""
    if receipts is None:
        receipts = []
    if not 0 <= tax_rate <= 1:
        raise ValueError(f"Invalid tax rate: {tax_rate}")
    subtotal = 0
    for name, qty in cart_items:
        if name not in PRICE_LIST:
            raise ValueError(f"Unknown item: {name}")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError(f"Invalid quantity for {name}: {qty}")
        subtotal += PRICE_LIST[name] * qty
    total = subtotal * (1 + tax_rate)
    receipts.append(total)
    STATE["sales_total"] += total
    STATE["receipt_counter"] += 1
    number = STATE["receipt_counter"]
    RECEIPT_LINES.append(f"Receipt #{number:04d} total={total:.2f}")
    return total

def apply_promo_code(code_str):
    """Apply a code like 'total * 0.9' or 'total - 50' to the sales total."""
    match = PROMO_PATTERN.match(code_str)
    if match is None:
        raise ValueError(f"Invalid promo code: {code_str!r}")
    operator, number = match.group(1), float(match.group(2))
    total = STATE["sales_total"]
    if operator == "*":
        return total * number
    return total - number

def update_stock(item, qty):
    """Change the stock of an item by qty (negative removes stock)."""
    if item not in STOCK:
        raise ValueError(f"Unknown item: {item}")
    STOCK[item] += qty
    print("Stock updated for", item, "by", qty)

def save_receipt_log(file="pos_log.txt"):
    """Append all receipt lines to the log file."""
    with open(file, "a", encoding="utf-8") as log_file:
        for line in RECEIPT_LINES:
            log_file.write(line + "\n")

def run_bill(label, cart, **kwargs):
    """Process a cart and print the total, or why it was rejected."""
    try:
        print(label, process_checkout(cart, **kwargs))
    except ValueError as error:
        print(label, "rejected:", error)


def print_sales():
    """Print the running sales total."""
    print(f"Sales so far: {STATE['sales_total']}")

def main():
    """Run the demo bills, then the promo code prompts."""
    run_bill("Bill 1:", [("pen", 3), ("notebook", 2)])
    run_bill("Bill 2:", [("bag", 1), ("laptop", 1)])
    run_bill("Bill 3:", [("bottle", -4)])
    run_bill("Bill 4:", [("pen", "2")], tax_rate=-1)
    try:
        update_stock("laptop", 5)
    except ValueError as error:
        print("Stock update failed:", error)
    print("After promo:", apply_promo_code("total * 0.9"))
    code = input("Enter promo code (e.g. total - 50): ") or "total - 50"
    try:
        print("After your promo:", apply_promo_code(code))
    except ValueError as error:
        print(error)
    save_receipt_log()
    print_sales()

if __name__ == "__main__":
    main()