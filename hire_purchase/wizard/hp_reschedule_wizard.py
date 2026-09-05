"""HP Reschedule Wizard.

Allow restructuring of payment schedule for a contract.
Table 33, MOD-001 to MOD-005: Restructure controls.
"""

from odoo import models, fields, api, _


class HpRescheduleWizard(models.TransientModel):
     _name = 'hp.reschedule.wizard'
     _description = 'HP Reschedule Wizard'

    contract_id = fields.Many2one(
         'hp.contract', string='Contract', required=True,
      )
    new_duration_months = fields.Integer(string='New Duration (Months)')
    note = fields.Text()

    def action_reschedule(self):
          """Reschedule the contract."""
        self.ensure_one()
         # Placeholder: actual reschedule logic would regenerate schedule lines
        return {'type': 'ir.actions.act_window_close'}
