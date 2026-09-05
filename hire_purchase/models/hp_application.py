"""Hire Purchase Application model.

Manages the customer application workflow: credit review, approval,
rejection, expiry and withdrawal per Sections 10-12 of the spec.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpApplication(models.Model):
    _name = 'hp.application'
    _description = 'Hire Purchase Application'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='/')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    guarantor_ids = fields.Many2many(
         'res.partner', string='Guarantors',
        help='Optional guarantors for the hire purchase agreement.',
      )
    plan_id = fields.Many2one('hp.plan', string='Hire Purchase Plan', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')

    goods_description = fields.Text(string='Goods Description')
    total_goods_value = fields.Float(string='Total Goods Value (TT$)')
    deposit_amount = fields.Float(string='Deposit Amount (TT$)')
    finance_charge_amount = fields.Float(string='Finance Charge Amount (TT$)')
    total_hire_purchase_price = fields.Float(
        string='Total Hire Purchase Price (TT$)',
        compute='_compute_total_hp_price', store=True,
      )

    state = fields.Selection([
         ('draft', 'Draft'),
         ('submitted', 'Submitted'),
         ('credit_review', 'Credit Review'),
         ('approved', 'Approved'),
         ('conditionally_approved', 'Conditionally Approved'),
         ('rejected', 'Rejected'),
         ('expired', 'Expired'),
         ('withdrawn', 'Withdrawn'),
     ], string='Status', default='draft')

    application_date = fields.Date(default=fields.Date.today)
    expiry_date = fields.Date()
    credit_reviewer_id = fields.Many2one('res.users', string='Credit Reviewer')
    credit_review_notes = fields.Text()
    approval_decision = fields.Selection([
         ('approve', 'Approve'),
         ('conditionally_approve', 'Conditionally Approve'),
         ('reject', 'Reject'),
     ])
    approval_date = fields.Date()

    monthly_income = fields.Float(string='Monthly Income (TT$)')
    existing_commitments = fields.Float(string='Existing Commitments (TT$)')
    affordability_ratio = fields.Float(
        string='Affordability Ratio (%)', compute='_compute_affordability', store=True,
      )

    document_checklist = fields.Many2many('hp.document.type', string='Required Documents')
    documents_received = fields.Boolean(string='All Documents Received')

    def action_submit(self):
        for app in self:
            if app.state == 'draft':
                if not app.partner_id:
                    raise ValidationError(_('Customer is required.'))
                if not app.plan_id:
                    raise ValidationError(_('Hire Purchase Plan is required.'))
                app.state = 'submitted'

    def action_start_credit_review(self):
        for app in self:
            if app.state == 'submitted':
                app.state = 'credit_review'

    def action_approve(self):
        for app in self:
            if app.state in ('credit_review', 'conditionally_approved'):
                app.approval_decision = 'approve'
                app.approval_date = fields.Date.today()
                app.state = 'approved'

    def action_conditionally_approve(self):
        for app in self:
            if app.state == 'credit_review':
                app.approval_decision = 'conditionally_approve'
                app.approval_date = fields.Date.today()
                app.state = 'conditionally_approved'

    def action_reject(self):
        for app in self:
            if app.state in ('credit_review', 'conditionally_approved'):
                app.approval_decision = 'reject'
                app.approval_date = fields.Date.today()
                app.state = 'rejected'

    def action_withdraw(self):
        for app in self:
            if app.state not in ('draft',):
                app.state = 'withdrawn'

    @api.depends('total_goods_value', 'finance_charge_amount')
    def _compute_total_hp_price(self):
        for rec in self:
            rec.total_hire_purchase_price = (rec.total_goods_value or 0) + (rec.finance_charge_amount or 0)

    @api.depends('monthly_income', 'existing_commitments')
    def _compute_affordability(self):
        for rec in self:
            if rec.monthly_income and rec.monthly_income > 0:
                ratio = ((rec.monthly_income - rec.existing_commitments) / rec.monthly_income) * 100
                rec.affordability_ratio = ratio
            else:
                rec.affordability_ratio = 0
