def migrate(env, shared_data):
    env['res.partner.title'].create({'name': 'mig-title-111'})
    env.ref("base.res_partner_title_doctor").name = 'mig-title-222'
