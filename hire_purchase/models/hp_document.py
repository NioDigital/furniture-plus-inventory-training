"""Hire Purchase Document model.

Document checklist and attachment tracking per Tables 17-18 (APP-005, GUA-001).
Identity and income documents are restricted to authorised credit, legal
and audit users only (Table 70, AUD-005).

Table 61: Minimum document content includes signed agreements, payment
          schedules, statements, notices, settlement quotations and more.
"""

from odoo import models, fields, api


class HpDocumentType(models.Model):
    _name = 'hp.document.type'
    _description = 'Hire Purchase Document Type'

    name = fields.Char(string='Document Type', required=True)
    category = fields.Selection([
        ('identity', 'Identity'), ('income', 'Income'), ('agreement', 'Agreement'),
        ('payment', 'Payment'), ('legal', 'Legal'), ('delivery', 'Delivery'), ('other', 'Other'),
     ], string='Category', default='other')
    is_required = fields.Boolean(string='Required', default=True)
    requires_verification = fields.Boolean(string='Requires Verification', default=False)

    def __str__(self):
        return self.name


class HpDocument(models.Model):
    _name = 'hp.document'
    _description = 'Hire Purchase Document'

    name = fields.Char(string='Document Name', required=True)
    document_type_id = fields.Many2one('hp.document.type', string='Type', required=True)
    application_id = fields.Many2one('hp.application', string='Application')
    agreement_id = fields.Many2one('hp.agreement', string='Agreement')
    contract_id = fields.Many2one('hp.contract', string='Contract')

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    document_file = fields.Binary(string='Document File')
    document_filename = fields.Char(string='File Name')

    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    verification_status = fields.Selection([
        ('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected'),
     ], string='Verification Status', default='pending')
    verifier_id = fields.Many2one('res.users', string='Verifier')
    verification_date = fields.Date()

    access_group = fields.Selection([
        ('credit', 'Credit'), ('legal', 'Legal'), ('audit', 'Audit'), ('general', 'General'),
     ], string='Access Group', default='general')

    retention_years = fields.Integer(string='Retention Years (Years)', default=7)
    retention_expiry_date = fields.Date(
        string='Retention Expiry Date', compute='_compute_retention_expiry', store=True,
     )

    note = fields.Text()

    @api.depends('issue_date', 'retention_years')
    def _compute_retention_expiry(self):
        from datetime import timedelta
        for rec in self:
            if rec.issue_date and rec.retention_years > 0:
                rec.retention_expiry_date = rec.issue_date + timedelta(days=rec.retention_years * 365)
            else:
                rec.retention_expiry_date = False
