from odoo import models, tools
from odoo.exceptions import UserError
from odoo.http import request
from ...utils.magento.rest import Client


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _create_shipment(self, sale_order_increment_id, client, move_line_ids):
        item_id_information = {}
        order_magento = client.get(
            "rest/V1/orders?searchCriteria[filter_groups][0][filters][0][field]=increment_id&searchCriteria[filter_groups][0][filters][0][value]=" +
            sale_order_increment_id, arguments='')
        current_magento_order = order_magento['items'][0]
        for e in current_magento_order["items"]:
            item_id_information[e["sku"]] = e["item_id"]

        data = {}
        for e in move_line_ids:
            if e.location_id.is_magento_source == True and e.product_id.default_code in item_id_information:
                if str(e.location_id.id) not in data:
                    if e.product_id.on_magento == True:
                        data[str(e.location_id.id)] = [{
                            "order_item_id": item_id_information[e.product_id.default_code],
                            "qty": e.qty_done
                        }]
                else:
                    data[str(e.location_id.id)].append({
                        "order_item_id": item_id_information[e.product_id.default_code],
                        "qty": e.qty_done
                    })
        if len(data) > 0:
            for a in data:
                params = {
                    "items": data[a],
                    "arguments": {
                        "extension_attributes": {
                            "source_code": "odoo_location_" + a
                        }
                    }
                }
                url = 'rest/V1/order/' + str(current_magento_order['entity_id']) + '/ship'
                client.post(url, arguments=params)

    def _update_qty_product_source_magento(self, client, move_line_ids):
        for e in move_line_ids:
            source_location_id = e.location_id.id
            destination_location_id = e.location_dest_id.id
            data = []
            if e.location_id.is_magento_source == True and e.product_id.on_magento == True:
                stock_quant_source_location = request.env['stock.quant'].search(
                    [('product_id', '=', e.product_id.id), ('location_id', '=', source_location_id)])
                data.append({
                    "sku": e.product_id.default_code,
                    "source_code": "odoo_location_" + str(source_location_id),
                    "quantity": stock_quant_source_location.quantity,
                    "status": 1
                })
            if e.location_dest_id.is_magento_source == True and e.product_id.on_magento == True:
                stock_quant_destination_location = request.env['stock.quant'].search(
                    [('product_id', '=', e.product_id.id), ('location_id', '=', destination_location_id)])
                data.append(
                    {
                        "sku": e.product_id.default_code,
                        "source_code": "odoo_location_" + str(destination_location_id),
                        "quantity": stock_quant_destination_location.quantity,
                        "status": 1
                    }
                )
            if len(data) == 0:
                return
            else:
                try:
                    params = {
                        "sourceItems": data
                    }
                    client.post('rest/V1/inventory/source-items', arguments=params)
                except Exception as e:
                    raise UserError(('Not create source to magento - %s') % tools.ustr(e))

    def action_done(self):
        super(StockPicking, self).action_done()
        magento_backend = request.env['magento.backend'].search([], limit=1)
        client = Client(magento_backend.web_url, magento_backend.access_token, True)
        if self.sale_id.id:
            if magento_backend.prefix_sale_order in self.sale_id.name:
                self._create_shipment(self.sale_id.name.replace(magento_backend.prefix_sale_order, ''),
                                      client, self.move_line_ids)
        self._update_qty_product_source_magento(client, self.move_line_ids)

    def action_toggle_is_locked(self):
        magento_backend = request.env['magento.backend'].search([], limit=1)
        if self.sale_id:
            if magento_backend.prefix_sale_order in self.sale_id.name:
                raise UserError(
                    'You cannot unlock the delivery of the magento synchronization order')
            else:
                super(StockPicking, self).action_toggle_is_locked()
        else:
            super(StockPicking, self).action_toggle_is_locked()


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def do_scrap(self):
        result = super(StockScrap, self).do_scrap()
        data = []
        magento_backend = request.env['magento.backend'].search([], limit=1)
        client = Client(magento_backend.web_url, magento_backend.access_token, True)
        if self.location_id.is_magento_source == True and self.product_id.on_magento == True:
            stock_quant_source_location = request.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id)])
            data.append({
                "sku": self.product_id.default_code,
                "source_code": "odoo_location_" + str(self.location_id.id),
                "quantity": stock_quant_source_location.quantity,
                "status": 1
            })
        if len(data) > 0:
            try:
                params = {
                    "sourceItems": data
                }
                client.post('rest/V1/inventory/source-items', arguments=params)
            except Exception as e:
                raise UserError(('Not create source to magento - %s') % tools.ustr(e))
        return result
