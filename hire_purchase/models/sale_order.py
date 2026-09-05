"""Sale Order extension for Hire Purchase linkage.

Links sale orders to HP applications and contracts.
Table 20: Sales quotation -> HP application -> approval -> agreement -> contract.

Gate: If an HP payment term is selected on any order line, the SO cannot be
confirmed until the linked HP application is approved.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hp_application_id = fields.Many2one(
         'hp.application', string='HP Application', readonly=True,
     )
    hp_contract_id = fields.Many2one(
         'hp.contract', string='HP Contract', readonly=True,
     )
    hp_plan_id = fields.Many2one(
         'hp.plan', string='HP Plan', related='hp_application_id.plan_id', store=True,
     )

    def _get_hp_lines(self):
        """Return sale order lines that use an HP payment term."""
        hp_lines = self.env['sale.order.line']
        for line in self.order_line:
            if line.product_id and line.product_id.property_payment_term_id:
                pt = line.product_id.property_payment_term_id
                if hasattr(pt, 'hp_method') and pt.hp_method == 'hp_instalment':
                    hp_lines |= line
        return hp_lines

    def action_confirm(self):
        """Override: block confirmation if HP application is not approved."""
        for order in self:
            hp_lines = order._get_hp_lines()
            if hp_lines and order.state not in ('sale', 'done'):
                app = order.hp_application_id
                if app and app.state != 'approved':
                    raise ValidationError(
                        _('Cannot confirm this order: the linked Hire Purchase Application '
                          '"%s" is not yet approved (current status: %s).')
                        % (app.name, app.state)
                    )
        return super().action_confirm()

    def _get_payment_term_id(self):
        """Check if any line uses an HP payment term."""
        for line in self.order_line:
            if line.product_id and line.product_id.property_payment_term_id:
                pt = line.product_id.property_payment_term_id
                if hasattr(pt, 'hp_method') and pt.hp_method == 'hp_instalment':
                    return True
        return False
