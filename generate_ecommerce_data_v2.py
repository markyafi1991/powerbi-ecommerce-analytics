"""
E-Commerce Sample Data Generator v2
=====================================
Fixes applied from Cursor data quality review:

  Fix 1 — fact_returns DateIDs outside dim_date
           ReturnDate is now capped at END_DATE so all DateIDs
           exist in dim_date. No broken relationships.

  Fix 2 — FirstOrderDate vs order dates mismatch
           FirstOrderDate is now DERIVED from fact_orders
           (min OrderDate per customer) after orders are generated,
           so customer dates always agree with facts.

  Fix 3 — AOV tuned to $130–160 range (closer to $150 benchmark)
           List prices and basket sizes adjusted downward.

  Fix 4 — DiscountPct now reflects true order-level discount
           (weighted average across line items, not last-line value).

Output dir defaults to the folder this script lives in.
Change OUTPUT_DIR below if you want files elsewhere.

Tables produced:
  dim_date.csv       dim_channel.csv    dim_customer.csv
  dim_product.csv    fact_orders.csv    fact_returns.csv
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

# ── Config ────────────────────────────────────────────────────────────────────
SEED       = 42
START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2024, 12, 31)

N_CUSTOMERS = 800
N_PRODUCTS  = 120
N_ORDERS    = 6000

# Files land next to the script by default
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecommerce_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Reproducibility ───────────────────────────────────────────────────────────
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_CA")
Faker.seed(SEED)


# ══════════════════════════════════════════════════════════════════════════════
# 1. DIM DATE
# ══════════════════════════════════════════════════════════════════════════════
def generate_dim_date(start: datetime, end: datetime) -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"Date": dates})

    df["DateID"]       = df["Date"].dt.strftime("%Y%m%d").astype(int)
    df["Year"]         = df["Date"].dt.year
    df["Quarter"]      = df["Date"].dt.quarter
    df["QuarterLabel"] = "Q" + df["Quarter"].astype(str) + " " + df["Year"].astype(str)
    df["Month"]        = df["Date"].dt.month
    df["MonthName"]    = df["Date"].dt.strftime("%B")
    df["MonthLabel"]   = df["Date"].dt.strftime("%b %Y")
    df["Week"]         = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeek"]    = df["Date"].dt.day_name()
    df["IsWeekend"]    = df["Date"].dt.dayofweek >= 5

    seasonal_ranges = [
        ("11-25", "12-31"),
        ("01-01", "01-15"),
        ("02-10", "02-14"),
        ("05-08", "05-12"),
        ("07-01", "07-07"),
    ]
    df["IsSeasonal"] = False
    for s, e in seasonal_ranges:
        mask = (df["Date"].dt.strftime("%m-%d") >= s) & \
               (df["Date"].dt.strftime("%m-%d") <= e)
        df.loc[mask, "IsSeasonal"] = True

    df["Date"] = df["Date"].dt.date
    return df[["DateID","Date","Year","Quarter","QuarterLabel",
               "Month","MonthName","MonthLabel","Week","DayOfWeek",
               "IsWeekend","IsSeasonal"]]


# ══════════════════════════════════════════════════════════════════════════════
# 2. DIM CHANNEL
# ══════════════════════════════════════════════════════════════════════════════
def generate_dim_channel() -> pd.DataFrame:
    rows = [
        (1, "Organic Search", "Organic",  0.00),
        (2, "Paid Search",    "Paid",     18.50),
        (3, "Email",          "Owned",     4.20),
        (4, "Social Organic", "Organic",   0.00),
        (5, "Paid Social",    "Paid",     22.00),
        (6, "Direct",         "Direct",    0.00),
        (7, "Referral",       "Referral",  6.00),
        (8, "Affiliate",      "Paid",     12.00),
    ]
    return pd.DataFrame(rows,
        columns=["ChannelID","ChannelName","ChannelType","AvgCAC_USD"])


# ══════════════════════════════════════════════════════════════════════════════
# 3. DIM PRODUCT  (Fix 3: prices tuned to hit $130–160 AOV)
# ══════════════════════════════════════════════════════════════════════════════
def generate_dim_product(n: int) -> pd.DataFrame:
    catalog = {
        "Apparel": {
            "subcats": ["T-Shirts","Hoodies","Jackets","Pants","Activewear"],
            "price_range": (18, 95),          # was (24, 149)
            "margin_range": (0.45, 0.72),
        },
        "Footwear": {
            "subcats": ["Sneakers","Boots","Sandals","Athletic"],
            "price_range": (35, 130),         # was (49, 220)
            "margin_range": (0.40, 0.65),
        },
        "Accessories": {
            "subcats": ["Bags","Hats","Belts","Scarves","Watches"],
            "price_range": (14, 110),         # was (18, 180)
            "margin_range": (0.50, 0.75),
        },
        "Home & Living": {
            "subcats": ["Bedding","Kitchen","Decor","Storage"],
            "price_range": (16, 90),          # was (22, 160)
            "margin_range": (0.38, 0.62),
        },
        "Beauty & Wellness": {
            "subcats": ["Skincare","Haircare","Supplements","Fitness"],
            "price_range": (12, 65),          # was (14, 95)
            "margin_range": (0.55, 0.80),
        },
    }

    categories  = list(catalog.keys())
    cat_weights = [0.30, 0.20, 0.20, 0.15, 0.15]
    adjectives  = ["Premium","Classic","Essential","Pro","Signature","Urban",
                   "Natural","Active","Modern","Heritage"]
    nouns       = ["Series","Edition","Collection","Pack","Bundle","Set","Kit"]

    records = []
    for i in range(1, n + 1):
        cat    = random.choices(categories, cat_weights)[0]
        info   = catalog[cat]
        subcat = random.choice(info["subcats"])
        price  = round(random.uniform(*info["price_range"]), 2)
        margin = round(random.uniform(*info["margin_range"]), 4)
        cogs   = round(price * (1 - margin), 2)
        name   = f"{random.choice(adjectives)} {subcat} {random.choice(nouns)} {i}"

        records.append({
            "ProductID":      i,
            "ProductName":    name,
            "Category":       cat,
            "SubCategory":    subcat,
            "ListPrice_USD":  price,
            "COGS_USD":       cogs,
            "GrossMarginPct": round(margin * 100, 2),
            "Supplier":       fake.company(),
            "IsActive":       random.choices([True, False], [0.88, 0.12])[0],
        })

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════════
# 4. FACT ORDERS  (Fix 4: order-level DiscountPct = weighted avg across lines)
# ══════════════════════════════════════════════════════════════════════════════
def seasonal_multiplier(d: datetime) -> float:
    md = d.strftime("%m-%d")
    if "11-25" <= md <= "12-31": return 2.8
    if "01-01" <= md <= "01-07": return 1.6
    if "02-10" <= md <= "02-14": return 1.4
    if "05-08" <= md <= "05-12": return 1.3
    if "07-01" <= md <= "07-05": return 1.2
    return 1.0


def generate_fact_orders(n_orders: int,
                          n_customers: int,
                          products: pd.DataFrame,
                          channels: pd.DataFrame) -> pd.DataFrame:

    date_list = pd.date_range(START_DATE, END_DATE, freq="D").tolist()

    # Weight by seasonal peaks + upward trend
    weights = []
    for idx, d in enumerate(date_list):
        trend = 1 + (idx / len(date_list)) * 0.6
        weights.append(seasonal_multiplier(d) * trend)
    total_w = sum(weights)
    weights = [w / total_w for w in weights]

    channel_ids = channels["ChannelID"].tolist()
    ch_weights  = [0.25, 0.20, 0.15, 0.10, 0.12, 0.08, 0.05, 0.05]

    discount_options = [0, 0.05, 0.10, 0.15, 0.20]
    discount_weights = [0.55, 0.15, 0.15, 0.10, 0.05]

    records = []
    for order_id in range(1, n_orders + 1):
        order_date  = random.choices(date_list, weights)[0]
        customer_id = random.randint(1, n_customers)
        channel_id  = random.choices(channel_ids, ch_weights)[0]

        # Basket: 1–4 distinct products
        n_items     = random.choices([1,2,3,4], [0.50,0.28,0.14,0.08])[0]
        product_ids = random.sample(range(1, len(products)+1),
                                    min(n_items, len(products)))

        order_revenue    = 0.0
        order_cogs       = 0.0
        order_qty        = 0
        weighted_disc_num = 0.0   # for Fix 4: weighted avg discount

        for pid in product_ids:
            prod     = products.iloc[pid - 1]
            qty      = random.choices([1,2,3], [0.65,0.25,0.10])[0]
            price    = prod["ListPrice_USD"]
            cogs     = prod["COGS_USD"]
            disc_pct = random.choices(discount_options, discount_weights)[0]

            net_price = round(price * (1 - disc_pct), 2)
            line_rev  = net_price * qty

            order_revenue     += line_rev
            order_cogs        += cogs * qty
            order_qty         += qty
            weighted_disc_num += disc_pct * line_rev   # Fix 4

        order_revenue    = round(order_revenue, 2)
        order_cogs       = round(order_cogs,    2)
        order_margin     = round(order_revenue - order_cogs, 2)
        order_margin_pct = round((order_margin / order_revenue * 100)
                                  if order_revenue > 0 else 0, 2)

        # Fix 4: true order-level discount = revenue-weighted average
        order_disc_pct = round(
            (weighted_disc_num / order_revenue * 100)
            if order_revenue > 0 else 0, 2)

        # Shipping — free above $75
        shipping = 0.0 if order_revenue >= 75 else round(
            random.uniform(5.99, 14.99), 2)

        # Fulfillment timing — peaks add delay
        base_days = random.choices([1,2,3,4,5,6,7],
                                    [0.10,0.25,0.30,0.20,0.08,0.05,0.02])[0]
        if seasonal_multiplier(order_date) > 1.8:
            base_days = min(base_days + random.randint(0, 2), 10)

        ship_date    = order_date + timedelta(days=random.randint(0, 2))
        deliver_date = ship_date  + timedelta(days=base_days)
        on_time      = deliver_date <= order_date + timedelta(days=6)
        date_id = int(order_date.strftime("%Y%m%d"))

        records.append({
            "OrderID":           order_id,
            "CustomerID":        customer_id,
            "PrimaryProductID":  product_ids[0],
            "DateID":            date_id,
            "ChannelID":         channel_id,
            "OrderDate":         order_date.date(),
            "ShipDate":          ship_date.date(),
            "DeliveryDate":      deliver_date.date(),
            "Quantity":          order_qty,
            "Revenue_USD":       order_revenue,
            "COGS_USD":          order_cogs,
            "GrossMargin_USD":   order_margin,
            "GrossMarginPct":    order_margin_pct,
            "DiscountPct":       order_disc_pct,   # Fix 4
            "ShippingCost_USD":  shipping,
            "FulfillmentDays":   base_days,
            "ShippedOnTime":     on_time,
            "OrderStatus":       "Completed",
        })

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════════
# 5. FACT RETURNS  (Fix 1: ReturnDate capped at END_DATE)
# ══════════════════════════════════════════════════════════════════════════════
def generate_fact_returns(orders: pd.DataFrame) -> pd.DataFrame:
    return_reasons  = ["Wrong size","Changed mind","Defective product",
                       "Not as described","Arrived late","Better price found"]
    reason_weights  = [0.30, 0.22, 0.18, 0.15, 0.08, 0.07]

    return_mask = np.random.random(len(orders)) < 0.12
    returns_sub = orders[return_mask].copy().reset_index(drop=True)

    records = []
    for i, row in returns_sub.iterrows():
        delivery_dt = pd.to_datetime(row["DeliveryDate"])
        max_return  = min(delivery_dt + timedelta(days=30),
                          datetime(END_DATE.year, END_DATE.month, END_DATE.day))

        # Skip if no valid return window
        if max_return <= delivery_dt:
            continue

        days_window = (max_return - delivery_dt).days
        return_date = (delivery_dt + timedelta(
            days=random.randint(1, days_window))).date()

        refund_amt = round(row["Revenue_USD"] * random.uniform(0.7, 1.0), 2)
        proc_days  = random.choices(
            [2,3,4,5,6,7,8,9,10],
            [0.10,0.20,0.25,0.20,0.10,0.07,0.04,0.02,0.02])[0]
        date_id    = int(pd.to_datetime(return_date).strftime("%Y%m%d"))

        records.append({
            "ReturnID":         i + 1,
            "OrderID":          row["OrderID"],
            "PrimaryProductID": row["PrimaryProductID"],
            "CustomerID":       row["CustomerID"],
            "DateID":           date_id,
            "ReturnDate":       return_date,
            "ReturnReason":     random.choices(return_reasons, reason_weights)[0],
            "RefundAmount_USD": refund_amt,
            "ProcessingDays":   proc_days,
            "ReturnStatus":     "Completed",
        })

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════════
# 6. DIM CUSTOMER  (Fix 2: FirstOrderDate derived from facts after generation)
# ══════════════════════════════════════════════════════════════════════════════
def generate_dim_customer(n: int,
                           channels: pd.DataFrame,
                           orders: pd.DataFrame) -> pd.DataFrame:
    segments    = ["Champions","Loyal","At Risk","Potential","Lost"]
    seg_weights = [0.15, 0.25, 0.20, 0.25, 0.15]

    regions     = ["Ontario","Quebec","British Columbia","Alberta","Manitoba",
                   "Saskatchewan","Nova Scotia","New Brunswick"]
    reg_weights = [0.38, 0.23, 0.14, 0.11, 0.05, 0.04, 0.03, 0.02]

    channel_ids = channels["ChannelID"].tolist()
    ch_weights  = [0.25, 0.20, 0.15, 0.10, 0.12, 0.08, 0.05, 0.05]

    ltv_map = {
        "Champions": (400, 1200),
        "Loyal":     (180, 500),
        "At Risk":   (80,  220),
        "Potential": (40,  150),
        "Lost":      (20,   80),
    }

    # Fix 2: derive FirstOrderDate from facts
    first_order = (orders.groupby("CustomerID")["OrderDate"]
                          .min()
                          .reset_index()
                          .rename(columns={"OrderDate": "FirstOrderDate"}))

    records = []
    for i in range(1, n + 1):
        segment  = random.choices(segments, seg_weights)[0]
        region   = random.choices(regions,  reg_weights)[0]
        channel  = random.choices(channel_ids, ch_weights)[0]

        ltv = round(random.uniform(*ltv_map[segment]), 2)
        cac_base = float(
            channels.loc[channels["ChannelID"]==channel, "AvgCAC_USD"].values[0])
        cac = round(max(cac_base + random.uniform(-3, 8), 0.01), 2)

        # Fix 2: look up actual first order date from facts
        match = first_order.loc[first_order["CustomerID"]==i, "FirstOrderDate"]
        first_dt = match.values[0] if len(match) else None

        records.append({
            "CustomerID":           i,
            "FirstName":            fake.first_name(),
            "LastName":             fake.last_name(),
            "Email":                fake.email(),
            "Region":               region,
            "City":                 fake.city(),
            "Segment":              segment,
            "AcquisitionChannelID": channel,
            "FirstOrderDate":       first_dt,   # Fix 2
            "LTV_USD":              ltv,
            "CAC_USD":              cac,
            "LTV_CAC_Ratio":        round(ltv / cac, 2),
        })

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 54)
    print("  E-Commerce Data Generator v2")
    print("=" * 54)

    print("\n[1/6] dim_date...")
    dim_date = generate_dim_date(START_DATE, END_DATE)
    dim_date.to_csv(f"{OUTPUT_DIR}/dim_date.csv", index=False)
    print(f"      {len(dim_date):,} rows")

    print("[2/6] dim_channel...")
    dim_channel = generate_dim_channel()
    dim_channel.to_csv(f"{OUTPUT_DIR}/dim_channel.csv", index=False)
    print(f"      {len(dim_channel):,} rows")

    print("[3/6] dim_product...")
    dim_product = generate_dim_product(N_PRODUCTS)
    dim_product.to_csv(f"{OUTPUT_DIR}/dim_product.csv", index=False)
    print(f"      {len(dim_product):,} rows")

    print("[4/6] fact_orders...")
    fact_orders = generate_fact_orders(
        N_ORDERS, N_CUSTOMERS, dim_product, dim_channel)
    fact_orders.to_csv(f"{OUTPUT_DIR}/fact_orders.csv", index=False)
    print(f"      {len(fact_orders):,} rows")

    print("[5/6] fact_returns  (ReturnDate capped at END_DATE)...")
    fact_returns = generate_fact_returns(fact_orders)
    fact_returns.to_csv(f"{OUTPUT_DIR}/fact_returns.csv", index=False)
    print(f"      {len(fact_returns):,} rows")

    print("[6/6] dim_customer  (FirstOrderDate derived from facts)...")
    dim_customer = generate_dim_customer(N_CUSTOMERS, dim_channel, fact_orders)
    dim_customer.to_csv(f"{OUTPUT_DIR}/dim_customer.csv", index=False)
    print(f"      {len(dim_customer):,} rows")

    # ── Validation checks ─────────────────────────────────────────────────
    print("\n--- Validation ---")

    # Fix 1 check: no return DateIDs outside dim_date
    valid_date_ids   = set(dim_date["DateID"])
    bad_return_dates = fact_returns[~fact_returns["DateID"].isin(valid_date_ids)]
    print(f"  Return DateIDs outside dim_date : {len(bad_return_dates)}  (target: 0)")

    # Fix 2 check: no orders before FirstOrderDate
    merged = fact_orders.merge(
        dim_customer[["CustomerID","FirstOrderDate"]], on="CustomerID", how="left")
    merged["OrderDate"]      = pd.to_datetime(merged["OrderDate"])
    merged["FirstOrderDate"] = pd.to_datetime(merged["FirstOrderDate"])
    early_orders = merged[merged["OrderDate"] < merged["FirstOrderDate"]]
    print(f"  Orders before FirstOrderDate    : {len(early_orders)}  (target: 0)")

    # Fix 3 check: AOV
    aov = fact_orders["Revenue_USD"].mean()
    print(f"  Average order value             : ${aov:.2f}  (target: $130-$160)")

    # Fix 4 check: DiscountPct is order-level weighted avg
    multi = fact_orders[fact_orders["DiscountPct"] > 0]
    print(f"  Orders with discount            : {len(multi):,}  ({len(multi)/len(fact_orders)*100:.1f}%)")

    # General stats
    total_rev   = fact_orders["Revenue_USD"].sum()
    return_rate = len(fact_returns) / len(fact_orders) * 100
    on_time_pct = fact_orders["ShippedOnTime"].mean() * 100

    print(f"\n--- Summary ---")
    print(f"  Total revenue   : ${total_rev:,.2f}")
    print(f"  Orders          : {len(fact_orders):,}")
    print(f"  Returns         : {len(fact_returns):,}  ({return_rate:.1f}%)")
    print(f"  On-time pct     : {on_time_pct:.1f}%")
    print(f"\n  Output folder   : {OUTPUT_DIR}")
    print("=" * 54)


if __name__ == "__main__":
    main()
