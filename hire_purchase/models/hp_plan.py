"""Hire Purchase Plan model.

A Hire Purchase Plan is a financing product. It is linked to an Odoo
payment term but contains additional legal, credit, pricing and
accounting rules per Section 9 of the requirements spec.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpPlan(models.Model):
    _name = 'hp.plan'
    _description = 'Hire Purchase Plan'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    payment_term_id = fields.Many2one(
           'account.payment.term', string='Payment Term', required=True,
         help='Linked Odoo payment term for instalment scheduling.',
       )
    duration_months = fields.Integer(string='Duration (Months)', required=True)

      # Pricing
    monthly_min_payment = fields.Float(string='Minimum Monthly Payment')
    finance_charge_type = fields.Selection([
           ('flat', 'Flat Finance Charge'),
           ('reducing', 'Reducing Balance'),
           ('daily', 'Daily Rest'),
       ], string='Finance Charge Type', default='flat', required=True)
    finance_charge_rate = fields.Float(string='Finance Charge Rate (%)')
    max_contract_value = fields.Float(string='Max Contract Value (TT$)')

      # Legal / regulatory
    statutory_scope_limit = fields.Float(
         string='Statutory Scope Limit (TT$)', default=15000.0,
         help='Hire Purchase Act Ch 82:33 limit. Contracts above require '
                'legal approval per R1.',
       )
    requires_guarantor = fields.Boolean(string='Requires Guarantor')
    min_deposit_pct = fields.Float(string='Minimum Deposit %')
    grace_period_days = fields.Integer(
         string='Grace Period (Days)', default=7,
         help='Number of days after due date before contract enters arrears.',
       )

      # Accounting — all configurable per plan (user-selectable)
    unearned_income_account_id = fields.Many2one(
           'account.account', string='Unearned Finance Income Account',
       )
    finance_income_account_id = fields.Many2one(
           'account.account', string='Finance Income Account',
       )
    finance_income_journal_id = fields.Many2one(
           'account.journal', string='Finance Income Journal',
       )
    bad_debt_account_id = fields.Many2one(
           'account.account', string='Bad Debt Expense Account',
       )
    allowance_bad_debt_account_id = fields.Many2one(
           'account.account', string='Allowance for Bad Debts Account',
       )
    repossessed_goods_account_id = fields.Many2one(
           'account.account', string='Repossessed Goods Account',
       )
    loss_repossession_account_id = fields.Many2one(
           'account.account', string='Loss on Repossession Account',
       )
    gain_repossession_account_id = fields.Many2one(
           'account.account', string='Gain on Repossession Resale Account',
       )
    write_off_account_id = fields.Many2one(
           'account.account', string='Write-off Account',
       )
    vat_payable_account_id = fields.Many2one(
           'account.account', string='VAT Payable Account',
       )

      # Early settlement configuration (configurable by plan)
    early_settlement_method = fields.Selection([
           ('cash_price', 'Cash Price (Full Rebate)'),
           ('penalty_flat', 'Flat Penalty'),
           ('penalty_percentage', 'Percentage Penalty'),
           ('no_penalty', 'No Penalty'),
       ], string='Early Settlement Method', default='cash_price')
    early_settlement_penalty_pct = fields.Float(string='Penalty %')
    early_settlement_penalty_amount = fields.Float(string='Penalty Amount (TT$)')

      # Accounting framework selection
    accounting_framework = fields.Selection([
           ('full_ifrs', 'Full IFRS'),
           ('ifrs_smes', 'IFRS for SMEs'),
       ], string='Accounting Framework', default='ifrs_smes')

      # Status
    is_active = fields.Boolean(default=True)
    state = fields.Selection([
           ('draft', 'Draft'),
           ('approved', 'Approved'),
           ('archived', 'Archived'),
       ], string='Status', default='draft')

    def action_approve(self):
        for plan in self:
            plan.state = 'approved'

    def action_archive(self):
        for plan in self:
            plan.state = 'archived'

    @api.constrains('finance_charge_rate', 'max_contract_value')
    def _check_rates(self):
        for plan in self:
            if plan.finance_charge_rate < 0:
                raise ValidationError(_('Finance charge rate cannot be negative.'))
            if plan.max_contract_value <= 0:
                raise ValidationError(_('Max contract value must be positive.'))
