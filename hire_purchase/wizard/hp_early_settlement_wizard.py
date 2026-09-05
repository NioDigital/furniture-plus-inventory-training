"""HP Early Settlement Wizard.

Allow early settlement of a hire purchase contract.
Table 32, SET-001 to SET-004: Early settlement rules.
"""

from odoo import models, fields, api, _


class HpEarlySettlementWizard(models.TransientModel):
     _name = 'hp.early.settlement.wizard'
     _description = 'HP Early Settlement Wizard'

    contract_id = fields.Many2one(
         'hp.contract', string='Contract', required=True,
      )
    settlement_amount = fields.Float(string='Settlement Amount')
    note = fields.Text()

    def action_settle(self):
           """Settle the contract early."""
        self.ensure_one()
         # Placeholder: actual settlement logic would calculate remaining balance,
         # apply finance income adjustments and create accounting entries
        return {'type': 'ir.actions.act_window_close'}
