"""Hire Purchase Agreement model.

Generated and signed legal document versions per Table 26 (AGR-001 to AGR-007).
Each material amendment creates a new agreement version; the original
signed document remains unchanged (AGR-007).

Table 61: Minimum content includes approved contractual/statutory terms,
          goods identification, signatures and version.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpAgreement(models.Model):
    _name = 'hp.agreement'
    _description = 'Hire Purchase Agreement'

    name = fields.Char(string='Agreement Reference', required=True, copy=False, readonly=True, default='/')
    contract_id = fields.Many2one('hp.contract', string='Contract', ondelete='cascade', required=True)
    application_id = fields.Many2one('hp.application', string='Application', related='contract_id.application_id', store=True)

    version = fields.Integer(string='Version', default=1)
    template_version_id = fields.Many2one('hp.plan.template', string='Template Version')
    sign_request_id = fields.Many2one('account.sign.request', string='Odoo Sign Request')
    sign_status = fields.Selection([
        ('not_sent', 'Not Sent'), ('sent', 'Sent'), ('signed_all', 'All Signatures Complete'),
        ('declined', 'Declined'), ('expired', 'Expired'),
    ], string='Sign Status', default='not_sent')
    sign_completed_date = fields.Date(string='Signature Completed Date')

    signer_order = fields.Selection([
        ('customer_first', 'Customer First'), ('guarantor_first', 'Guarantor First'),
        ('company_first', 'Company First'),
    ], string='Signer Order', default='customer_first')

    customer_signed = fields.Boolean(string='Customer Signed')
    customer_signed_date = fields.Date()
    guarantor_signed = fields.Boolean(string='Guarantor Signed')
    guarantor_signed_date = fields.Date()
    company_signed = fields.Boolean(string='Company Signed')
    company_signed_date = fields.Date()

    customer_name = fields.Char()
    customer_id_number = fields.Char()
    goods_description = fields.Text()
    cash_price = fields.Float()
    hp_price = fields.Float()
    deposit_amount = fields.Float()
    finance_charge = fields.Float()
    statutory_notices = fields.Text(string='Statutory Notices Included')

    document_ids = fields.One2many('hp.document', 'agreement_id', string='Documents')
    company_id = fields.Many2one('res.company')
    note = fields.Text()

    @api.constrains('version')
    def _check_version_positive(self):
        for rec in self:
            if rec.version < 1:
                raise ValidationError(_('Version must be at least 1.'))

    def action_send_for_signature(self):
        """Send agreement for signature via Odoo Sign. Table 26, AGR-003."""
        for rec in self:
            if not rec.customer_id_number:
                raise ValidationError(_('Customer ID is required before sending for signature.'))
            sign_request = self.env['account.sign.request'].sudo().create({
                'name': '%s - Agreement v%d' % (rec.contract_id.name, rec.version),
                'res_model': 'hp.contract', 'res_id': rec.contract_id.id,
                'signer_order': rec.signer_order,
            })
            rec.sign_request_id = sign_request.id
            rec.sign_status = 'sent'

    def action_mark_signed(self):
        """Mark agreement as fully signed. Table 26, AGR-004."""
        for rec in self:
            if not (rec.customer_signed and rec.guarantor_signed and rec.company_signed):
                raise ValidationError(_('All required signatures must be complete.'))
            rec.sign_status = 'signed_all'
            rec.sign_completed_date = fields.Date.today()

    def action_create_amendment(self):
        """Create a new agreement version for material amendment. Table 26, AGR-007."""
        self.ensure_one()
        return {
            'name': '%s - Amendment v%d' % (self.name, self.version + 1),
            'type': 'ir.actions.act_window',
            'res_model': 'hp.agreement',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env.ir.sequence.next_by_code('hp.agreement') or '/'
        return super().create(vals_list)
