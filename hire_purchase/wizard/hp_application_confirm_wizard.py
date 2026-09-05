"""HP Application Confirm Wizard.

Wizard to confirm an approved application and create the contract.
Table 20: Application → Approval → Contract flow.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpApplicationConfirmWizard(models.TransientModel):
     _name = 'hp.application.confirm.wizard'
     _description = 'HP Application Confirm Wizard'

    application_id = fields.Many2one(
         'hp.application', string='Application', required=True,
      )
    note = fields.Text()

    def action_confirm(self):
         """Confirm the application and create a contract."""
        self.ensure_one()
        app = self.application_id

         if app.state != 'approved':
             raise ValidationError(_('Only approved applications can be confirmed.'))

         # Create contract from application data
        contract_vals = {
             'application_id': app.id,
             'plan_id': app.plan_id.id,
             'partner_id': app.partner_id.id,
             'cash_price_excl_vat': app.total_goods_value / 1.125 if app.total_goods_value else 0,
             'vat_amount': (app.total_goods_value or 0) * 0.125 / 1.125,
             'deposit_amount': app.deposit_amount,
             'finance_charge': app.finance_charge_amount,
             'statutory_hp_price': app.total_hire_purchase_price,
             'accounting_framework': app.plan_id.accounting_framework,
         }

        contract = self.env['hp.contract'].create(contract_vals)

        return {
             'type': 'ir.actions.act_window',
             'res_model': 'hp.contract',
             'res_id': contract.id,
             'view_mode': 'form',
             'target': 'current',
         }
