def migrate(env, shared_data):
    ResPartner = env['res.partner']
    ResPartner.create([{'name': 'mig-partner-111'}, {'name': 'mig-partner-222'}])
    env.cr.execute(
        "UPDATE res_company set name = 'mig-company-111' WHERE id = %s",
        (env.ref('base.main_company').id,)
    )
