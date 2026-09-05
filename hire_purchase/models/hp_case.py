"""Hire Purchase Collection Case model.

Manages arrears, statutory notices, legal review and repossession per
Tables 31-40 (COL-001 to LEG-044).

Key workflows:
 - Collections (Table 31): Reminders, late fees, promises, notices
 - Statutory notices (Table 37): 21 clear days, recovery intention
 - Court cases (Table 38): At or above 70% threshold
 - Voluntary termination (Table 40): Customer-requested return
 - Repossession (Tables 56-57): Recovery, valuation, resale

Table 67: hp.case links to contract and manages the collections lifecycle.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HpCase(models.Model):
    _name = 'hp.case'
    _description = 'Hire Purchase Collection Case'
    _order = 'create_date desc'

    name = fields.Char(string='Case Reference', required=True, copy=False, readonly=True, default='/')

     # ── Contract linkage ────────────────────────────────────────
    contract_id = fields.Many2one(
          'hp.contract', string='Contract', ondelete='cascade', required=True,
      )
    application_id = fields.Many2one(
          'hp.application', string='Application', related='contract_id.application_id', store=True,
      )

     # ── Case type (Table 31-40) ────────────────────────────────
    case_type = fields.Selection([
           ('reminder', 'Reminder'),
           ('late_fee', 'Late Fee'),
           ('promise_to_pay', 'Promise to Pay'),
           ('statutory_notice', 'Statutory Notice'),
           ('legal_review', 'Legal Review'),
           ('court_action', 'Court Action'),
           ('voluntary_termination', 'Voluntary Termination'),
           ('repossession', 'Repossession'),
           ('repossession_resale', 'Repossessed Goods Resale'),
       ], string='Case Type', default='reminder')

     # ── Status / stage ──────────────────────────────────────────
    state = fields.Selection([
           ('open', 'Open'),
           ('notice_active', 'Notice Active'),
           ('cured', 'Cured'),
           ('legal_review_pending', 'Legal Review Pending'),
           ('court_action_required', 'Court Action Required'),
           ('repossession_scheduled', 'Repossession Scheduled'),
           ('goods_recovered', 'Goods Recovered'),
           ('goods_valued', 'Goods Valued'),
           ('closed', 'Closed'),
       ], string='Status', default='open')

     # ── Notice details (Table 37, LEG-020 to LEG-026) ───────────
    notice_date = fields.Date(string='Notice Date')
    notice_served_date = fields.Date(string='Service Date')
    notice_service_method = fields.Selection([
           ('personal', 'Personal Delivery'),
           ('registered_letter', 'Registered Letter'),
       ], string='Service Method')
    recovery_intention_date = fields.Date(string='Proposed Recovery Date')
    clear_days_end_date = fields.Date(string='21 Clear Days End')
    notice_cured = fields.Boolean(string='Notice Cured')
    cure_amount = fields.Float(string='Cure Amount')

     # ── Court details (Table 38, LEG-030 to LEG-034) ────────────
    court_case_number = fields.Char(string='Court Case Number')
    court_name = fields.Char(string='Court')
    filing_date = fields.Date()
    hearing_dates = fields.Text(string='Hearing Dates')
    court_orders = fields.Text(string='Court Orders')
    court_evidence = fields.Binary(string='Evidence Attachment')

     # ── Repossession details (Tables 56-57) ─────────────────────
    repossessed_date = fields.Date()
    recovery_agent_id = fields.Many2one(
          'res.partner', string='Recovery Agent/Bailiff',
        help='Identity, licence or authority evidence required.',
      )
    recovery_scope = fields.Text(string='Scope of Recovery')
    recovery_outcome = fields.Text(string='Recovery Outcome')
    goods_condition = fields.Selection([
           ('good', 'Good'),
           ('fair', 'Fair'),
           ('poor', 'Poor'),
           ('damaged', 'Damaged'),
       ], string='Goods Condition')
    repossessed_value = fields.Float(string='Repossessed Goods Value')
    write_down_amount = fields.Float(string='Write-down Amount')

     # ── Voluntary termination (Table 40, TER-001 to TER-005) ────
    termination_request_date = fields.Date()
    goods_returned_date = fields.Date()
    damage_assessment = fields.Text(string='Damage Assessment')
    refund_amount = fields.Float(string='Refund Amount')
    shortfall_amount = fields.Float(string='Shortfall Amount')

     # ── Promise to pay (Table 31, COL-005) ──────────────────────
    promised_amount = fields.Float()
    promised_date = fields.Date()
    promise_channel = fields.Selection([
           ('phone', 'Phone'),
           ('portal', 'Portal'),
           ('in_store', 'In Store'),
           ('email', 'Email'),
       ], string='Promise Channel')
    promise_employee_id = fields.Many2one('res.users', string='Recorded By')
    promise_outcome = fields.Selection([
           ('fulfilled', 'Fulfilled'),
           ('broken', 'Broken'),
       ], string='Outcome')

     # ── Late fee tracking (Table 31, COL-002 to COL-004) ────────
    late_fee_amount = fields.Float()
    late_fee_waived = fields.Boolean()
    waiver_authority = fields.Many2one('res.users', string='Waiver Authority')

     # ── General tracking ────────────────────────────────────────
    legal_owner_id = fields.Many2one('res.users', string='Legal Owner')
    notes = fields.Text()
    company_id = fields.Many2one('res.company')

     # ── Computed: 70% threshold check (Table 35, LEG-006) ───────
    is_above_70_percent = fields.Boolean(
        string='Above 70% Threshold', compute='_check_threshold', store=True,
      )

     # ── Constraints ─────────────────────────────────────────────
    @api.depends('contract_id.statutory_paid_percentage')
    def _check_threshold(self):
        for rec in self:
            rec.is_above_70_percent = (rec.contract_id.statutory_paid_percentage >= 70.0)

     # ── Methods: Notice lifecycle (Table 37, LEG-020 to LEG-026) ─
    def action_issue_notice(self):
        """Issue statutory notice. Table 37, LEG-021 to LEG-024."""
        for rec in self:
            if rec.notice_date and rec.recovery_intention_date:
                # Calculate 21 clear days (exclude service date and recovery date) — Table 80
                from datetime import timedelta as td
                clear_days = 21
                rec.clear_days_end_date = rec.notice_served_date + td(days=clear_days)

            rec.state = 'notice_active'

    def action_cure_notice(self):
        """Mark notice as cured. Table 37, LEG-025."""
        for rec in self:
            rec.notice_cured = True
            rec.state = 'cured'

    def action_mark_repossessed(self):
        """Mark goods as repossessed. Tables 56-57."""
        for rec in self:
            if not rec.repossessed_value:
                raise ValidationError(_('Repossessed goods value is required.'))
            rec.state = 'goods_recovered'

    def action_valuate_goods(self):
        """Value repossessed goods. Table 56, step 2."""
        for rec in self:
            if not rec.repossessed_value:
                raise ValidationError(_('Goods value is required.'))
            rec.state = 'goods_valued'

    def action_mark_closed(self):
        """Close the case."""
        for rec in self:
            rec.state = 'closed'

     # ── Create override ─────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env.ir.sequence.next_by_code('hp.case') or '/'
        return super().create(vals_list)
