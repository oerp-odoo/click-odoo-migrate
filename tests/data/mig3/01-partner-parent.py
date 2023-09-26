def migrate(env, shared_data):
    partner = env["res.partner"].create(
        {"name": "mig-partner-parent-111", "is_company": True}
    )
    return partner.id
