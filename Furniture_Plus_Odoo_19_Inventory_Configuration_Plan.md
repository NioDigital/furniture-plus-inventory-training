# 📋 Furniture Plus — Odoo 19 Inventory Configuration Plan

**Prepared by:** Nio Digital  
**Platform:** Odoo 19  
**Date:** July 13, 2026  
**Source:** Meeting Notes — POS & Sales Stimulation Training (July 1, 2026)

---

## Table of Contents

1. [Meeting Notes Analysis — What the Client Told Us](#1-meeting-notes-analysis--what-the-client-told-us)
2. [Configuration Checklist — Step-by-Step Setup Tasks](#2-configuration-checklist--step-by-step-setup-tasks)
3. [Prioritized Task List for Nio Discussions](#3-prioritized-task-list-for-nio-discussions)
4. [Prioritized Task List for The Group (Furniture Plus)](#4-prioritized-task-list-for-the-group-furniture-plus)
5. [Implementation Sequence — Recommended Order](#5-implementation-sequence--recommended-order)

---

## 1. Meeting Notes Analysis — What the Client Told Us

This document maps every topic from the July 1, 2026 POS & Sales Stimulation Training meeting to specific Odoo 19 configuration steps. Each note has been cross-referenced with our existing inventory setup and translated into actionable configuration tasks.

### Note Topics Mapped to Configuration Areas

| Meeting Note Topic | What It Means | Configuration Area in Odoo 19 |
|-------------------|---------------|-------------------------------|
| **Scanning of items at customer locations** | Tracking begins when stock is consumed/sold at the store level, triggering replenishment alerts | Inventory → Products → Reordering Rules |
| **Sales orders trigger replenishment requests when stock falls below thresholds** | Min/Max rules need to be configured for ALL product variants across ALL stores | Inventory → Configuration → Reordering Rules |
| **Replenishment rules link product variants to specific suppliers and warehouses** | Each variant needs a supplier, lead time, and target warehouse defined | Purchase → Vendor Pricelists & Reorder Rules |
| **PO confirmation generates automated receipts** | When a PO is confirmed, Odoo creates the Receipt — this is default behavior but needs verification | Purchase Configuration → Automation |
| **Procurement team manages PO processes with admin approval gates** | Need multi-level approval workflow on POs above certain thresholds | Settings → Purchase → Approval Rules |
| **Delivery locations and routes require manual specification on sales orders** | Default delivery rules exist, but exceptions need override capability — either through delivery methods or custom fields | Sales → Delivery Methods + Routing |
| **Dashboard optimization for direct viewing of delivery destinations in list views** | Need customized kanban/list views per store that show delivery status at a glance | Inventory → Configuration → Views + Studio |
| **Automated email notifications and AI-driven field checks for credit history and balances on SOs** | Sales orders need to integrate with Accounting for customer credit checks; automated alerts on risky orders | Sales/Accounting Integration |
| **Package quantity units (pack-of-5 configurations) validated for inventory tracking** | Product variants may have multi-unit pack configs — need proper unit of measure setup | Inventory → Products → Units of Measure |
| **Sales orders attach to incoming POs on a first-come, first-served basis** | This is Odoo's default reservation logic, but needs testing and possibly custom rules for priority orders | Inventory → Routes & Reservation Strategy |
| **Inventory reservation system uses incoming stock to fulfill open sales orders** | Forecasting formula: on-hand + incoming − outgoing = forecasted; needs route configuration to allow "buy now" fulfillment | Inventory → Routing Rules |
| **Forecast formula calculates availability: on-hand + incoming − outgoing** | This is the standard Odoo forecasting — needs verification of correct product category routing | Inventory → Reports → Forecast |
| **Master production schedule module for annual purchase planning** | MRP (Manufacturing) integration needed to support seasonal/historical-based purchasing plans | Inventory → MRP (Manufacturing) Module |
| **New stock locations configurable within existing warehouse structures** | Additional internal locations needed (e.g., "Damage Holding," "QC Check," "Seasonal Storage") | Inventory → Warehouses → Locations |
| **Damaged stock processing requires manual adjustments — credit inventory, debit damage accounts** | Custom scrap/inventory adjustment process with dedicated accounting entries | Accounting + Inventory Integration |
| **Receipt transfers modifiable by canceling draft and updating configurations** | Draft PO/Receipt editing workflow — needs staff training or custom auto-edit permissions | Purchase → Draft PO Editing Policy |

---

## 2. Configuration Checklist — Step-by-Step Setup Tasks

### TASK 1: Fix Product Errors ✅ (PRIORITY — MUST DO FIRST)

**What the notes say:**
> "[The group] Fix Product Errors: Correct product configuration settings if errors appear in the system. Resolve identified issues by accessing the product view."

**Configuration Steps:**

1. **Audit all products** in Odoo:
    - Go to **Inventory → Products → Products**
    - Review every product for: correct name, category, vendor, cost price, sale price, unit of measure, default location
2. **Fix any missing or incorrect fields**:
    - Ensure each product has a **Category** assigned (e.g., "Furniture — Living Room," "Lighting")
    - Verify **Vendor/Supplier** is set on every product that's purchased
    - Check **Unit of Measure** — all quantities should use the correct UoM (each, pack of 5, pallet, etc.)
3. **Product Variants**:
    - For products with attributes (color, size, material), ensure variants are properly configured
    - Verify each variant has its own min/max levels once Reorder Rules are set up

**Deliverable:** Clean product catalog — no errors in the Product view. No further configuration can proceed until this is done.

---

### TASK 2: Configure Min/Max Replenishment Rules for All Products ✅ (HIGH PRIORITY)

**What the notes say:**
> "[The group] Configure Replenishment Rules: Add replenishment rules for all product variants within the inventory system. Link each variant to the correct supplier and warehouse."

**Configuration Steps:**

1. **Go to Inventory → Configuration → Reordering Rules → Create**
2. **For each product (or product category)**, define:
    - **Minimum Quantity**: The reorder trigger point (e.g., 5 sofas)
    - **Maximum Quantity**: How much stock should be held at maximum (e.g., 20 sofas)
    - **Whichever is satisfied first**: Min, Max, or Both
    - **Supply Method**: Buy (from vendor), Take From Stock (warehouse), Produce (manufacture), or Take From Another Warehouse (internal transfer)
3. **Link to Supplier**:
    - On the product form, set the primary vendor
    - In the reorder rule, link to the correct warehouse location
4. **Set up per-store rules** for your 10+ stores:
    - Each store needs its own min/max based on historical sales data
    - A high-traffic store like San Fernando may need higher minimums than a smaller branch

**Deliverable:** Every product variant has a min/max rule. When stock falls below minimum, a purchase request or internal transfer is automatically generated.

---

### TASK 3: Configure PO Approval Gates ✅ (HIGH PRIORITY)

**What the notes say:**
> "PO confirmation generates automated receipts to track incoming goods."
> "Procurement team manages PO processes with admin approval gates required for specific actions."

**Configuration Steps:**

1. **Go to Settings → Purchase → Confirm Purchase Orders Automatically**:
    - By default, Odoo creates a Receipt when a PO is confirmed — verify this is working correctly
    - Decide whether you want auto-confirmation or manual review before each PO
2. **Set up Multi-Level Approval (for POs above certain amounts)**:
    - Go to **Purchase → Configuration → Approval Rules**
    - Create rules like:
        - PO < $1,000 → Store Manager approves
        - PO $1,000–$5,000 → Warehouse Manager + Finance Manager approve
        - PO > $5,000 → All-stakeholder approval required
3. **Test the flow**: Create a test PO above your threshold and verify it routes to the correct approvers before confirmation.

**Deliverable:** POs automatically generate receipts when confirmed. Any PO exceeding configured thresholds requires admin/management approval before it can be confirmed.

---

### TASK 4: Set Up Delivery Routing & Override Capability ✅ (MEDIUM PRIORITY)

**What the notes say:**
> "Delivery locations and routes require manual specification on sales orders when deviating from default settings."

**Configuration Steps:**

1. **Go to Sales → Configuration → Delivery Methods**:
    - Create a default delivery method for each store (e.g., "Store Pickup," "Local Delivery")
    - Define the **Carrier** (your own fleet or external — e.g., Courier, Customer Pick Up)
2. **Set up Delivery Routes** in Inventory:
    - Go to **Inventory → Configuration → Routes**
    - Create store-specific delivery routes that override defaults when needed
    - Example: "Store #3 Local Delivery" route overrides default and specifies a custom carrier
3. **Manual Override on Sales Orders**:
    - When creating a SO, the user can change the **Delivery Method** field (if they have write access)
    - Alternatively, create custom fields or use Odoo Studio to add a "Special Delivery Notes" field for exceptions

**Deliverable:** Default delivery routes work automatically. Store managers and CSRs can manually specify different delivery locations/routes on individual sales orders when needed.

---

### TASK 5: Build Per-Store Dashboard Views ✅ (MEDIUM PRIORITY)

**What the notes say:**
> "[Nio Discussions] Configure Store Views: Create separate dashboard views for each store location to reduce visual clutter and improve inventory monitoring."

**Configuration Steps:**

1. **Inventory → Configuration → Views**:
    - Use Odoo Studio or write custom XML view definitions per warehouse
    - Create a **store-specific list view** showing only products relevant to that store
2. **Customize the views to show**:
    - Product name, category, free qty, reserved qty, forecasted qty
    - Delivery destination (linked to sales orders)
    - Pending replenishment requests
    - Incoming purchase order status
3. **Add Kanban cards** for a visual dashboard:
    - Cards showing low-stock items at the store level
    - Color-coded stock indicators (red = below min, yellow = near min, green = ok)
4. **Use Odoo Studio** (if licensed) to quickly build these views without code:
    - Open any inventory view → "Edit View" → add filters for the current store
    - Save as a custom view tied to that warehouse

**Deliverable:** Each store has its own clean dashboard showing only relevant data — no clutter from other stores. Real-time visibility into stock levels, pending orders, and delivery destinations.

---

### TASK 6: Configure Email Notifications & Credit Checks ✅ (MEDIUM PRIORITY)

**What the notes say:**
> "Automated email notifications and AI-driven field checks for credit history and balances integrated into sales orders."

**Configuration Steps:**

1. **Enable Automated Sales Order Emails**:
    - Go to **Sales → Settings → Emails**
    - Enable "Send confirmation emails automatically" on confirmed SOs
    - Customize the email template (Sales → Settings → Email Templates)
2. **Customer Credit History Checks** (via Accounting):
    - When creating a sales order, Odoo can show customer payment history via the **Accounting** module
    - Configure **Customer Credit Limits** per customer in the Partner form:
        - Go to the Customer contact → Sales & Purchases tab → set "Credit Limit"
        - System will warn/block orders exceeding their limit
3. **AI-Driven Field Checks** (Odoo 19 features):
    - Odoo 19 includes AI-assisted field validation — this may require enabling via:
        - **Settings → General Settings → Enable AI Features** (if available in your edition)
        - Configure warning rules based on customer balance, overdue invoices, or payment history
4. **Custom Alert Workflow**:
    - If AI credit checks aren't fully configured, create a custom action that triggers an alert email to Finance whenever a sales order is created for a customer with outstanding balances

**Deliverable:** Automated emails sent when SOs are confirmed. Sales team gets warnings or blocks on orders exceeding customer credit limits.

---

### TASK 7: Configure Package Quantity Units (Pack-of-5, etc.) ✅ (LOW-MEDIUM PRIORITY)

**What the notes say:**
> "Package quantity units, including pack-of-5 configurations, validated for inventory tracking and purchasing."

**Configuration Steps:**

1. **Go to Inventory → Configuration → Settings**:
    - Ensure **"Units of Measure"** are enabled (show in top-right settings toggle)
2. **Define UoM Categories**:
    - Create a category like "Furniture Units" with base unit = "Each"
    - Add conversions: Pack of 5, Pallet, Case
3. **On Each Product**, set the correct UoM:
    - Standard item: Unit of Measure = "Each"
    - Pack-of-5 cushion sets: UoM = "Pack of 5"
    - Bulk order items (e.g., carpet by linear foot): UoM = "Linear Meter" or "Square Meter"
4. **Verify Inventory Tracking**:
    - When a pack-of-5 is purchased from vendor, the system should track 5 individual units in stock
    - Test: Create a PO for "Cushion Pack of 5" (qty: 10) → confirm receipt → verify 50 cushions appear in stock

**Deliverable:** Multi-unit products are tracked correctly in inventory. A pack-of-5 purchase increases individual item stock by the correct multiplier.

---

### TASK 8: Configure Reservation Logic — FCFS + Incoming Stock ✅ (MEDIUM PRIORITY)

**What the notes say:**
> "Sales orders automatically attach to incoming purchase orders on first-come, first-served basis."
> "Inventory reservation system utilizes incoming stock to fulfill open sales orders."
> "Forecast formula calculates stock availability using on-hand plus incoming minus outgoing values."

**Configuration Steps:**

1. **Verify Odoo's default reservation behavior**:
    - By default, Odoo reserves stock in FIFO (first-in-first-out) and FCFS order
    - When a PO is received, stock becomes available immediately and the system assigns it to pending sales orders
2. **Set the correct Reservation Strategy** on products:
    - Go to each Product → **Inventory tab**
    - Set "Replenish" method: either Buy or Manufacture
    - The system will automatically link incoming POs to SOs based on demand
3. **Enable Multi-Location Reservation**:
    - If stock exists across multiple locations, Odoo reserves from the nearest/most appropriate location
4. **Test the Forecast Formula**:
    - Open a product → Check "Forecasted Quantity" field
    - Verify: **On Hand + Incoming Transfers − Outgoing Deliveries = Forecasted**
5. **Configure Routes** for advanced reservation behavior:
    - Go to Inventory → Configuration → Routes
    - For the "Buy" route, ensure it triggers purchase orders automatically (via reorder rules)

**Deliverable:** Sales orders are automatically matched with incoming stock in FCFS order. The forecast formula correctly reflects on-hand + incoming − outgoing.

---

### TASK 9: Set Up Master Production Schedule (MRP Integration) ✅ (FUTURE/ADVANCED)

**What the notes say:**
> "Master production schedule module supports annual purchase planning based on historical data and seasonal trends."

**Configuration Steps:**

1. **Install the MRP (Manufacturing) Module**:
    - Go to Apps → Search "MRP" or "Manufacturing" → Install
    - For a furniture store, you may not need full manufacturing — but the MRP module adds purchasing planning capabilities
2. **Enable Procurement Management**:
    - Go to **Inventory → Configuration → Settings**
    - Enable "Master Production Schedule" (MPS) if available in Odoo 19
3. **Define Purchase Plans**:
    - Use historical data to set seasonal purchase targets for each product
    - Configure monthly/quarterly procurement plans based on sales trends
4. **Integrate with Reordering Rules**:
    - Link MPS forecasts to reorder rules so that planned quantities influence min/max thresholds seasonally

**Deliverable:** Annual purchasing plans can be created and tracked. Seasonal trends automatically inform reorder thresholds.

---

### TASK 10: Configure New Stock Locations ✅ (LOW PRIORITY)

**What the notes say:**
> "New stock locations configurable within existing warehouse structures."

**Configuration Steps:**

1. **Go to Inventory → Configuration → Warehouses**:
    - For each warehouse (Main WH + all 10+ stores), click into the warehouse configuration
2. **Add internal stock locations as needed**:
    - Common new locations for Furniture Plus:
        - **Damage Holding** — damaged goods waiting for disposal/scrap
        - **QC Check** — items awaiting quality inspection before being put in active stock
        - **Seasonal Storage** — seasonal furniture (e.g., outdoor sets stored off-season)
        - **Consignment** — items held on behalf of external parties
3. **Set up Put-Away Rules** for each new location:
    - When goods arrive from a vendor, route them through QC Check first
    - Items passing QC go to Bulk Storage; failing items go to Damage Holding
4. **Update Reordering Rules** if needed:
    - Some reorder rules may need to target specific locations (e.g., replenish from Seasonal Storage for summer items)

**Deliverable:** All necessary internal stock locations exist within each warehouse structure with proper routing.

---

### TASK 11: Configure Damaged Stock Processing — Credit/Debit Accounting Entries ✅ (MEDIUM PRIORITY)

**What the notes say:**
> "Damaged stock processing requires manual adjustments by crediting inventory and debiting damage stock accounts."

**Configuration Steps:**

1. **Set up Inventory Adjustment Accounts**:
    - Go to **Accounting → Configuration → Settings**
    - Ensure "Inventory Valuation" is set to **Automated** (perpetual)
2. **Configure Stock Valuation Accounts**:
    - For each product category, define:
        - **Stock Input Account** — where incoming stock value goes
        - **Stock Output Account** — where outgoing stock value comes from
        - **Stock Valuation Account** — the main inventory asset account
3. **Create a Damage/Loss Expense Account**:
    - In Chart of Accounts, create: "Inventory Damage & Loss" (expense account)
4. **Configure Scrap Process**:
    - Go to Inventory → Operations → Scrap → Create
    - When you scrap items, Odoo should auto-generate:
        - **Credit** the inventory asset account (reduce stock value)
        - **Debit** the damage/loss expense account
5. **Test the flow**: Create a test scrap for 1 damaged item and verify the accounting entries are correct in Accounting → Journal Entries.

**Deliverable:** Scrapping damaged goods automatically generates proper credit/debit journal entries: inventory account credited (reduced), damage expense account debited (increased).

---

### TASK 12: Configure Draft PO/Receipt Editing Permissions ✅ (LOW PRIORITY)

**What the notes say:**
> "Receipt transfers modifiable by canceling draft and updating configurations."

**Configuration Steps:**

1. **Decide who can edit draft POs**:
    - By default in Odoo, users with write access on Purchase Orders can modify them while in Draft status
    - Once confirmed, edits require cancellation → draft → re-edit → confirm again
2. **Configure Access Rights**:
    - Go to **Settings → Users & Companies → Users**
    - For each user, assign appropriate **Purchase** access:
        - Procurement Team → read/write on POs
        - Store Managers → read/write only on their store's POs (if multi-company or via record rules)
3. **Set up automated cancel-and-reedit workflow**:
    - If someone needs to change a confirmed PO, the process is:
        1. Click "Cancel" on the PO → it becomes Draft Cancelled
        2. Edit the draft version
        3. Confirm again (triggering approval gate if configured)
4. **Train staff** on when to edit in draft vs. when to cancel and re-confirm.

**Deliverable:** Staff can modify draft POs directly. Confirmed POs require a cancellation/re-edit workflow with proper audit trail.

---

## 3. Prioritized Task List for Nio Discussions

These are the configuration tasks **Nio Digital needs to implement** on the Odoo system:

| # | Task | Priority | Est. Effort | Dependencies |
|---|------|----------|-------------|--------------|
| 1 | Fix Product Errors | 🔴 Critical | 1–2 hours | None — do first |
| 2 | Configure Min/Max Replenishment Rules for ALL Products | 🔴 Critical | 4–8 hours | After product errors are fixed |
| 3 | Set Up PO Approval Gates (Admin Approval Workflows) | 🟠 High | 2–3 hours | Depends on Task #1 |
| 4 | Configure Per-Store Dashboard Views (Inventory Monitoring) | 🟡 Medium | 3–5 hours | Needs Odoo Studio or custom dev |
| 5 | Configure Delivery Routing & Override Capability | 🟡 Medium | 2–3 hours | After warehouses are set up |
| 6 | Set Up Automated SO Emails + Credit Checks | 🟡 Medium | 1–2 hours | Requires Accounting module configured |
| 7 | Configure Package Quantity Units (Pack-of-5) | 🟢 Low-Medium | 1 hour | Depends on UoM module enabled |
| 8 | Configure FCFS Reservation Logic + Forecast Formula Validation | 🟡 Medium | 2–3 hours | Testing-heavy — verify after all rules are set |
| 9 | Set Up MRP / Master Production Schedule Module | 🔵 Future/Advanced | 3–5 hours | Needs historical sales data loaded |
| 10 | Configure New Stock Locations (Damage, QC, Seasonal) | 🟢 Low-Medium | 1–2 hours | After warehouses are structured |
| 11 | Configure Damaged Stock Accounting Entries (Credit/Debit) | 🟡 Medium | 2 hours | Requires accounting accounts set up |
| 12 | Configure Draft PO Editing Permissions | 🟢 Low | 30 min–1 hour | — |

---

## 4. Prioritized Task List for The Group (Furniture Plus)

These are the **operational tasks** that Furniture Plus staff need to perform:

| # | Task | Who Does It | Frequency |
|---|------|-------------|-----------|
| A | **Fix Product Errors** — Review and correct product settings in Odoo | All Store Managers + Warehouse Manager | One-time audit, then as needed |
| B | **Review Purchase Requests Daily** — Check the list every morning; verify delivery locations are assigned correctly | Procurement Team / Management | Daily (every morning) |
| C | **Configure Replenishment Rules** — Add min/max for ALL product variants, link each to correct supplier and warehouse | Warehouse Manager + Nio Digital support | One-time setup + ongoing maintenance |
| D | **Train Staff on PO Approval Gates** — Procurement team must understand when admin approval is needed | Store Managers → Staff | Before go-live of PO workflows |

---

## 5. Implementation Sequence — Recommended Order

Here's the recommended order to implement everything, to avoid configuration conflicts:

### Phase 1 — Foundation (Week 1)
1. **Fix Product Errors** ✅ (all products must be clean before anything else)
2. **Configure Package Quantity Units** (UoM setup — simple but foundational)
3. **Configure New Stock Locations** (Damage, QC, Seasonal — structure the warehouses)

### Phase 2 — Core Operations (Week 2)
4. **Configure Min/Max Replenishment Rules** (the heart of the system — do this before day-to-day use)
5. **Set Up PO Approval Gates** (procurement workflow must be ready for daily operations)
6. **Configure Damaged Stock Accounting Entries** (ensure scrap processes work properly from day one)

### Phase 3 — Visibility & Automation (Week 3)
7. **Build Per-Store Dashboard Views** (reduce clutter, improve monitoring — important but not urgent)
8. **Configure Delivery Routing & Override Capability** (enable flexible delivery options)
9. **Validate FCFS Reservation Logic + Forecast Formula** (test everything works end-to-end)
10. **Set Up Automated SO Emails + Credit Checks** (sales team gets alerts and credit warnings)

### Phase 4 — Advanced Planning (Week 4+)
11. **Configure MRP / Master Production Schedule** (seasonal/historical-based purchasing planning — advanced feature)
12. **Configure Draft PO Editing Permissions** (fine-tune staff access levels after system is live)

---

## Cross-Reference: Meeting Notes → Configuration Tasks

This section maps each specific note from the meeting to the configuration task number above, so you can trace any requirement back to an action item.

| Meeting Note | Config Task(s) |
|--------------|---------------|
| "Scanning of items occurs at customer locations to initiate tracking" | #2 (Replenishment Rules trigger on stock level changes) |
| "Sales orders trigger replenishment requests when stock falls below defined thresholds" | #2 (Min/Max rules), #8 (FCFS reservation logic) |
| "Replenishment rules link product variants to specific suppliers and warehouses" | #2 (link each variant → supplier + warehouse in reorder rule) |
| "PO confirmation generates automated receipts to track incoming goods" | #3 (verify auto-receipt behavior on PO confirm) |
| "Procurement team manages PO processes with admin approval gates required for specific actions" | #3 (multi-level approval rules), #12 (draft edit permissions) |
| "Delivery locations and routes require manual specification on sales orders when deviating from default settings" | #4 (delivery methods + routing override), #5 (per-store dashboard shows delivery dest) |
| "Dashboard optimization enables direct viewing of delivery destinations within list views" | #5 (custom per-store views showing SO delivery destination) |
| "Automated email notifications and AI-driven field checks for credit history and balances integrated into sales orders" | #6 (SO emails + customer credit limit warnings) |
| "Package quantity units, including pack-of-5 configurations, validated for inventory tracking and purchasing" | #7 (UoM setup — pack-of-5, pallet, etc.) |
| "Sales orders automatically attach to incoming purchase orders on first-come, first-served basis" | #8 (FCFS reservation via standard Odoo behavior + routes) |
| "Inventory reservation system utilizes incoming stock to fulfill open sales orders" | #8 (verify forecast = on-hand + incoming − outgoing) |
| "Forecast formula calculates stock availability using on-hand plus incoming minus outgoing values" | #8 (validate the math in Forecasted Qty field) |
| "Master production schedule module supports annual purchase planning based on historical data and seasonal trends" | #9 (MRP module installation + procurement plans) |
| "New stock locations configurable within existing warehouse structures" | #10 (add Damage Holding, QC Check, Seasonal Storage locations per WH) |
| "Damaged stock processing requires manual adjustments by crediting inventory and debiting damage stock accounts" | #11 (automated credit/debit journal entries on scrap/adjustment) |
| "Receipt transfers modifiable by canceling draft and updating configurations" | #12 (define who can edit drafts vs. confirmed POs) |

---

*End of Configuration Plan — Furniture Plus Odoo 19 Inventory Setup*
*Nio Digital | July 2026*
