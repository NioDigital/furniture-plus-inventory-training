# 📋 FURNITURE PLUS — Odoo 19 INVENTORY MANAGEMENT TRAINING MANUAL

**Version:** 1.0 | **Date:** July 2026  
**Prepared for:** Furniture Plus (FP) | **Odoo Version:** 19  
**Department:** Inventory & Warehouse Operations  

---

## TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [Warehouse Structure & Locations](#2-warehouse-structure--locations)
3. [User Roles & Access Permissions](#3-user-roles--access-permissions)
4. [Inbound Operations — Receiving Goods](#4-inbound-operations--receiving-goods)
5. [Stock Valuation & FIFO](#5-stock-valuation--fifo)
6. [Multi-Store Transfers — Main Warehouse to Stores](#6-multi-store-transfers--main-warehouse-to-stores)
7. [Direct Ship Purchases — Supplier to Store](#7-direct-ship-purchases--supplier-to-store)
8. [Automated Replenishment — Min/Max Rules](#8-automated-replenishment--minmax-rules)
9. [Point of Sale (POS) Integration](#9-point-of-sale-pos-integration)
10. [Backorders & Exception Handling](#10-backorders--exception-handling)
11. [Stock Reservations — Customer Orders](#11-stock-reservations--customer-orders)
12. [Physical Inventory Counts](#12-physical-inventory-counts)
13. [Scrap, Damage & Returns Processing](#13-scrap-damage--returns-processing)
14. [Fleet Management & Deliveries](#14-fleet-management--deliveries)
15. [Barcode Scanning Operations](#15-barcode-scanning-operations)
16. [Reporting & Dashboards](#16-reporting--dashboards)
17. [Common Use Cases — Step by Step](#17-common-use-cases--step-by-step)
18. [Troubleshooting FAQ](#18-troubleshooting-faq)

---

## 1. SYSTEM OVERVIEW

### What This Manual Covers

This manual is designed for **Furniture Plus** staff who work with Odoo 19 Inventory across:

- **1 Main Warehouse** (distribution hub — central stock, receives all supplier deliveries)
- **10+ Store Warehouses** (each store has its own warehouse record in Odoo)
- **Direct Supplier-to-Store purchasing**
- **Automated replenishment between main warehouse and stores**
- **Barcode scanning for counts and transfers**
- **Fleet/delivery management with driver sign-off**

### Key Terms You'll See Throughout

| Term | Meaning |
|------|---------|
| **Warehouse** | A logical building/zone in Odoo where stock is held. Each FP store = 1 warehouse. |
| **Location** | A specific spot inside a warehouse (e.g., "Store A / Shelving / Aisle 3") |
| **Operation Type** | The *type* of move: Receipts, Internal Transfers, Shipments, etc. |
| **Product** | Any item in inventory — furniture pieces, cushions, hardware, fixtures |
| **Route** | The rules that dictate how a product flows (replenish from main? direct ship?) |
| **Push/Pull Rules** | Automated triggers that create moves when stock reaches min/max thresholds |
| **Reservation** | Stock earmarked for a specific customer order so it won't be sold to someone else |
| **FIFO** | First-In, First-Out — Odoo's default stock removal method (oldest stock leaves first) |

---

## 2. WAREHOUSE STRUCTURE & LOCATIONS

### The Furniture Plus Warehouse Hierarchy

```
Odoo Database
│
├── 🏭 Main Warehouse (WH_MAIN) — Distribution Hub
│   ├── Receipts (Docking Area 1-7)
│   ├── Stock / Bulk Storage
│   ├── QC Inspection Location
│   ├── Reserved Stock (for customer orders)
│   ├── Scrap / Damage Zone
│   └── Outgoing Shipments
│
├── 🏪 Store 01 Warehouse (WH_STORE_01)
│   ├── Reception Area
│   ├── Sales Floor / Display Area
│   ├── Reserve Location (for customer orders)
│   └── Scrap Location
│
├── 🏪 Store 02 Warehouse ... up to Store 12+
│   ├── (same structure as above)
│
└── 📦 Virtual Locations (system-managed, do not edit manually)
    ├── Stock Input (where incoming goods land)
    ├── Stock Output (where outgoing goods depart)
    └── Lost & Found (mismatched stock goes here)
```

### Creating a New Store Warehouse — Checklist

When Furniture Plus opens a new store:

1. **Inventory → Configuration → Warehouses** → Click *New*
2. Name: `WH_STORE_[XX]` (e.g., `WH_STORE_05`)
3. Address: Full store address
4. Define the following locations in the warehouse setup wizard:
   - `/Stock` — primary stock location
   - `/Input` — receipt staging area
   - `/Output` — shipment dispatch area
   - `/Reserve_CustOrders` — reserved for customer purchases
   - `/Scrap` — damaged/unusable goods

5. Assign **Warehouse Managers** per store (see Section 3)
6. Add **Docking Areas** if the store has multiple loading bays
7. Configure **Min/Max Replenishment Rules** (see Section 8)
8. Enable **Barcode App** for that warehouse (Settings → Barcode)

> ⚠️ **Rule:** Each store MUST have its own warehouse record. Never mix stores in one warehouse — it breaks reporting and transfer accountability.

---

## 3. USER ROLES & ACCESS PERMISSIONS

### Furniture Plus User Roles

| Role | Access Level | Who Typically Has This |
|------|-------------|----------------------|
| **Inventory Administrator** | Full access to all warehouses, configurations, reports | Warehouse Manager / Nio Admin |
| **Warehouse Manager (per warehouse)** | Full access to their store's warehouse only; can approve transfers | Store Managers |
| **Inventory User** | Receive, move, count stock. No configuration changes. | CSR Staff, Floor Associates |
| **Inventory Picker** | Only sees and executes transfer orders / deliveries | Warehouse Pickers |
| **Read-Only Inventory** | Can view stock levels, reservations; no modifications allowed | CSRs viewing reservations for customers |

### Permission Setup — Example: Store Manager Approval Workflow

For **inter-store transfers**, the following approval chain applies:

```
Store A Manager (creates transfer) 
    → Manager approves via Odoo 
        → Main Warehouse Picker fulfills transfer 
            → Store B Receiver confirms receipt
```

**To set this up:**
1. Go to **Inventory → Configuration → Users**
2. For each store manager, assign:
   - `Warehouse Manager` rights on their specific warehouse only
3. Enable **Transfer Approval** for non-manager users under **Settings → Inventory**
4. Set transfer thresholds — e.g., transfers over 50 units or above $10K require Warehouse Administrator approval

### Critical Security Rules

- **CSRs** can *view* reservations but CANNOT unreserve or modify stock
- **Store managers** approve inter-store transfers but cannot alter another store's configuration
- **Only Inventory Admins** can modify routes, min/max rules, or dock door configurations
- **No one** can skip the backorder validation workflow (see Section 10)

---

## 4. INBOUND OPERATIONS — RECEIVING GOODS

### Scenario A: Delivery from Supplier to Main Warehouse (Docking Areas 1–7)

This is the most common inbound flow for Furniture Plus.

#### Step-by-Step: Receiving at Main Warehouse Dock

**Who:** Dock Workers → Warehouse Manager → QC Inspector

| Step | Action | Odoo Navigation | Notes |
|------|--------|-----------------|-------|
| 1 | Supplier sends delivery order (DO) with packing slip | Purchase Order confirms → Auto-creates Transfer in Odoo | PO must have correct product, qty, UoM |
| 2 | Dock worker arrives at assigned door (Door #3, for example) | **Inventory → Operations → Receipts** → Find the transfer | Transfers appear automatically when PO is confirmed |
| 3 | Scan/verify products against packing slip | Click *Scan* button or enter quantities manually | Use barcode app: scan item → confirm qty |
| 4 | Handle discrepancies (overage, shortage, damage) | See Section 10 — Backorders & Exceptions | If qty doesn't match → system prompts for backorder approval |
| 5 | Confirm receipt | Click *Validate* | Stock now appears in `/Stock` of Main Warehouse |
| 6 | QC inspection (if applicable) | Move to **QC Inspection Location** if needed | Some high-value furniture items require QC before stocking |

#### Example: Receiving 24 Dining Tables from "WoodCraft Furnishings"

```
1. Purchase Order confirmed → Transfer #TRF_001 created
   - Product: DT-4200 (Dining Table, Mahogany) — Qty: 24
   - Supplier: WoodCraft Furnishings
   - Scheduled Dock Door: #5

2. Driver arrives at Dock #5 with 24 tables
3. Dock Worker scans each table's barcode or enters manually:
   - DT-4200 × 24 ✓ (matches PO exactly)
4. Warehouse Manager verifies on tablet → clicks *Validate*
5. Stock update: Main WH /Stock now has +24 DT-4200
6. Cost impact: COGS valuation updated per FIFO method
```

### Scenario B: Direct Ship — Supplier to Store (Store Handles Receipt)

Some stores purchase items directly from suppliers (e.g., local upholstery fabric). These POs are **approved by management**.

#### Flow:

```
1. Store Manager creates Draft PO in Odoo → sends to supplier
2. Management (Warehouse Admin or higher) approves the PO
3. Supplier delivers directly to the store's receiving area
4. Store staff confirms receipt via Inventory → Operations → Receipts
5. Stock lands in that store's /Stock location
```

> ⚠️ **Important:** Direct-ship POs MUST be tagged with the correct destination warehouse (store) at creation time. Otherwise, Odoo defaults to Main Warehouse and creates the wrong transfer.

---

## 5. STOCK VALUATION & FIFO

### How Furniture Plus Values Stock

- **Valuation Method:** FIFO (First-In, First-Out) — configured as system default
- **Automated Accounting Entries:** Created when stock moves (invoicing triggers COGS recognition)
- **Cost Tracking:** Per product, per warehouse

### Understanding FIFO in Practice

**Example: Main Warehouse receives DT-4200 (Dining Tables) on three different dates:**

| Batch Date | Qty Received | Unit Cost | Total Value |
|------------|-------------|-----------|-------------|
| June 1 | 10 tables | $800 | $8,000 |
| June 15 | 12 tables | $820 | $9,840 |
| July 1 | 24 tables | $835 | $20,040 |

**If a store needs 25 tables:**

FIFO removes from the *oldest* batch first:
- 10 × $800 = $8,000 (June 1 batch — gone)
- 12 × $820 = $9,840 (June 15 batch — gone)
- 3 × $835 = $2,505 (July 1 batch — partial)

**Total COGS for that transfer: $20,345**

Odoo handles this automatically. Users don't need to calculate it manually — just understand the logic.

### Key Configuration Steps

In Odoo:
1. **Inventory → Configuration → Settings → Products**
2. Set **Product Costing** to *Automated* (for items you want automatic accounting entries)
3. Set **Stock Valuation** to *FIFO*
4. Enable **Automatic Journal Entries** for inventory movements

---

## 6. MULTI-STORE TRANSFERS — MAIN WAREHOUSE TO STORES

### How Replenishment Works

When a store's stock falls below its minimum threshold, Odoo can automatically create an internal transfer request to the main warehouse.

### Min/Max Replenishment Rules — Setup & Explanation

#### What Are Min/Max Rules?

- **Min:** The lowest stock level before replenishment is triggered
- **Max:** The target stock level after replenishment arrives
- When actual stock ≤ Min → Odoo auto-creates a transfer from the source warehouse (usually Main) to this store's warehouse

#### Configuring Min/Max for a Product

1. Open the product form → *Inventory* tab
2. Enable **Reordering Rules**
3. Set:
   - **Min Quantity:** e.g., 5 (trigger reorder when stock hits 5)
   - **Max Quantity:** e.g., 20 (order enough to reach 20 total)
   - **Warehouse:** Which store warehouse this rule applies to
   - **Location:** Usually `/Stock`
   - **Route:** Internal Transfer (from Main Warehouse)
4. Choose: *Automatic* or *Manual* trigger

#### Example: Store #3 Needs Coffee Tables Restocked

```
Product: CT-1500 (Coffee Table, Oak)
Store WH_03 Current Stock: 6 units
Min Threshold: 10
Max Target: 30

Action: System auto-generates Internal Transfer
   - Source: WH_MAIN /Stock
   - Destination: WH_STORE_03 /Stock
   - Quantity: 24 (brings stock from 6 → 30)
   - Status: Draft → Waiting/Pending (awaiting main warehouse picker)
```

#### Auto vs. Manual Replenishment

| Mode | Behavior | When to Use |
|------|----------|-------------|
| **Auto** | Transfer creates itself immediately when stock ≤ min | High-turnover items, well-established products |
| **Manual** | Creates a *request* for review; user clicks "Confirm" | New products, seasonal items, management-controlled items |

> 💡 **Recommendation for FP:** Use **Auto** for established high-sellers (best-selling sofa lines, popular dining sets). Use **Manual** for furniture being tested, seasonal items, or anything over $2,000.

---

## 7. DIRECT SHIP PURCHASES — SUPPLIER TO STORE

### When Direct Shipping Is Used

Furniture Plus stores sometimes need to bypass the main warehouse and receive directly from suppliers. Common scenarios:

- **Custom furniture** ordered by a specific customer (made-to-order)
- **Local fabric/trim supplies** that are impractical to route through Main WH
- **Emergency restocking** where waiting for main warehouse transfer would lose a sale
- **Oversized items** (grand pianos, sectional sofas) better shipped directly from the manufacturer

### Process: Direct Ship PO Approval Workflow

```
Step 1: Store Manager creates a draft Purchase Order
   → Selects correct store warehouse as destination
   → Adds products and quantities

Step 2: Management reviews and approves
   → Goes to Purchases → Vendor Orders → finds draft PO
   → Reviews items, prices, delivery dates
   → Clicks "Confirm" (or sends for approval if multi-level)

Step 3: Supplier ships directly to store address

Step 4: Store staff receives goods
   → Inventory → Operations → Receipts → confirms receipt
   → Stock updates in that store's warehouse only
```

### Critical Rules for Direct Ship

1. ✅ Always verify the **destined warehouse** on the PO before confirming
2. ✅ Management approval required — no unapproved direct-ship POs
3. ✅ Store manager must confirm receipt (cannot auto-confirm high-value items)
4. ❌ Never use direct ship without a confirmed PO (prevents "ghost inventory")

---

## 8. AUTOMATED REPLENISHMENT — MIN/MAX RULES

### How the System Works End-to-End

```
Store A sells products → Stock decreases
    ↓
Stock falls below Min threshold for Product X
    ↓
Odoo creates Internal Transfer automatically (if Auto mode)
    OR
Odoo creates a pending transfer request (if Manual mode)
    ↓
Main Warehouse receives the transfer order
    ↓
Picker picks and packs from WH_MAIN /Stock
    ↓
Transfer ships to Store A → arrives at store reception
    ↓
Store receiver confirms receipt
    ↓
Store A stock increases to Max level (or wherever it lands)
```

### Replenishment Route Configuration

1. Go to **Inventory → Configuration → Routes**
2. Find or create a route: "Main Warehouse → Stores"
3. On each product, set the route under the *Inventory* tab
4. Under *Reordering Rules*, ensure the rule points to the correct source warehouse (Main)

### Replenishment Dashboard

Access via: **Inventory → Dashboard → Replenishment**

This shows:
- Which stores need restocking
- How much they need
- Status of each transfer request (Draft → Confirmed → In Transit → Received)

> 📊 **Pro Tip:** Check this dashboard every morning as part of your opening routine. It's the heartbeat of your multi-store operation.

---

## 9. POINT OF SALE (POS) INTEGRATION

### How POS Affects Inventory

When a sale happens at any Furniture Plus store:

1. Customer purchases items at the POS terminal
2. Odoo **immediately reduces stock** in that store's warehouse
3. If the item was already reserved for a customer order → reservation is consumed
4. If stock drops below min → replenishment may trigger automatically

### CSR Reservation Workflow (No Modify Permissions)

CSRs need to *view* reservations for customers but not change them:

| Task | How to Do It | Permission Level |
|------|-------------|------------------|
| View stock levels across all stores | Inventory → Reporting → Stock Ledger / Dashboard | Read-Only or Inventory User |
| Check reservation status for a customer's order | Sales → Orders → find order → click "Reservations" tab | Inventory User |
| Check reserved locations (e.g., `/Reserve_CustOrders`) | Inventory → Operations → Moves → filter by location | Inventory User |
| Create unreserve? | ❌ NOT ALLOWED for CSRs | Blocked by permissions |

### Reservation Locations Explained

Furniture Plus uses a dedicated **`/Reserve_CustOrders`** location:

```
Main Warehouse / Reserve_CustOrders  → Customer orders not yet delivered
Store WH_05 / Reserve_CustOrders    → Local customer pickups from Store 5
```

When a customer places an order:
1. Sales creates SO → Odoo auto-reserves stock from `/Stock`
2. Stock moves to `/Reserve_CustOrders` (virtual location, not physical)
3. When delivery/pickup happens → stock leaves Reserve and COGS is posted

---

## 10. BACKORDERS & EXCEPTION HANDLING

### What Is a Backorder?

A backorder occurs when the **received quantity doesn't match** what was expected on a transfer or receipt. Examples:

- PO said 50 chairs → supplier delivered 42 → 8 are backordered
- Transfer requested 10 tables → Main WH only has 6 in stock → 4 are pending
- Store manager ordered via min/max for 30 sofas → only 20 available at main → partial transfer

### Configured System Alert (Next Step — See Meeting Notes)

**[Nio Action Item]:** Configure a system alert that notifies users when items are missing during scanning, requiring administrative approval for backorder adjustments.

#### Current Backorder Workflow (until alert is configured):

```
1. Dock worker or picker scans items against the transfer order
2. Received qty < Expected qty → Odoo shows discrepancy popup
3. User clicks "Backorder" to create a partial receipt
4. System prompts: "Confirm backorder for remaining X units?"
5. Admin/Warehouse Manager must approve the backorder via their dashboard
6. Partial stock is received; remainder stays in a pending state
7. When supplier delivers the balance → find the pending transfer and confirm
```

### Approval Levels for Backorders

| Scenario | Who Approves |
|----------|-------------|
| Qty mismatch ≤ 5 units | Store/Warehouse Manager |
| Qty mismatch > 5 units or value > $5,000 | Warehouse Administrator |
| Damaged goods requiring scrap | Inventory Admin (mandatory reason code) |

---

## 11. STOCK RESERVATIONS — CUSTOMER ORDERS

### Understanding Reservations in Furniture Plus

Reservations ensure that a customer's order won't be sold or transferred to someone else while waiting for delivery/pickup.

#### Reservation Flow:

```
Customer places order (Sales / POS / Website)
    ↓
Odoo auto-reserves available stock from the appropriate warehouse
    ↓
Stock status changes from "Available" → "Reserved"
    ↓
Customer is notified of reserved status
    ↓
Upon delivery/pickup: reservation released → stock leaves warehouse
```

#### What CSRs Can and Cannot Do

| Action | Allowed? | How |
|--------|----------|-----|
| View which items are reserved for a customer | ✅ Yes | Sales Order → Reservations tab |
| Check total reserved quantity per product | ✅ Yes | Inventory Dashboard or Stock Report |
| Unreserve stock (release a reservation) | ❌ No | Blocked by role permissions |
| Modify a customer's order quantities | ✅ Yes (if they have Sales rights) | Edit SO before delivery confirmation |

---

## 12. PHYSICAL INVENTORY COUNTS

### Scheduled Inventory Counts — How It Works

Furniture Plus conducts physical counts **per location, assigned to specific users**. This is the primary way to ensure Odoo's virtual stock matches reality.

### Count Process — Step by Step

#### Setup (done once, repeated periodically):

1. **Inventory → Operations → Physical Inventory** → Click *New*
2. Name: e.g., "Store #3 Monthly Count — July 2026"
3. Set the inventory count date/time
4. Select which warehouse(s) to count
5. Optionally filter by specific products, categories, or locations
6. Assign a **Counting User** (the person doing the physical count)

#### Day of the Count:

| Step | Action | Tool |
|------|--------|------|
| 1 | Print count sheets OR use the Barcode app on mobile/tablet | Inventory → Physical Inventory → *Print* or open Barcode app |
| 2 | Walk through the store/warehouse, physically counting each product at each location | Use barcode scanner for speed |
| 3 | Enter counted quantities (or scan barcodes) in Odoo | Barcode app auto-populates; manual entry on count sheets |
| 4 | Submit counts (DO NOT confirm yet!) | Count Status: *Counted* — not yet validated |

#### Manager Review & Validation:

| Step | Action | Who |
|------|--------|-----|
| 1 | Manager reviews submitted counts vs. system quantities | Warehouse Manager / Inventory Admin |
| 2 | Identify and investigate discrepancies | Manager + counting user |
| 3 | Adjust count if warranted OR keep original system qty | Manager approval required for adjustments |
| 4 | Confirm/validate the inventory count | Only **Warehouse Administrator** or designated approver |

> ⚠️ **Golden Rule:** The person who *counts* stock CANNOT be the same person who *validates* the count. This separation prevents fraudulent adjustments and ensures audit integrity.

### Count Frequency — Furniture Plus Standard

| Location Type | Count Frequency | Assigned Role |
|--------------|-----------------|---------------|
| Main Warehouse (all locations) | Monthly (1st week) | Inventory Admin + 2 staff |
| Each Store (/Stock only) | Monthly (aligned with store closing day) | Store Manager + 1 associate |
| /Reserve_CustOrders | Weekly spot check | CSR supervisor |
| /Scrap location | As needed (whenever scrap occurs) | Warehouse Manager |

### Reporting After a Count

After validation, generate:
- **Inventory Adjustment Report** — shows what changed and financial impact
- **Stock Ledger Entry** filter by count date
- Audit trail preserved for accounting/compliance

---

## 13. SCRAP, DAMAGE & RETURNS PROCESSING

### Scrap Process — Removing Damaged Goods from Active Inventory

When furniture arrives damaged, is displayed and dented, or fails QC:

#### Step-by-Step Scrap Workflow:

| Step | Action | Details |
|------|--------|---------|
| 1 | Identify the damaged item in Odoo | Find the product in inventory (by barcode, name, or SKU) |
| 2 | Create a scrap move | **Inventory → Operations → Scrap** → Click *New* |
| 3 | Select the source location (where the damaged item currently sits) | e.g., WH_MAIN /QC_Inspection or WH_STORE_05 /Stock |
| 4 | Select the destination: `/Scrap` | This is a dedicated scrap location per warehouse |
| 5 | Enter the quantity being scrapped | Full quantity — scraps remove 100% of the item from stock |
| 6 | **MANDATORY: Add a reason code** | Options: "Arrival Damage", "Display Damage", "QC Fail", "Customer Return Unsellable" |
| 7 | Confirm/Validate the scrap move | Stock is removed; value is fully written off |

#### Financial Impact of Scraping

- The scrapped item's full cost is removed from inventory asset value
- An accounting entry is automatically created (if automated valuation is enabled)
- The audit trail captures: **who** scrapped it, **when**, **why** (reason code), and the **value impact**

#### Reason Codes Used at Furniture Plus

| Code | When to Use |
|------|-------------|
| `ARRIVAL_DAMAGE` | Item arrived from supplier with damage |
| `DISPLAY_DAMAGED` | Customer-facing display furniture dented/damaged |
| `QC_FAILURE` | Failed quality inspection before stocking |
| `CUST_RETURN_UNSELLABLE` | Customer returned item; too damaged to resell |
| `DISCONTINUED_BATCH` | End-of-line product being retired (not damage) |

---

### Returns Processing (Customer Returning Furniture)

```
1. Customer returns item → create a "Return" on the original Sale Order / Delivery
2. System generates an incoming transfer to receive the returned item
3. Staff receives at the designated return area
4. QC inspection determines: can it go back in stock? or needs to be scrapped?
5a. If sellable → move back to /Stock (or a "Return Inspection" location first)
5b. If unsellable → scrap per the process above (Section 13, Scrap workflow)
```

---

## 14. FLEET MANAGEMENT & DELIVERIES

### Overview

Furniture Plus uses Odoo's Fleet module for truck/driver management and delivery confirmation with **digital signatures**.

### Digital Signature Process — Driver Confirms Delivery

| Step | Action | Tool/Module |
|------|--------|-------------|
| 1 | Delivery Order is ready in Odoo (Inventory → Operations → Deliveries) | Inventory Module |
| 2 | Assign the delivery to a driver & truck (from Fleet module) | Fleet Management → add contractor trucks |
| 3 | Driver picks up goods from warehouse loading dock | Warehouse Picker confirms load on tablet/phone |
| 4 | Driver delivers to customer address | Digital signature collected on mobile device |
| 5 | Customer signs on screen → signature saved to delivery record in Odoo | Signature captured via Odoo's digital sign feature |
| 6 | Delivery status updated to "Done" in Odoo | Auto-updates stock and triggers COGS/Revenue recognition |

### Fleet Management Setup (Next Step — See Meeting Notes)

**[Nio Action Item]:** Add contractor trucks to the fleet management system for delivery tracking.

#### Setup Checklist:
1. **Fleet → Vehicles → New** → Add each truck:
   - License plate, make, model, year, color
   - Assigned driver (if known)
   - Maintenance schedule settings
2. Link vehicles to available drivers in the Fleet module
3. When creating a delivery order, assign the vehicle and driver from dropdowns

---

## 15. BARCODE SCANNING OPERATIONS

### Barcode App Overview

The Odoo Barcode app (mobile/tablet) is used throughout Furniture Plus for:

- **Receiving** goods at dock doors
- **Picking** transfers in the warehouse
- **Physical inventory counts**
- **Internal stock movements** between locations within a warehouse

### Getting Started with Barcodes

1. Ensure products have barcodes (or generate labels from Odoo: **Inventory → Products → Print → Labels**)
2. Install/configure the Barcode app on mobile devices/tablets per warehouse
3. Log in to the Barcode app as a staff member with Inventory User rights or higher

### Common Barcode Workflows

#### Scanning a Receipt at Dock #5 (Main Warehouse)

```
1. Open Barcode app → select "Receipt" operation type
2. Scan or search for the incoming transfer (by PO#, product, or barcode)
3. For each item: scan its barcode → confirm quantity → move to next
4. If mismatch detected → system prompts: "Expected X, Scanned Y"
5. Resolve discrepancy → click *Backorder* or adjust
6. When all items scanned and confirmed → hit *Validate*
7. Stock updated in real-time across the entire Odoo database
```

#### Scanning a Physical Count

```
1. Open Barcode app → select "Physical Inventory" 
2. Select the count (e.g., "Store #3 — July 2026")
3. Navigate to each location and scan products as you find them
4. Enter actual counted quantity for each product
5. Submit when done → goes to manager for review
```

### Barcode Scanner Hardware Evaluation (Future Use Case)

Furniture Plus is evaluating standard barcode scanners (not brand-specific). When purchased:

- Scanners connect via Bluetooth or USB to the tablets/devices running the Barcode app
- Ensure scanner compatibility with Odoo's barcode module (most HID-compatible scanners work)
- Test scan speed and range in your warehouse environment before full deployment

---

## 16. REPORTING & DASHBOARDS

### Key Reports for Furniture Plus Staff

#### Inventory Admin / Warehouse Manager Daily Checks

| Report | Path | Purpose |
|--------|------|---------|
| **Replenishment Dashboard** | Inventory → Dashboard → Replenishment | See which stores need restocking today |
| **Pending Transfers** | Inventory → Operations → Transfers (filter: status = Waiting) | See all pending internal moves between warehouses |
| **Stock Valuation** | Inventory → Reporting → Valuation | Total inventory value per warehouse |
| **Inventory Adjustments** | Inventory → Reporting → Adjustments | Review recent count adjustments and their impact |

#### Store Manager Weekly Checks

| Report | Path | Purpose |
|--------|------|---------|
| **On-Hand by Product** | Inventory → Reporting → On Hand | What's physically in your store right now |
| **Forecasted Quantity** | Inventory → Reporting → Forecasted | Expected stock after pending transfers arrive |
| **Reservations** | Inventory → Operations → Moves (filter: Status = Assigned) | Stock reserved for customer orders |

#### Monthly/Quarterly Reports

| Report | Path | Purpose |
|--------|------|---------|
| **Stock Ledger** | Inventory → Reporting → Stock Ledger | Detailed movement history for auditors |
| **Traceability/Lot Tracking** | Inventory → Reporting → Traceability | Track individual batches/lots through your supply chain |
| **Inventory Performance** | Accounting or custom report | COGS, shrinkage, scrap value trends |

---

## 17. COMMON USE CASES — STEP BY STEP

### Use Case 1: Store #7 Runs Out of Popular Dining Sets — Full Flow

```
PROBLEM: Store #7 has sold its last "DT-4200 Dining Set (6pc)". Only 1 reserved for a customer order.

AUTOMATED RESPONSE:
1. Min/Max rule triggers because stock (0) ≤ min threshold (3)
2. Odoo creates internal transfer request automatically:
   - Source: WH_MAIN → /Stock
   - Destination: WH_STORE_07 → /Stock
   - Quantity: 18 (brings Store #7 from 1 to Max of 19 including the reserved one)

3. Main Warehouse Picker sees the transfer in their dashboard
4. Picker collects 18 dining sets from bulk storage
5. Transfer status changes to "Ready" → shipped to Store #7
6. Store #7 warehouse manager receives at reception → confirms receipt
7. Store #7 stock: 19 dining sets available for sale

If Main WH only has 10 in stock:
→ Backorder created for the remaining 8
→ Backorder requires Admin approval before partial transfer ships
```

### Use Case 2: Direct Purchase — Store #2 Needs Local Upholstery Fabric

```
NEED: Store #2 needs 50 yards of custom fabric for a bespoke order. Not stocked at main warehouse.

FLOW:
1. Store #2 Manager creates PO in Purchases module
   - Supplier: "Local Fabric Supply" (already in Odoo contact database)
   - Destination Warehouse: WH_STORE_02 ← CRITICAL — must be set correctly
   - Quantity: 50 yards, price agreed with supplier
2. Management approves the PO → status = Confirmed
3. Supplier delivers fabric directly to Store #2 receiving area
4. Store staff receives via Inventory → Operations → Receipts in Odoo
5. Stock updated in WH_STORE_02 only — does NOT appear at Main Warehouse
6. COGS and inventory valuation adjusted accordingly

VERIFICATION: 
   - Check stock: Inventory → On Hand → filter by WH_STORE_02 → confirm fabric appears
```

### Use Case 3: Inter-Store Transfer Requested by Manager

```
NEED: Store #4 manager needs to borrow 3 sectional sofas from Store #6 (which has overstock).

FLOW:
1. Store #4 Manager: Inventory → Operations → Internal Transfers → New
   - Source Warehouse: WH_STORE_06
   - Destination Warehouse: WH_STORE_04
   - Product: "SOFA-SEL-3Pc" × 3
2. Transfer status: Draft
3. If approval is required (>50 units or $10K threshold):
   → Warehouse Admin reviews and clicks "Confirm"
4. Store #6 receives notification → picker pulls the 3 sofas
5. Transfer status: Waiting/Ready → shipped to Store #4
6. Store #4 receiver confirms receipt
7. Both stores' stock balances updated automatically

REVERSAL (if needed): Same process, just flip source and destination warehouses.
```

### Use Case 4: Damaged Delivery — Dock Worker Finds Scratched Table

```
SITUATION: Truck arrives at Dock #3 with 20 dining tables. On inspection, 3 have scratched surfaces.

FLOW:
1. Dock worker scans the delivery against the transfer order
2. For the good items (17): scan normally → confirm receipt
3. For damaged items (3): open Inventory → Operations → Scrap
   - Source location: WH_MAIN /Input (where they just landed)
   - Destination: WH_MAIN /Scrap
   - Reason code: ARRIVAL_DAMAGE
   - Confirm scrap move
4. Supplier notified for credit/replace of 3 units
5. Remaining 17 dining tables now in active stock at Main Warehouse

AUDIT TRAIL: The scrap entry records who did it, when, why, and the cost impact.
```

### Use Case 5: Monthly Physical Count at Store #9

```
PREPARATION (Monday morning):
1. Inventory Admin creates new physical inventory: "Store #9 — July 2026"
2. Assign counting users: "Maria (Associate)" and "Carlos (CSR Supervisor)"
3. Print count sheets OR confirm Barcode app is loaded for both devices

COUNT DAY (Thursday after closing):
1. Maria walks through Store #9 with Tablet A (Barcode app) → counts each product
2. Carlos walks through Store #9 with Tablet B → double-checks random sections
3. Both submit counts (Status = Counted, NOT validated yet)

REVIEW (Friday morning):
4. Warehouse Manager reviews: compares Maria's count vs. system quantities
5. Found 1 discrepancy: System shows 8 ottomans; count shows 6
   - Investigation: 2 ottomans were in a backroom that wasn't counted → fixed
6. Warehouse Administrator validates the count → status = Done
7. Stock adjustment posted automatically
8. Audit report generated and filed

RESULT: Odoo stock now matches physical reality for Store #9.
```

---

## 18. TROUBLESHOOTING FAQ

### Q: A product shows "0 on hand" but I know we have some in the back room?
**A:** The item may be in a different location or reserved. Check:
- Inventory → Operations → Moves → filter by product and status = Reserved
- Try searching all locations, not just `/Stock` (use the location dropdown)

### Q: A transfer isn't triggering even though stock is below min?
**A:** Verify:
1. The reordering rule is **enabled** (check the checkbox on the rule)
2. The rule's warehouse matches the product's current warehouse
3. The product's route allows replenishment from the source warehouse
4. Minimum quantity is set correctly (not 0 or blank)

### Q: Why can't I unreserve a customer order?
**A:** Your user role doesn't have unreserve permissions. Only Warehouse Administrators and Inventory Managers can release reservations. CSRs can *view* but not modify — this is intentional to protect customer orders.

### Q: A delivery was confirmed but stock didn't update?
**A:** Check:
1. Was the correct warehouse selected on the delivery order?
2. Is there a QC check step blocking validation? (Inventory → Configuration → Settings → Quality)
3. Were there location issues? (destination location might be locked or inactive)

### Q: I accidentally scrapped too many items — can I reverse it?
**A:** No, scrap moves cannot be reversed directly. To fix:
1. Create a new Receipt/purchase for the damaged item from the supplier
2. Add a note in the inventory adjustment history explaining the correction
3. Report this to your Warehouse Admin — they'll log the discrepancy

### Q: How do I see which store has the most stock of a product?
**A:** 
1. Open the product form → look at "On Hand" for each warehouse listed
2. Or go to Inventory → Reporting → On Hand → filter by product → see the full list
3. Or use the Barcode app's cross-warehouse search function

### Q: Can I temporarily stop auto-replenishment for a product?
**A:** Yes — open the product's reordering rule and **uncheck "Enable"** on that specific rule. The rule remains saved; just paused. Remember to re-enable it when appropriate.

---

## APPENDIX A: QUICK REFERENCE — KEY NAVIGATION PATHS

| Task | Odoo Menu Path |
|------|---------------|
| Create a receipt | Inventory → Operations → Receipts → New |
| Create an internal transfer | Inventory → Operations → Transfers → New |
| Create a scrap move | Inventory → Operations → Scrap → New |
| View stock levels | Inventory → Reporting → On Hand |
| Set up min/max rules | Product Form → Inventory Tab → Reordering Rules |
| View reservations | Sales Order → Reservations tab OR Inventory → Operations → Moves (filter: Assigned) |
| Schedule a physical count | Inventory → Operations → Physical Inventory → New |
| View transfer dashboard | Inventory → Dashboard |
| Assign vehicle/driver to delivery | Delivery Form → Fleet/Vehicle dropdown |
| Print barcode labels | Product Form → Action → Print → Labels |
| Configure routes | Inventory → Configuration → Routes |

---

## APPENDIX B: ODOO 19 — NEW/CHANGED FEATURES RELEVANT TO FURNITURE PLUS

| Feature | What Changed in Odoo 19 | Impact on FP |
|---------|------------------------|--------------|
| **Inventory Dashboard** | Redesigned, more drill-down capable | Easier daily checks for replenishment and pending transfers |
| **Barcode App UI** | Improved mobile touch interface | Faster scanning at dock doors and during counts |
| **Quality Module** | Integrated into Inventory (no separate install) | QC steps can be added to any operation type |
| **Fleet Module** | Enhanced with maintenance scheduling | Better tracking of contractor trucks and delivery assignments |
| **Multi-Warehouse Routing** | More intuitive route configuration | Setting up main-to-store replenishment is simpler |

---

## APPENDIX C: UPCOMING / FUTURE CONFIGURATION ITEMS (From Meeting Notes)

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Backorder validation alert system | ⏳ Pending | Nio | System alert when items are missing during scanning; requires admin approval |
| Fleet management — add contractor trucks | ⏳ Pending | Nio | Add vehicles to Odoo Fleet module for delivery tracking |
| Inventory donation use case | 📋 Future session | FP Team + Nio | To be designed in upcoming sessions |
| Temporary stock loaning workflow | 📋 Future session | FP Team + Nio | To be designed in upcoming sessions |
| Audit configuration | 📋 Future session | FP Team + Nio | To be designed in upcoming sessions |
| Barcode scanner hardware evaluation | 🔍 In progress | FP Team | Evaluating feasibility of company-brand scanners |

---

*— End of Furniture Plus Odoo 19 Inventory Training Manual —*  
*Version 1.0 | July 2026 | Prepared by Nio Digital (Functional Consultant Trainer)*  
