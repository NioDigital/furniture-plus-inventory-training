"""Custom Payment Term Type for Hire Purchase.

Table 68, INT-001: Hire Purchase Plans link to Odoo payment terms but
generate custom maturity lines from the signed schedule.

This implements a custom payment term type ('hp_instalment') that generates
instalment-based maturity lines instead of using Odoo's built-in distribution
method. Each instalment is a fixed amount with a due date from the contract
schedule, not from the payment term's own logic.
"""

from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    hp_method = fields.Selection([
        ('standard', 'Standard Odoo'),
        ('hp_instalment', 'HP Instalment (Custom)'),
      ], string='HP Payment Method', default='standard')

    def _compute_next_line_amount(self, first_invoice_amount, total_amount, total_lines):
        """Override for HP instalment method."""
        if self.hp_method == 'hp_instalment':
            if total_lines > 0:
                return total_amount / total_lines
            return 0.0
        return super()._compute_next_line_amount(first_invoice_amount, total_amount, total_lines)

    def _get_payment_term_values(self, value_residual, currency, invoice_date=None):
        """Generate custom payment term values for HP instalments."""
        if self.hp_method == 'hp_instalment':
            return []
        return super()._get_payment_term_values(value_residual, currency, invoice_date)


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    def _compute_next_line_amount(self, first_invoice_amount, total_amount, total_lines):
        """HP instalment lines are equal amounts."""
        if self.payment_id.hp_method == 'hp_instalment':
            if total_lines > 0:
                return total_amount / total_lines
            return 0.0
        return super()._compute_next_line_amount(first_invoice_amount, total_amount, total_lines)
