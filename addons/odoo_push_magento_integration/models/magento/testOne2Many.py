from odoo import models,fields

class LibraryBook(models.Model):
    # ...
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
    )

