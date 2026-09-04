{
    'name': 'Hire Purchase',
    'version': '19.0.1.0.0',
    'category': 'Sales/Hire Purchase',
    'summary': 'Trinidad & Tobago Hire Purchase sales with legal controls, IFRS finance income, and statutory compliance for Furniture Plus.',
    'description': """
        Hire Purchase Module for Odoo 19 Enterprise (T&T) - Furniture Plus
        ===============================================================
        Extends Odoo Sales with a controlled Hire Purchase payment term.
        A quotation cannot become a sales order until the Hire Purchase
        application is approved, the customer and guarantor have signed
        the agreement, the required deposit is received, and all delivery
        conditions are satisfied.

        Five separate records with different responsibilities:
             - Sales Quotation
             - Hire Purchase Plan
             - Hire Purchase Application
             - Signed Hire Purchase Agreement
             - Active Hire Purchase Contract

        One collections case manages arrears, statutory notices, legal
        review and repossession. Prevents a salesperson from bypassing
        credit, legal or accounting controls.

        At delivery: one contractual receivable covering goods, VAT and
        any approved finance charge. Instalment maturity lines generated
        from the signed payment schedule. Product sale and VAT recognised
        at delivery; finance charge held as unearned income and recognised
        over time (IFRS for SMEs).

        See Odoo_19_Hire_Purchase_Requirements_Specification_1.docx
        for full functional, legal-control and accounting requirements.
    """,
    'author': 'NioDigital / Furniture Plus',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'account',
        'contacts',
    ],
    'data': [
        # Security
        'security/hire_purchase_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/hire_purchase_payment_term_data.xml',
        'data/account_journal_data.xml',
        'data/account_account_data.xml',
        'data/cron.xml',

        # Views
        'views/hp_plan_views.xml',
        'views/hp_application_views.xml',
        'views/hp_contract_views.xml',
        'views/hp_agreement_views.xml',
        'views/hp_case_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',

        # Reports
        'reports/hp_statement_report.xml',
        'reports/hp_schedule_report.xml',

        # Wizards
        'wizard/hp_application_confirm_wizard_view.xml',
        'wizard/hp_reschedule_wizard_view.xml',
        'wizard/hp_early_settlement_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
}
