"""Hire Purchase Contract model.

The active contract is created when goods are delivered and all
activation gates pass (Table 20, DEL-004). It holds:
 - The contractual receivable (gross HP price)
 - Unearned finance income (to be recognised over time)
 - Payment schedule (contractual + accounting lines)
 - Statutory tracking (70% threshold, qualifying paid amount)
 - Ownership status (Seller Owned until ownership transfer)

See Tables 28-30, 42-50, 56-60, 76.
"""

from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpContract(models.Model):
    _name = 'hp.contract'
    _description = 'Hire Purchase Contract'
    _order = 'name desc'

    # ── Core identification ────────────────────────────────────────
    name = fields.Char(
        string='Contract Reference', required=True, copy=False, readonly=True, default='/',
    )
    application_id = fields.Many2one(
        'hp.application', string='Application', readonly=True, ondelete='restrict',
    )
    plan_id = fields.Many2one('hp.plan', string='Hire Purchase Plan', readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', related='application_id.partner_id', store=True,
    )

    # ── Pricing (snapshot at activation) ───────────────────────────
    cash_price_excl_vat = fields.Float(string='Cash Price excl. VAT')
    vat_amount = fields.Float(string='VAT Amount')
    cash_price_incl_vat = fields.Float(string='Cash Price incl. VAT')
    deposit_amount = fields.Float(string='Deposit Amount')
    trade_in_credit = fields.Float(string='Trade-in Credit')
    amount_financed = fields.Float(string='Amount Financed')
    finance_charge = fields.Float(string='Finance Charge')
    installation_charge = fields.Float(string='Installation Charge')
    other_charges = fields.Float(string='Other Charges')
    statutory_hp_price = fields.Float(
        string='Statutory HP Price',
        help='Total required to complete purchase per the published Act '
             '(excludes penalties, damages, installation charges).',
    )
    total_customer_amount = fields.Float(
        string='Total Customer Amount',
        help='All contractual amounts including separately identified charges and taxes.',
    )

    # ── Ownership & delivery ───────────────────────────────────────
    ownership_status = fields.Selection([
        ('seller_owned', 'Seller Owned'),
        ('transfer_pending', 'Transfer Pending'),
        ('transferred', 'Transferred'),
    ], string='Ownership Status', default='seller_owned')
    delivery_date = fields.Date()
    activation_date = fields.Date()
    ownership_transfer_date = fields.Date()

    # ── Schedule status ────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('payment_due', 'Payment Due'),
        ('grace_period', 'Grace Period'),
        ('in_arrears', 'In Arrears'),
        ('promise_to_pay', 'Promise to Pay'),
        ('restructure_review', 'Restructure Review'),
        ('statutory_notice_required', 'Statutory Notice Required'),
        ('statutory_notice_active', 'Statutory Notice Active'),
        ('legal_review', 'Legal Review'),
        ('court_action_required', 'Court Action Required'),
        ('voluntary_termination', 'Voluntary Termination'),
        ('repossession_approved', 'Repossession Approved'),
        ('repossessed_returned', 'Repossessed or Returned'),
        ('settled', 'Settled'),
        ('ownership_transferred', 'Ownership Transferred'),
        ('written_off', 'Written Off'),
    ], string='Status', default='draft', index=True)

    # ── Statutory tracking (Table 35, LEG-004 to LEG-006) ──────────
    qualifying_paid_amount = fields.Float(
        string='Qualifying Paid Amount',
        help='Deposit + approved non-cash credits + payments/tenders by '
             'customer or guarantor towards HP price.',
    )
    statutory_paid_percentage = fields.Float(
        string='Statutory Paid %', compute='_compute_statutory_percentage', store=True,
    )
    amount_to_70_percent = fields.Float(
        string='Amount to 70%',
        help='Maximum of zero and 70% of statutory HP price less qualifying paid.',
    )

    # ── Accounting snapshots ───────────────────────────────────────
    gross_receivable = fields.Float(string='Gross Receivable')
    unearned_finance_income = fields.Float(string='Unearned Finance Income')
    loss_allowance = fields.Float(string='Loss Allowance')
    net_receivable = fields.Float(
        string='Net Receivable', compute='_compute_net_receivable', store=True,
    )

    # ── Accounting framework ───────────────────────────────────────
    accounting_framework = fields.Selection([
        ('full_ifrs', 'Full IFRS'),
        ('ifrs_smes', 'IFRS for SMEs'),
    ], string='Accounting Framework')

    effective_rate = fields.Float(
        string='Effective Periodic Rate (%)', digits=(12, 8),
    )

    # ── Related records ────────────────────────────────────────────
    schedule_line_ids = fields.One2many('hp.schedule.line', 'contract_id', string='Schedule Lines')
    agreement_ids = fields.One2many('hp.agreement', 'contract_id', string='Agreements')
    case_ids = fields.One2many('hp.case', 'contract_id', string='Collection Cases')

    # ── Company & currency ─────────────────────────────────────────
    company_id = fields.Many2one('res.company', required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # ── Notes & audit ──────────────────────────────────────────────
    note = fields.Text()
    scheduled_next_due_date = fields.Date(string='Next Due Date')
    overdue_amount = fields.Float(string='Overdue Amount')

    # ── Constraints ────────────────────────────────────────────────
    @api.constrains('statutory_hp_price', 'finance_charge')
    def _check_statutory_price(self):
        for rec in self:
            if rec.statutory_hp_price <= 0:
                raise ValidationError(_('Statutory HP price must be positive.'))

    # ── Computed fields ────────────────────────────────────────────
    @api.depends('qualifying_paid_amount', 'statutory_hp_price')
    def _compute_statutory_percentage(self):
        for rec in self:
            if rec.statutory_hp_price > 0:
                pct = (rec.qualifying_paid_amount / rec.statutory_hp_price) * 100
                rec.statutory_paid_percentage = min(pct, 999.99)
            else:
                rec.statutory_paid_percentage = 0.0

    @api.depends('gross_receivable', 'unearned_finance_income', 'loss_allowance')
    def _compute_net_receivable(self):
        for rec in self:
            rec.net_receivable = rec.gross_receivable - rec.unearned_finance_income - rec.loss_allowance

    # ── Schedule generation (Table 29, SCH-001 to SCH-006) ────────
    @api.model
    def _generate_schedule_lines(self, contract):
        """Generate contractual and accounting schedule lines.

        Table 29: SCH-001 (contractual), SCH-002 (accounting),
                  SCH-004 (weekends/holidays), SCH-005 (rounding).
        """
        plan = contract.plan_id
        if not plan or not plan.finance_charge_rate:
            # Zero-finance plan (e.g. 3 Months Same as Cash) — Table 50, FIN-005
            return self._generate_zero_finance_schedule(contract)

        rate_decimal = contract.effective_rate / 100.0
        total_instalments = plan.duration_months or 1
        payment_amount = contract.amount_financed / total_instalments

        lines = []
        opening_balance = contract.amount_financed
        unearned_remaining = contract.finance_charge

        for i in range(1, total_instalments + 1):
            due_date = self._next_due_date(contract, plan, i)

            if opening_balance > 0:
                finance_income = opening_balance * rate_decimal
                finance_income = min(finance_income, unearned_remaining)
            else:
                finance_income = 0.0

            principal = payment_amount - finance_income
            closing_balance = opening_balance - principal

            if i == total_instalments:
                payment_amount = principal + closing_balance + contract.amount_financed * 0.001
                finance_income = unearned_remaining

            lines.append({
                'contract_id': contract.id,
                'instalment_number': i,
                'due_date': due_date,
                'contractual_amount': payment_amount,
                'paid_amount': 0.0,
                'balance': closing_balance + contract.amount_financed - payment_amount + finance_income,
                'status': 'pending',
            })

            lines.append({
                'contract_id': contract.id,
                'instalment_number': i,
                'due_date': due_date,
                'opening_net_balance': opening_balance,
                'effective_rate': rate_decimal * 100,
                'finance_income': finance_income,
                'payment_amount': payment_amount,
                'principal_reduction': principal,
                'closing_balance': closing_balance + contract.amount_financed - payment_amount + finance_income,
                'unearned_income_remaining': unearned_remaining,
            })

            opening_balance = closing_balance + contract.amount_financed - payment_amount + finance_income
            unearned_remaining -= finance_income

        return lines

    def _generate_zero_finance_schedule(self, contract):
        """Zero-finance plan: deposit + equal instalments. No finance income."""
        total_instalments = contract.plan_id.duration_months or 1
        payment_amount = contract.amount_financed / total_instalments

        lines = []
        balance = contract.amount_financed

        for i in range(1, total_instalments + 1):
            due_date = self._next_due_date(contract, contract.plan_id, i)
            closing_balance = balance - payment_amount

            if i == total_instalments:
                payment_amount = balance

            lines.append({
                'contract_id': contract.id,
                'instalment_number': i,
                'due_date': due_date,
                'contractual_amount': payment_amount,
                'paid_amount': 0.0,
                'balance': closing_balance,
                'status': 'pending',
            })

            lines.append({
                'contract_id': contract.id,
                'instalment_number': i,
                'due_date': due_date,
                'opening_net_balance': balance,
                'effective_rate': 0.0,
                'finance_income': 0.0,
                'payment_amount': payment_amount,
                'principal_reduction': payment_amount,
                'closing_balance': closing_balance,
                'unearned_income_remaining': 0.0,
            })

            balance = closing_balance

        return lines

    def _next_due_date(self, contract, plan, instalment_number):
        """Calculate due date respecting weekends and public holidays.

        Table 29, SCH-004: Due dates respect weekends and public holidays
        according to the approved contract rule.
        """
        if not contract.activation_date:
            return fields.Date.today() + timedelta(days=30)

        month_offset = instalment_number - 1
        day = contract.activation_date.day
        month = contract.activation_date.month - 1 + month_offset
        year = contract.activation_date.year + (month // 12)
        month = month % 12 + 1

        try:
            base_date = contract.activation_date.replace(year=year, month=month, day=day)
        except ValueError:
            last_day = (
                contract.activation_date.replace(
                    year=year, month=month + 1 if month < 12 else 1, day=1
                ) - timedelta(days=1)
            ).day
            base_date = contract.activation_date.replace(
                year=year, month=min(month, 12), day=min(day, last_day)
            )

        while base_date.weekday() >= 5:
            base_date += timedelta(days=1)

        return base_date

    # ── Contract lifecycle methods ─────────────────────────────────
    def action_activate(self):
        """Activate the contract upon delivery. Table 20, DEL-004."""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Only draft contracts can be activated.'))

            schedule_data = rec._generate_schedule_lines(rec)
            ScheduleLine = self.env['hp.schedule.line']
            for sd in schedule_data:
                ScheduleLine.create(sd)

            rec.state = 'active'
            rec.activation_date = fields.Date.today()

    def action_restructure_review(self):
        """Enter restructure review. Table 33, MOD-001 to MOD-005."""
        for rec in self:
            if rec.state not in ('active', 'in_arrears', 'grace_period'):
                raise ValidationError(_('Restructure can only be reviewed on active contracts.'))
            rec.state = 'restructure_review'

    def action_mark_settled(self):
        """Mark contract as settled. Table 32, SET-005."""
        for rec in self:
            total_paid = sum(
                sl.paid_amount for sl in rec.schedule_line_ids
                if sl.status not in ('cancelled',)
            )
            if abs(total_paid - rec.statutory_hp_price) > 0.01:
                raise ValidationError(
                    _('Contract is not fully settled. Paid: %s, Statutory Price: %s')
                    % (total_paid, rec.statutory_hp_price)
                )
            rec.state = 'settled'

    def action_mark_ownership_transferred(self):
        """Transfer ownership. Table 32, SET-005."""
        for rec in self:
            if rec.state != 'settled':
                raise ValidationError(_('Contract must be settled first.'))
            rec.ownership_status = 'transferred'
            rec.ownership_transfer_date = fields.Date.today()
            rec.state = 'ownership_transferred'

    # ── Statutory calculations (Table 35, LEG-004 to LEG-006) ──────
    def action_recalculate_statutory(self):
        """Recalculate qualifying paid amount and 70% threshold.

        Table 35, LEG-004: Qualifying paid = deposit + approved non-cash credits
                            + payments/tenders by customer or guarantor towards HP price.
        LEG-005: Penalties, late fees, damages, legal fees, collection costs
                 and installation charges are EXCLUDED from 70% calculation.
        """
        for rec in self:
            qualifying = 0.0
            for sl in rec.schedule_line_ids:
                if sl.status not in ('cancelled',):
                    qualifying += sl.paid_amount

            rec.qualifying_paid_amount = qualifying

            threshold_70 = rec.statutory_hp_price * 0.70
            rec.amount_to_70_percent = max(0.0, threshold_70 - qualifying)

    # ── Status update job (Table 70, JOB-001) ─────────────────────
    @api.model
    def action_update_statuses(self):
        """Daily job to update due/grace/arreurs statuses. Table 70, JOB-001."""
        today = fields.Date.today()

        for contract in self.search([('state', 'in', ['active', 'payment_due', 'grace_period'])]):
            overdue_lines = contract.schedule_line_ids.filtered(
                lambda sl: sl.due_date and sl.due_date < str(today)
                             and sl.status not in ('paid', 'cancelled')
                             and sl.balance > 0.01
            )

            if overdue_lines:
                grace_days = contract.plan_id.grace_period_days or 7
                grace_date = today - timedelta(days=grace_days)

                for line in overdue_lines:
                    if line.due_date < str(grace_date):
                        contract.state = 'in_arrears'
                        break
                    else:
                        contract.state = 'grace_period'
            else:
                due_today = contract.schedule_line_ids.filtered(
                    lambda sl: sl.due_date == str(today) and sl.status not in ('paid',)
                )
                if due_today:
                    contract.state = 'payment_due'

    # ── Report helpers ─────────────────────────────────────────────
    def action_generate_statement(self):
        """Generate customer statement. Table 29, SCH-006."""
        lines = []
        for sl in self.schedule_line_ids.sorted(key=lambda s: s.instalment_number):
            lines.append({
                'instalment': sl.instalment_number,
                'due_date': sl.due_date,
                'amount': sl.contractual_amount,
                'paid': sl.paid_amount,
                'balance': sl.balance,
                'status': sl.status,
            })

        return {
            'type': 'ir.actions.report',
            'report_name': 'hire_purchase.hp_statement_report',
            'report_type': 'qweb-pdf',
            'context': {'statement_lines': lines},
        }

    # ── Override create to set default values ───────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env.ir.sequence.next_by_code('hp.contract') or '/'
        return super().create(vals_list)
