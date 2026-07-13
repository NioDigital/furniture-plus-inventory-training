# 📋 Furniture Plus — Odoo 19 Inventory Training Manual

**Prepared by:** Nio Digital — Functional Consultant Trainer  
**Platform:** Odoo 19  
**Audience:** Store Managers, Warehouse Staff, CSRs, Fleet Coordinators, Management  
**Version:** 1.0 | July 2026

---

## Table of Contents

1. [Getting Started — Your Inventory World](#1-getting-started---your-inventory-world)
2. [Warehouse Structure — How Stores & Warehouses Fit Together](#2-warehouse-structure--how-stores--and-warehouses-fit-together)
3. [Product Categories & Stock Locations](#3-product-categories--stock-locations)
4. [Receiving Goods — Docking & Put-Away](#4-receiving-goods---docking--put-away)
5. [Min/Max Replenishment — Keeping Stores Stocked](#5-minmax-replenishment--keeping-stores-stocked)
6. [Direct-to-Store Purchases — Vendor Delivers Directly](#6-direct-to-store-purchases--vendor-delivers-directly)
7. [Internal Transfers — Store-to-Store & Warehouse-to-Store](#7-internal-transfers--store-to-store--warehouse-to-store)
8. [Reservations — Holding Stock for Customers](#8-reservations--holding-stock-for-customers)
9. [Physical Inventory Counts](#9-physical-inventory-counts)
10. [Scrap & Damaged Goods](#10-scrap--damaged-goods)
11. [Fleet Management — Delivery Tracking](#11-fleet-management---delivery-tracking)
12. [Backorder Procedures — When You Can't Fulfill Everything](#12-backorder-procedures--when-you-cant-fulfill-everything)
13. [Stock Reporting & Dashboards](#13-stock-reporting--dashboards)
14. [Quick Reference — Common Tasks](#14-quick-reference---common-tasks)

---

## 1. Getting Started — Your Inventory World

### What Odoo Inventory Manages for Furniture Plus

Odoo is the system that tracks every piece of furniture, every item, and every location across all your stores and the main warehouse. Think of it as a digital ledger that knows exactly where every product is, who has it reserved, when it arrived, and what needs restocking.

### Key Terms You'll Use Daily

| Term | What It Means | Example |
|------|--------------|---------|
| **Warehouse** | A physical or logical storage location | Main Warehouse (Port of Spain), Store #3 Warehouse (San Fernando) |
| **Stock Location** | A specific spot within a warehouse where items live | "Reserve Shelf" at Store #7 |
| **Product** | Any sellable item | "Modern 3-Seater Sofa — Charcoal" |
| **Operation Type** | The type of movement (receipt, delivery, internal transfer) | "Receipts" at Main Warehouse |
| **Pick/Pack/Ship** | The process of pulling items for a customer order | Picking the dining table for a customer purchase |
| **Replenishment** | Restocking stores from the warehouse or vendors | Min/Max rule triggers a transfer request |
| **Backorder** | Remaining items on an order that are temporarily out of stock | Customer ordered 10 dining chairs, only 7 available — backorder for 3 |
| **Put-Away Rule** | Automatic instruction for where incoming goods should go | All "Office Furniture" goes to Aisle C in the Main Warehouse |

### Navigation Basics

To access inventory features in Odoo:
- Go to the **Inventory** app (the crate 📦 icon) from the main dashboard.
- The left sidebar contains: **Products**, **Warehouses**, **Orders** (Receipts/Transfers/Deliveries), **Reports**, and **Configuration**.

---

## 2. Warehouse Structure — How Stores & Warehouses Fit Together

### Your Setup at a Glance

Furniture Plus operates with a hierarchical warehouse model:

```
🏢 MAIN WAREHOUSE (Distribution Hub)
│   ├── Docking Areas (1–7) — Where trucks pull up
│   ├── Bulk Storage Zones (Aisle A–H)
│   └── Ready-to-Ship Staging Area
│
├── 🏬 Store #1 Warehouse (San Fernando)
│   ├── Floor Stock
│   └── Reserve Shelf
│
├── 🏬 Store #2 Warehouse (Port of Spain Central)
│   ├── Floor Stock
│   └── Reserve Shelf
│
├── 🏬 Store #3 Warehouse (Arima)
│   └── ... (and so on for all 10+ stores)
```

### How Stores Work in Odoo

Each store is configured as a **separate warehouse** in Odoo with:
- Its own stock locations (floor, reserve, receiving dock)
- Its own product catalog (all Furniture Plus products available to all stores)
- Its own inventory counts and valuations
- Staff who see only that store's data

### What This Means for You

- **Store Managers:** You manage only your store's warehouse in Odoo. You don't see other stores' stock levels — unless a transfer is initiated.
- **Main Warehouse Team:** You handle receipts from vendors, internal transfers to all stores, and the central inventory pool.
- **Management:** Can view consolidated reports across all warehouses.

---

## 3. Product Categories & Stock Locations

### Product Categories Used at Furniture Plus

| Category | Examples | Special Handling |
|----------|---------|------------------|
| **Furniture — Living Room** | Sofas, sectionals, coffee tables | Bulky items require special delivery routes |
| **Furniture — Bedroom** | Beds, mattresses, dressers | Requires assembly coordination |
| **Furniture — Office** | Desks, chairs, filing cabinets | Moderate weight, pallet-shipment possible |
| **Office Furniture** | Workstations, conference tables | Large items, white-glove delivery required |
| **Accessories** | Cushions, throws, decorative items | High volume, easy to pick and pack |
| **Lighting** | Chandeliers, lamps | Fragile — handled with care protocols |
| **Rugs & Flooring** | Area rugs, carpet tiles | Rolled storage, weight tracking important |

### Stock Locations Within Each Warehouse

Every warehouse contains these standard locations:

```
WH (Warehouse Root)
├── 📥 WH/Receipt (Incoming goods staging area)
├── 📦 WH/Stock (Active inventory — where items live between movements)
│   ├── WH/Stock/Bulk (Bulk storage for reserve stock)
│   └── WH/Stock/Floor (Floor display items)
├── 🔒 WH/Reserve (Reserved items — tied to customer orders)
├── 📤 WH/Output (Items ready for delivery)
├── ✂️ WH/Scrap (Damaged goods removed from active stock)
└── 🔄 WH/Lot (For future inventory adjustment staging)
```

### How Stock Levels Work

- **Free Qty:** Items available to sell right now.
- **Reserved Qty:** Items already committed to customer orders — not for sale.
- **Forecasted Qty:** Free + Incoming transfers — Inbound minus Outbound deliveries = what you expect to have soon.

**📌 Example — Checking Stock for a Customer:**

> A customer at Store #3 wants "Modern 3-Seater Sofa — Charcoal." The CSR opens the product form and sees:
> - **Free Qty:** 3 (available immediately)
> - **Reserved Qty:** 2 (already sold but not picked)
> - **Forecasted Qty:** 8 (3 free + 5 expected from Main Warehouse transfer in 2 days)

The CSR tells the customer: *"Good news — we have 3 in stock right now, and another 5 arriving in 2 days."*

---

## 4. Receiving Goods — Docking & Put-Away

### The Docking Process (Main Warehouse Only)

You have **7 docking areas** at the Main Warehouse. Each dock is a specific location where trucks pull up for deliveries.

#### Step-by-Step: Receiving a Vendor Delivery

1. **Truck Arrives at a Dock**
   - The receiving clerk assigns the truck to a docking area (Dock 1 through Dock 7).
   - Create a **Receipt** in Odoo: `Inventory → Operations → Receipts → Create`
   - Select the vendor and scan or enter the products being delivered.

2. **Verify Quantity & Quality**
   - Compare the vendor's delivery note against the Receipt in Odoo.
   - Confirm quantities match. If there's a discrepancy, note it on the receipt before confirming.

3. **Confirm the Receipt**
   - Click **Validate** when all items are verified.
   - Odoo automatically moves the stock from *Receipt Location → Stock Location* for each warehouse.

4. **Put-Away Automation (For Specific Categories)**
   - **Auto-Putaway:** If you have put-away rules configured, Odoo will suggest where to place each item:
     - All "Office Furniture" → Aisle C, Rack 2
     - All "Lighting" → Zone D, Climate-Controlled Section
     - All "Rugs & Flooring" → Zone F, Flat Storage
   - The put-away rule eliminates guessing — items go to the right place automatically.

### 📌 Use Case Example: Large Furniture Delivery

> **Scenario:** A vendor delivers 15 dining tables and 60 chairs to Dock #3.
> 
> **Steps:**
> 1. Clerk creates a Receipt, references the PO# from management approval.
> 2. Scans barcodes for all items (or enters quantities manually).
> 3. Confirms receipt — Odoo moves stock to Main Warehouse.
> 4. Put-away rule kicks in: tables → Aisle B Rack 1; chairs → Aisle B Rack 3–5.
> 5. The items are now available for allocation to any store or customer order.

### Barcode Scanning During Receipts

- Use a handheld barcode scanner or the Odoo mobile app to scan barcodes on each item as it's unloaded.
- This ensures **real-time accuracy** — no manual counting errors.
- Management is evaluating standard brand scanners for all docks (see Next Steps).

---

## 5. Min/Max Replenishment — Keeping Stores Stocked

### How It Works

Each product in each store has a **Minimum Quantity** and **Maximum Quantity** configured:

| Product | Min Qty | Max Qty | Current Free Qty | Action Triggered |
|---------|---------|---------|-----------------|------------------|
| Modern Sofa — Charcoal (Store #3) | 5 | 20 | 4 | ✅ Transfer Request Created |
| Office Desk — Walnut (Store #7) | 3 | 15 | 8 | — (OK, above min) |

When a store's stock falls **below the minimum**, Odoo automatically creates a **Replenishment** (a request to move product to that store).

### The Replenishment Flow for Furniture Plus

```
Store Stock < Minimum Qty?
    │
    ├── YES → Odoo creates a Transfer Request
    │           │
    │           ├── If source = Main Warehouse: Main WH team picks & ships
    │           └── If source = Direct from Vendor: Management reviews & approves PO
    │
    └── NO  → No action needed ✅
```

### Step-by-Step: When a Store Hits Its Minimum

> **Scenario:** Store #5's "Classic Leather Recliner — Brown" drops to 4 units. The minimum is 5.

1. **System Action:** Odoo automatically creates an internal transfer request from the Main Warehouse.
2. **Main WH Team Sees It:** On the **Transfers** dashboard under "Internal," the replenishment appears:
   ```
   From: Main Warehouse / Stock → To: Store #5 / Stock
   Product: Classic Leather Recliner — Brown | Qty: 10
   ```
3. **Main WH Picks & Ships:** The warehouse team picks 10 recliners from bulk storage and delivers them to Store #5.
4. **Store #5 Receives:** The store manager confirms receipt, and the stock level rises back above the minimum.

### ⚠️ Important: When the Main Warehouse Also Has Low Stock

If the Main Warehouse can't fulfill the full quantity:
- Create a **partial transfer** for what's available.
- Management reviews the remaining gap and decides: order from vendor or let the store wait.
- **Approval Required:** Any transfer exceeding configured thresholds requires management sign-off in Odoo.

---

## 6. Direct-to-Store Purchases — Vendor Delivers Directly

### When This Happens

Some stores have vendor agreements that allow direct purchasing (bypassing the main warehouse). Examples:
- A local furniture manufacturer delivering custom pieces to Store #2.
- An emergency restock of a high-demand item where the Main Warehouse is empty.

### The Approval Workflow

```
Store Manager identifies need → Creates Purchase Request in Odoo
        │
        ▼
Management reviews request (email/dashboard notification)
        │
        ▼
Management approves → PO sent to vendor directly
        │
        ▼
Vendor delivers to store → Store creates Receipt in Odoo
        │
        ▼
Stock lands directly in the store's warehouse (not through main WH)
```

### Step-by-Step: Direct-to-Store Purchase

> **Scenario:** Store #7 runs out of a popular coffee table. The Main Warehouse is empty.

1. **Store Manager** opens Inventory → Vendor Bills/Orders → Create Purchase Order.
2. **Selects the vendor**, adds the product, confirms quantity.
3. **Sends to Management** for approval (system flags it for review).
4. **Management approves** in Odoo — PO is sent to the vendor.
5. **Vendor delivers** directly to Store #7's receiving dock.
6. **Store creates a Receipt**, scans items, confirms — stock appears immediately at Store #7.

### 📌 Key Rule

All direct-to-store purchases **must** be approved by management before confirmation. Unapproved POs should never be confirmed in Odoo.

---

## 7. Internal Transfers — Store-to-Store & Warehouse-to-Store

### Types of Internal Movements

| Movement Type | From → To | Who Initiates | Approval Needed |
|--------------|-----------|---------------|-----------------|
| **Replenishment** | Main WH → Any Store | Auto (Min/Max rule) | No* (*subject to thresholds) |
| **Manual Transfer** | Any Store ↔ Any Store | Store Manager | Yes — manager approval on both ends |
| **Emergency Borrow** | One Store → Another Store (temporary) | Store Manager | Yes — management sign-off required |
| **Return to WH** | Store → Main WH | Store Manager | No — standard return |

### Transferring Stock Between Stores

> **Scenario:** Store #4 has 20 extra dining chairs they won't use this quarter. Store #9 needs 12.

**Steps:**
1. **Store #4 Manager** opens Inventory → Operations → Internal Transfers → Create.
2. Selects source: "Store #4 / Stock," destination: "Store #9 / Stock."
3. Adds product: Dining Chair — Oak | Qty: 12.
4. Sends for approval (auto-routed to Store #9 manager).
5. **Store #9 Manager** receives a notification, opens the transfer, confirms receipt.
6. The stock moves out of Store #4 and into Store #9. Both sides' inventory is updated.

### 📌 Use Case: Inter-Store Emergency Transfer

> **Scenario:** A customer at Store #1 wants a specific sofa that's only in Stock at Store #6.

**Quick Transfer (Express Lane):**
1. CSR at Store #1 checks Odoo → Products → search sofa → check "Available at Other Locations."
2. Sees: 2 available at Store #6.
3. Manager at both stores approves a same-day transfer.
4. Truck picks up from Store #6 and delivers to Store #1 (usually within hours).
5. Customer gets their order — no lost sale!

---

## 8. Reservations — Holding Stock for Customers

### What Is a Reservation?

A reservation means a specific item is **tied to a customer order** — it's set aside so nobody else can sell it while waiting for pickup or delivery.

### The Reserve Location System

Each store has a dedicated **"Reserve" location**:
- Items here are visible in Odoo as "Reserved Qty."
- They remain on the shelf but cannot be sold again.
- Only CSRs and managers (with elevated permissions) can release a reservation.
- Regular CSRs **can view** reservations but **cannot modify or unreserve** them.

### Reservation Workflow — Customer Orders Furniture

> **Scenario:** A customer places an order for a $3,000 sectional at Store #3.

1. **CSR creates the Sale Order** in Odoo (or via POS).
2. System checks stock → confirms 2 sectionals are available.
3. Clicks **Reserve Stock** → those 2 items move from "Free" to "Reserved."
4. The items sit in the **Reserve Location** until delivered or picked up.
5. When the customer pays and picks up:
   - CSR confirms the delivery/sale → stock leaves the Reserve location.
6. If the customer cancels:
   - Manager releases the reservation → items return to "Free" stock.

### 📌 What CSRs Can and Cannot Do

| Action | CSR | Store Manager | Warehouse Staff |
|--------|-----|---------------|-----------------|
| View reservations at their store | ✅ Yes | ✅ Yes | ✅ Yes (own warehouse) |
| Reserve items for customers | ✅ Yes (via SO) | ✅ Yes | N/A |
| Unreserve/release items | ❌ No | ✅ Yes | N/A |
| Modify reservation quantities | ❌ No | ✅ Yes | N/A |

---

## 9. Physical Inventory Counts

### How and When Counts Happen

| Count Type | Frequency | Who Does It | What's Counted |
|-----------|-----------|-------------|----------------|
| **Scheduled Full Count** | Quarterly (or as needed) | Assigned users per store | Entire warehouse |
| **Cycle Count** | Weekly/Monthly per location | Designated counter | Specific aisles/zones |
| **Spot Count** | As needed (audit/dispute) | Any authorized user | Single product or bin |

### Barcode Scanning Counts

1. Open Inventory → Operations → Physical Inventory → Create.
2. Select the **product** or **location** to count.
3. Assign a counter (or leave it unassigned — anyone can do it).
4. Open the **barcode scanning app** and scan each item as you go.
5. Enter confirmed quantities for each scanned item.
6. When all items are counted → click **Validate**.

### The Two-Step Validation (Safety Feature)

Odoo separates counting from accounting to prevent accidental stock changes:

```
Step 1: Count Submission (Done by store staff)
   └── "We counted X of Product A, Y of Product B..."
   
Step 2: Manager Approval & Accounting Adjustment (Done by manager)
   └── System calculates the variance → adjusts inventory value accordingly.
```

This means a store employee can't unilaterally change the recorded stock value — **only management** can approve the financial impact after reviewing the count.

### 📌 Use Case: Inventory Audit Discrepancy

> **Scenario:** Weekly cycle count at Store #2 shows 50 "Modern Sofa — Charcoal" but Odoo says 47.
> 
> **Counter submits:** 50 on barcode app.
> **Manager reviews:** Finds the 3-unit difference. Investigates (discovers a customer return wasn't scanned).
> **Manager approves count:** Stock updates to 50, audit trail records the variance and reason.

---

## 10. Scrap & Damaged Goods

### When to Use Scrap

Scrap removes items from active inventory permanently:
- Items damaged in transit or at the warehouse/store.
- Products returned by customers that can't be resold.
- Expired or discontinued products.

### The Scrap Process (Requires a Reason Code)

> **Scenario:** A customer returns a sofa with a torn seat cushion — not resellable.

1. Open Inventory → Operations → Scrap → Create.
2. Select the product and warehouse.
3. Enter quantity to scrap.
4. **Select a mandatory reason code** (e.g., "Customer Return — Damaged," "Transit Damage," "Manufacturing Defect").
5. Confirm the scrap.

### Financial Impact

- The **full value of the scrapped items is deducted from inventory** immediately.
- The accounting entries are generated automatically for cost-of-goods adjustments.
- A detailed report tracks all scrap activity by reason code, store, and date — available for management review.

---

## 11. Fleet Management — Delivery Tracking

### What Fleet Management Tracks

Odoo's Fleet module (being set up for Furniture Plus) will track:
- Company-owned delivery trucks and contractor vehicles
- Driver assignments per delivery route
- Digital signatures from customers upon delivery
- Delivery status in real time

### Setting Up a Delivery Truck in Odoo (Fleet App)

When Fleet Management is fully configured:
1. Open **Fleet** app → Vehicles → Create.
2. Enter truck details: license plate, driver, capacity, type (company vs. contractor).
3. Associate the vehicle with delivery routes and store zones.

### Digital Signature on Delivery

> **Scenario:** A truck from the Main Warehouse delivers a sectional to Store #3's receiving dock.

1. The driver opens the delivery in Odoo (mobile/tablet).
2. At the docking area, the receiver signs on a tablet or phone.
3. The signature is captured and attached to the delivery record in Odoo.
4. Stock is confirmed received — the process is closed with digital proof.

**Benefits:**
- No lost deliveries — every handoff is documented.
- Dispute resolution — if someone claims "we didn't receive it," the signature proves otherwise.

---

## 12. Backorder Procedures — When You Can't Fulfill Everything

### What Is a Backorder?

A backorder happens when you can't fulfill an order completely — some items are available, but others are out of stock. Odoo handles this by splitting the order:
- The available items ship immediately.
- The missing items create a **backorder** that gets flagged for admin review.

### System Alert for Backorders (Upcoming Configuration)

> [Nio] Configure Backorder Validation
> 
> A system alert will notify users when items are missing during scanning. Administrative approval will be required to confirm backorder adjustments.

#### Current Manual Procedure (Until Alert Is Active)

1. **Scanning the order:** You scan each item as you pick it.
2. **Quantity mismatch detected:** If fewer items than ordered are available, Odoo shows a warning: *"Not enough stock for X items."*
3. **Partial fulfillment:** Confirm what IS available → the rest becomes a backorder automatically.
4. **Admin Approval Required:** Before the backorder can be confirmed, it routes to an administrator (warehouse manager or store manager) who reviews and approves.
5. **Customer Notification:** Management contacts the customer about the delay — sets expectations.

### 📌 Use Case: Partial Delivery

> **Scenario:** A restaurant orders 20 dining tables and 80 chairs. Main Warehouse has all 80 chairs but only 14 tables.

**What Happens:**
1. Warehouse team picks 80 chairs → ships immediately to the customer.
2. Remaining 6 tables → backorder created automatically.
3. Manager gets alerted: *"Backorder #BO-1847 needs approval for 6 dining tables."*
4. Manager checks with vendors → confirms 6 more arriving in 5 days.
5. Manager approves backorder → customer is notified of the expected delivery date.

---

## 13. Stock Reporting & Dashboards

### Key Reports Everyone Should Know

| Report | Who Uses It | What It Shows |
|--------|------------|---------------|
| **Inventory Valuation** | Management, Finance | Total value of all inventory at each warehouse |
| **Free vs. Reserved Qty** | CSRs, Store Managers | What's available to sell vs. what's already committed |
| **Stock Moves History** | Warehouse Staff | Every movement of every product (receipts, transfers, scrap, counts) |
| **Transfer Requests** | All | Pending, in-progress, and completed transfers across all stores |
| **Backorder Report** | Management | Outstanding backorders with expected resolution dates |
| **Scrap Log** | Management | Damaged/scrapped items by reason code, store, and date |
| **Minimum Stock Report** | Store Managers | Which products in which stores are below minimum thresholds |

### The Warehouse Dashboard (Main Warehouse Team)

The Main Warehouse team has a centralized dashboard showing:
- **Pending Transfer Tasks:** All active internal transfers to/from stores.
- **Picking Requirements:** Products that need to be pulled to fulfill orders.
- **Dock Schedules:** Which docking areas are occupied, which trucks are expected.
- **Replenishment Queue:** Min/Max triggered requests waiting for processing.

---

## 14. Quick Reference — Common Tasks

### 🔹 "I need to check if a product is in stock"

1. Open **Inventory → Products** → search the product name or scan its barcode.
2. On the product form, look at:
   - **Free Qty:** Available right now
   - **Reserved Qty:** Already sold/committed
   - **Forecasted Qty:** Expected to arrive soon
3. To check a specific store: Click on the location/filter → select that store's warehouse.

### 🔹 "A customer wants to reserve an item"

1. Open or create a **Sale Order** (or POS order).
2. Add the product and quantity.
3. Confirm → Odoo reserves the stock automatically.
4. Item moves from "Free" to "Reserved."

### 🔹 "I need to receive a vendor delivery"

1. Open **Inventory → Operations → Receipts → Create**.
2. Select vendor and PO reference.
3. Scan or enter products.
4. Validate → stock is received.

### 🔹 "A store is running low — I need to transfer stock"

1. **Automatic:** If Min/Max is configured, Odoo creates the transfer automatically.
2. **Manual:** Open **Inventory → Operations → Internal Transfers → Create** → select source and destination → confirm.

### 🔹 "An item is damaged — I need to scrap it"

1. Open **Inventory → Operations → Scrap → Create**.
2. Select product, quantity, and a **mandatory reason code**.
3. Confirm.

### 🔹 "I need to see the audit trail for stock changes"

1. Open the product form → click **Inventory History** or **Stock Moves**.
2. Every receipt, transfer, count, and scrap is logged here with timestamps and user.

---

## Appendix A: Permissions Matrix — Who Can Do What

| Task | CSR | Store Manager | Warehouse Staff (Main WH) | Management/Finance |
|------|-----|---------------|--------------------------|-------------------|
| View own store's stock | ✅ | ✅ | ✅ (own WH) | ✅ (all stores) |
| Create receipts | ❌ | ✅ | ✅ (Main WH only) | ✅ |
| Confirm deliveries | ❌ | ✅ | ✅ (Main WH only) | ✅ |
| Reserve stock for customers | ✅ (via SO) | ✅ | — | — |
| Unreserve/release items | ❌ | ✅ | — | ✅ |
| Create internal transfers | ❌ | ✅ | ✅ (own WH) | ✅ (all) |
| Approve backorders | ❌ | ✅ | ✅ | ✅ |
| Conduct inventory counts | ✅ (assigned) | ✅ | ✅ | ✅ |
| Confirm count adjustments | ❌ | ✅ | — | ✅ |
| Create scrap entries | ❌ | ✅ | ✅ (own WH) | ✅ |
| Approve scrap | ❌ | ✅ | ✅ | ✅ |
| View all store reports | ❌ | ❌ (own only) | ❌ (own only) | ✅ |
| Manage fleet vehicles | ❌ | ❌ | ❌ | ✅ |

---

## Appendix B: Troubleshooting Common Issues

### "I can't see stock for another store"
- This is by design. Each warehouse location is siloed to its staff.
- To see other stores' stock, managers with multi-store access must use the consolidated inventory view in Reports.

### "A transfer request is stuck and won't process"
1. Check if it requires management approval (look for the "To Approve" badge).
2. Verify source warehouse has sufficient free qty.
3. Confirm there are no blocked locations or count-in-progress flags.

### "Barcode scanner isn't working"
- Ensure the device is paired and connected to the Odoo inventory app.
- Try scanning a different barcode to rule out product data issues.
- If persistent, notify Nio Digital support.

### "Stock doesn't match what I counted"
- Review the **last physical count** for discrepancies.
- Check **recent scrap entries** — items may have been scrapped but not reported.
- Review **stock moves history** for any unrecorded transfers.

---

## Appendix C: Glossary of Odoo Inventory Terms

| Term | Definition |
|------|-----------|
| **Lots/Serial Numbers** | Unique identifiers on products for traceability |
| **Double-Entry** | Every stock move has a debit (from) and credit (to) location |
| **Shelf Life** | Maximum time a product can be held before expiring (for applicable items) |
| **Lead Time** | Expected number of days between ordering and receiving |
| **Routing** | The defined path stock takes through the warehouse during movements |
| **Reordering Rule** | Automated rule that triggers orders or transfers when stock falls below minimum |
| **Incoterms** | Delivery terms (who pays for shipping, where risk transfers) — configured per vendor |

---

## Appendix D: Future Features Coming to Furniture Plus

These items are in development/planning and will be covered in future training sessions:

- ✅ **Donation Tracking:** Track furniture donations with separate inventory categories
- ✅ **Temporary Stock Loaning:** Borrow stock from another store or vendor with return tracking
- ✅ **Audit Configurations:** Enhanced reporting for regulatory/compliance audits
- ⏳ **Standard Barcode Scanners:** Evaluating feasibility of company-brand scanners across all stores and docks
- ⏳ **Fleet Management Integration:** Full delivery route optimization and contractor truck tracking

---

## Questions?

This manual covers the inventory workflows you'll use day-to-day. If something isn't addressed here, or if your process differs slightly from what's documented:

1. Note the discrepancy — don't force a square peg into a round hole.
2. Contact your Nio Digital support team or your Store Manager for clarification.
3. Updates to this manual are issued whenever Odoo configurations change.

---

*End of Training Manual — Furniture Plus Inventory Operations — Odoo 19 — July 2026*
