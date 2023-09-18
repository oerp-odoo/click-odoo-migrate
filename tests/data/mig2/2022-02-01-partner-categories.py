def migrate(env):
    # Change from "Services" name.
    env.ref('base.res_partner_category_11').name = 'mig-services-111'
