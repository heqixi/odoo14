from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    #@api.multi
    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        for rec in self:
            stock_location = self.env['stock.location'].sudo().search([('partner_id', '=', rec.id)])
            for e in stock_location:
                e.write({
                    'partner_id': rec.id
                })
        return result
