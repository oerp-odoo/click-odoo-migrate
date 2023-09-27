def migrate(env, shared_data):
    parent_id = shared_data["01-partner-parent"]
    contact = env["res.partner"].create(
        {
            "name": "mig-partner-contact-222",
            "is_company": False,
            "parent_id": parent_id
        }
    )
    return contact.id
