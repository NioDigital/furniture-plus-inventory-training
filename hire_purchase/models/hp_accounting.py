"""Hire Purchase Accounting Entries.

Generates journal items for:
 1. Deposit receipt (at application approval)
 2. Delivery entry (goods + VAT + receivable recognition)
 3. Instalment payment entries (principal + finance income)
 4. Finance income recognition (EIR method - IFRS for SMEs)
 5. Repossession entries (derecognition, fair value, gain/loss)
 6. Early settlement entries (rebate or penalty calculation)
 7. Write-off entries (bad debt allowance)

Table 47: Chart of accounts for HP (10 accounts).
Table 50: Finance income recognition rules.
Table 56-57: Repossession accounting.
"""

from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpAccountingEntry(models.Model):
    _name = 'hp.accounting.entry'
    _description = 'Hire Purchase Accounting Entry'
    _order = 'contract_id, entry_date desc'

    contract_id = fields.Many2one(
        'hp.contract', string='Contract', ondelete='cascade', required=True,
    )
    entry_type = fields.Selection([
        ('deposit', 'Deposit Receipt'),
        ('delivery', 'Delivery Entry'),
        ('instalment', 'Instalment Payment'),
        ('finance_income', 'Finance Income Recognition'),
        ('repossession', 'Repossession'),
        ('early_settlement', 'Early Settlement'),
        ('write_off', 'Write-off'),
        ('adjustment', 'Adjustment'),
    ], string='Entry Type', required=True)
    entry_date = fields.Date(string='Entry Date')
    reference = fields.Char(string='Reference')

    # Amounts
    gross_amount = fields.Float(string='Gross Amount')
    net_amount = fields.Float(string='Net Amount')
    vat_amount = fields.Float(string='VAT Amount')
    finance_income_amount = fields.Float(string='Finance Income Amount')
    principal_amount = fields.Float(string='Principal Amount')

    # Accounts (from plan configuration)
    debit_account_id = fields.Many2one('account.account', string='Debit Account')
    credit_account_id = fields.Many2one('account.account', string='Credit Account')

    # Journal
    journal_id = fields.Many2one('account.journal', string='Journal')

    # Link to schedule line
    schedule_line_id = fields.Many2one('hp.schedule.line', string='Schedule Line')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Reconciled tracking
    reconciled = fields.Boolean(string='Reconciled', default=False)

    # Notes
    note = fields.Text()

    def action_post(self):
        """Post the accounting entry."""
        for entry in self:
            if not entry.debit_account_id or not entry.credit_account_id:
                raise ValidationError(
                    _('Both debit and credit accounts are required.')
                )
            if not entry.journal_id:
                raise ValidationError(_('A journal is required.'))

            # Create account.move
            move = self.env['account.move'].create({
                'journal_id': entry.journal_id.id,
                'date': entry.entry_date or fields.Date.today(),
                'ref': entry.reference or '',
                'line_ids': [
                    (0, 0, {
                        'name': 'Debit line',
                        'account_id': entry.debit_account_id.id,
                        'debit': entry.gross_amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Credit line',
                        'account_id': entry.credit_account_id.id,
                        'debit': 0.0,
                        'credit': entry.gross_amount,
                    }),
                ],
            })
            entry.state = 'posted'

    def action_cancel(self):
        """Cancel the accounting entry."""
        for entry in self:
            if entry.state == 'posted':
                move = self.env['account.move'].search([
                    ('ref', '=', entry.reference),
                    ('journal_id', '=', entry.journal_id.id),
                ], limit=1)
                if move:
                    move.action_cancel()
            entry.state = 'cancelled'

    def action_reconcile(self):
        """Mark as reconciled."""
        for entry in self:
            entry.reconciled = True


class HpContractAccounting(models.Model):
    """Mixin for HP contract accounting methods."""
    _inherit = 'hp.contract'

    def action_generate_delivery_entry(self):
        """Generate delivery entry. Table 47, DEL-004."""
        for contract in self:
            plan = contract.plan_id
            if not plan:
                raise ValidationError(_('Plan is required.'))

            move = self.env['account.move'].create({
                'journal_id': plan.finance_income_journal_id.id,
                'date': contract.delivery_date or fields.Date.today(),
                'ref': 'Delivery - %s' % contract.name,
                'line_ids': [
                    (0, 0, {
                        'name': 'Customer Receivable',
                        'account_id': plan.finance_income_account_id.id,
                        'debit': contract.statutory_hp_price,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Sales Revenue',
                        'account_id': plan.unearned_income_account_id.id,
                        'debit': 0.0,
                        'credit': contract.cash_price_excl_vat,
                    }),
                    (0, 0, {
                        'name': 'VAT Payable',
                        'account_id': plan.vat_payable_account_id.id,
                        'debit': 0.0,
                        'credit': contract.vat_amount,
                    }),
                ],
            })

    def action_generate_early_settlement_entry(self, settlement_amount):
        """Generate early settlement entry with configurable method."""
        for contract in self:
            plan = contract.plan_id

            if plan.early_settlement_method == 'cash_price':
                # Customer pays cash price (full rebate)
                settlement_amount = contract.cash_price_incl_vat
            elif plan.early_settlement_method == 'penalty_percentage':
                remaining = contract.statutory_hp_price - contract.qualifying_paid_amount
                settlement_amount = remaining * (1 + plan.early_settlement_penalty_pct / 100)
            elif plan.early_settlement_method == 'penalty_flat':
                remaining = contract.statutory_hp_price - contract.qualifying_paid_amount
                settlement_amount = remaining + plan.early_settlement_penalty_amount
            # else: no penalty - settlement amount as-is

            move = self.env['account.move'].create({
                'journal_id': plan.finance_income_journal_id.id,
                'date': fields.Date.today(),
                'ref': 'Early Settlement - %s' % contract.name,
                'line_ids': [
                    (0, 0, {
                        'name': 'Bank Receipt',
                        'account_id': plan.finance_income_account_id.id,
                        'debit': settlement_amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Customer Receivable Derecognition',
                        'account_id': plan.unearned_income_account_id.id,
                        'debit': 0.0,
                        'credit': contract.statutory_hp_price,
                    }),
                ],
            })

    def action_generate_repossession_entry(self, repossessed_value):
        """Generate repossession entry. Tables 56-57."""
        for contract in self:
            plan = contract.plan_id

            net_carrying = (contract.statutory_hp_price -
                            contract.qualifying_paid_amount)

            if repossessed_value >= net_carrying:
                # Gain
                gain = repossessed_value - net_carrying
                move_lines = [
                    (0, 0, {
                        'name': 'Repossessed Goods',
                        'account_id': plan.repossessed_goods_account_id.id,
                        'debit': repossessed_value,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Customer Receivable Derecognition',
                        'account_id': plan.unearned_income_account_id.id,
                        'debit': 0.0,
                        'credit': net_carrying,
                    }),
                    (0, 0, {
                        'name': 'Gain on Repossession',
                        'account_id': plan.gain_repossession_account_id.id,
                        'debit': 0.0,
                        'credit': gain,
                    }),
                ]
            else:
                # Loss
                loss = net_carrying - repossessed_value
                move_lines = [
                    (0, 0, {
                        'name': 'Repossessed Goods',
                        'account_id': plan.repossessed_goods_account_id.id,
                        'debit': repossessed_value,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Loss on Repossession',
                        'account_id': plan.loss_repossession_account_id.id,
                        'debit': loss,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Customer Receivable Derecognition',
                        'account_id': plan.unearned_income_account_id.id,
                        'debit': 0.0,
                        'credit': net_carrying,
                    }),
                ]

            self.env['account.move'].create({
                'journal_id': plan.finance_income_journal_id.id,
                'date': contract.repossessed_date or fields.Date.today(),
                'ref': 'Repossession - %s' % contract.name,
                'line_ids': move_lines,
            })

    def action_generate_write_off_entry(self):
        """Write off remaining balance against bad debt allowance."""
        for contract in self:
            plan = contract.plan_id
            remaining = contract.statutory_hp_price - contract.qualifying_paid_amount

            if remaining <= 0:
                continue

            self.env['account.move'].create({
                'journal_id': plan.finance_income_journal_id.id,
                'date': fields.Date.today(),
                'ref': 'Write-off - %s' % contract.name,
                'line_ids': [
                    (0, 0, {
                        'name': 'Bad Debt Allowance Write-off',
                        'account_id': plan.allowance_bad_debt_account_id.id,
                        'debit': remaining,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': 'Customer Receivable Derecognition',
                        'account_id': plan.unearned_income_account_id.id,
                        'debit': 0.0,
                        'credit': remaining,
                    }),
                ],
            })
