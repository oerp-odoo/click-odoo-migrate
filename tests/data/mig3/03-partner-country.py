def migrate(env, shared_data):
    partner_ids = [shared_data['01-partner-parent'], shared_data['02-partner-contact']]
    country_id = env.ref('base.lt')
    env['res.partner'].browse(partner_ids).write({'country_id': country_id})
