"""Hire Purchase Schedule Line model.

Each contract has two parallel schedule lines per instalment:
 1. Contractual line - customer obligation, collection, arrears tracking
 2. Accounting line - finance income recognition, net receivable tracking

Table 44: Contractual schedule (instalment number, due date, total due,
          paid, status, arrears, fees and balance)
Table 44: Accounting amortisation schedule (opening net balance, rate, days,
          finance income, payment, principal, closing balance and unearned income)

Table 29: SCH-001 (contractual), SCH-002 (accounting), SCH-003 (reconciliation).
"""

from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HpScheduleLine(models.Model):
    _name = 'hp.schedule.line'
    _description = 'Hire Purchase Schedule Line'
    _order = 'contract_id, instalment_number'

    contract_id = fields.Many2one('hp.contract', string='Contract', ondelete='cascade', required=True)
    instalment_number = fields.Integer(string='Instalment #')
    due_date = fields.Date(string='Due Date')
    contractual_amount = fields.Float(string='Contractual Amount')
    paid_amount = fields.Float(string='Paid Amount')
    balance = fields.Float(string='Balance')
    status = fields.Selection([
        ('pending', 'Pending'), ('paid', 'Paid'), ('partial', 'Partial'),
        ('overdue', 'Overdue'), ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')

    opening_net_balance = fields.Float(string='Opening Net Balance')
    effective_rate = fields.Float(string='Effective Rate (%)', digits=(12, 8))
    finance_income = fields.Float(string='Finance Income')
    payment_amount = fields.Float(string='Payment Amount')
    principal_reduction = fields.Float(string='Principal Reduction')
    closing_balance = fields.Float(string='Closing Balance')
    unearned_income_remaining = fields.Float(string='Unearned Income Remaining')

    payment_ids = fields.Many2many('account.payment', string='Payments')
    days_overdue = fields.Integer(string='Days Overdue', compute='_compute_days_overdue', store=True)

    @api.depends('due_date', 'paid_amount', 'contractual_amount')
    def _compute_days_overdue(self):
        today = date.today()
        for rec in self:
            if rec.due_date and rec.paid_amount < rec.contractual_amount - 0.01:
                delta = (today - rec.due_date).days
                rec.days_overdue = max(0, delta)
            else:
                rec.days_overdue = 0

    @api.constrains('contractual_amount', 'paid_amount')
    def _check_paid_not_exceeds(self):
        for rec in self:
            if rec.paid_amount > rec.contractual_amount + 0.01:
                raise ValidationError(
                    _('Payment (%.2f) exceeds contractual amount (%.2f).') % (rec.paid_amount, rec.contractual_amount)
                )

    def action_reconcile(self):
        """Verify schedule reconciles to GL. Table 29, SCH-003."""
        for rec in self:
            contract = rec.contract_id
            if contract.state == 'settled':
                if abs(rec.closing_balance) > 0.01:
                    raise ValidationError(
                        _('Contract %s is settled but schedule line %d has non-zero closing balance: %.2f')
                        % (contract.name, rec.instalment_number, rec.closing_balance)
                    )
