import click
import pytest
from click.testing import CliRunner
from click_odoo import OdooEnvironment

from xodoo import migration


def assert_mig_entries_count(cr, name, expected):
    cr.execute(
        """
        SELECT count(*)
        FROM xodoo_migration
        WHERE name = %s""",
        (name,),
    )
    assert cr.fetchone()[0] == expected


def test_01_migrate_multiple_times(odoodb, path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN
    with OdooEnvironment(database=odoodb, rollback=True) as env:
        migrated = migration.migrate(env, str(path_mig_1))
        migrated_2 = migration.migrate(env, str(path_mig_1))
        # THEN
        cr = env.cr
        cr.execute("SELECT to_regclass('public.xodoo_migration')")
        assert cr.fetchone()[0]
        assert migrated == [
            path_mig_1 / "2022-02-19-partners-companies.py",
            path_mig_1 / "2022-02-20-titles.py",
        ]
        assert migrated_2 == []
        assert_mig_entries_count(cr, "2022-02-19-partners-companies", 1)
        assert_mig_entries_count(cr, "2022-02-20-titles", 1)
        partners_cnt = env["res.partner"].search_count(
            [("name", "in", ("mig-partner-111", "mig-partner-222"))]
        )
        assert partners_cnt == 2
        assert env.ref("base.main_company").name == "mig-company-111"
        titles_cnt = env["res.partner.title"].search_count(
            [("name", "in", ("mig-title-111", "mig-title-222"))]
        )
        assert titles_cnt == 2


def test_02_migrate_single_file(odoodb, path_test_data):
    # GIVEN
    path_mig_file_1 = path_test_data / "mig1/2022-02-19-partners-companies.py"
    # WHEN
    with OdooEnvironment(database=odoodb, rollback=True) as env:
        cr = env.cr
        migrated = migration.migrate(env, str(path_mig_file_1))
        # THEN
        assert migrated == [path_mig_file_1]
        assert_mig_entries_count(cr, "2022-02-19-partners-companies", 1)
        assert_mig_entries_count(cr, "2022-02-20-titles", 0)
        partners_cnt = env["res.partner"].search_count(
            [("name", "in", ("mig-partner-111", "mig-partner-222"))]
        )
        assert partners_cnt == 2
        assert env.ref("base.main_company").name == "mig-company-111"
        titles_cnt = env["res.partner.title"].search_count(
            [("name", "in", ("mig-title-111", "mig-title-222"))]
        )
        assert titles_cnt == 0


def test_03_migrate_with_shared_data(odoodb, path_test_data):
    # GIVEN
    path_mig_3 = path_test_data / "mig3"
    # WHEN
    with OdooEnvironment(database=odoodb, rollback=True) as env:
        migrated = migration.migrate(env, str(path_mig_3))
        # THEN
        cr = env.cr
        cr.execute("SELECT to_regclass('public.xodoo_migration')")
        assert cr.fetchone()[0]
        assert migrated == [
            path_mig_3 / "01-partner-parent.py",
            path_mig_3 / "02-partner-contact.py",
            path_mig_3 / "03-partner-country.py",
        ]
        assert_mig_entries_count(cr, "01-partner-parent", 1)
        assert_mig_entries_count(cr, "02-partner-contact", 1)
        assert_mig_entries_count(cr, "03-partner-country", 1)
        ResPartner = env["res.partner"]
        partner_parent = ResPartner.search([("name", "=", "mig-partner-parent-111")])
        assert len(partner_parent) == 1
        assert partner_parent.is_company is True
        assert partner_parent.country_id.code == "LT"
        partner_contact = partner_parent.child_ids
        assert len(partner_contact) == 1
        assert partner_contact.is_company is False
        assert partner_contact.name == "mig-partner-contact-222"
        assert partner_contact.country_id.code == "LT"


def test_04_migrate_fail(odoodb, path_test_data):
    # GIVEN
    path_mig_2 = path_test_data / "mig2"
    # WHEN
    with OdooEnvironment(database=odoodb, rollback=True) as env:
        cr = env.cr
        with pytest.raises(
            click.ClickException, match=r"Something went wrong migrating '.+':"
        ):
            migration.migrate(env, str(path_mig_2))
            # THEN
            cr.execute("SELECT to_regclass('public.xodoo_migration')")
            assert cr.fetchone()[0] is None
            # Should not be changed.
            assert env.ref("base.res_partner_category_11").name == "Services"


def test_05_migrate_force(odoodb, path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    with OdooEnvironment(database=odoodb, rollback=True) as env:
        cr = env.cr
        migration.init_migration_table(cr)
        cr.execute(
            "INSERT INTO xodoo_migration VALUES ('2022-02-19-partners-companies')"
        )
        cr.execute("INSERT INTO xodoo_migration VALUES ('2022-02-20-titles')")
        # WHEN
        # Forcing only one.
        migrated = migration.migrate(
            env, str(path_mig_1), force=["2022-02-19-partners-companies"]
        )
        # THEN
        assert migrated == [path_mig_1 / "2022-02-19-partners-companies.py"]
        partners_cnt = env["res.partner"].search_count(
            [("name", "in", ("mig-partner-111", "mig-partner-222"))]
        )
        assert partners_cnt == 2
        assert env.ref("base.main_company").name == "mig-company-111"
        titles_cnt = env["res.partner.title"].search_count(
            [("name", "in", ("mig-title-111", "mig-title-222"))]
        )
        assert titles_cnt == 0


def test_06_migrate_with_cli_rollback(odoodb, odoocfg, path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN
    res = CliRunner().invoke(
        migration.main,
        [
            str(path_mig_1),
            "-d",
            odoodb,
            "-c",
            str(odoocfg),
            # This is to not save any changes in DB.
            "--rollback",
            "-f",
            "2022-02-19-partners-companies",
            "-f",
            "2022-02-20-titles",
            "-s",
            "natsorted",
        ],
    )
    # THEN
    assert res.exit_code == 0
    mig_out = res.stdout.strip().split("\n")
    assert mig_out[0] == (
        "Force Migrating: 2022-02-19-partners-companies, 2022-02-20-titles"
    )
    assert mig_out[1] == "Migrating: 2022-02-19-partners-companies"
    assert mig_out[2] == "Migrating: 2022-02-20-titles"
    with OdooEnvironment(database=odoodb) as env:
        cr = env.cr
        cr.execute("SELECT to_regclass('public.xodoo_migration')")
        assert cr.fetchone()[0] is None
        partners_cnt = env["res.partner"].search_count(
            [("name", "in", ("mig-partner-111", "mig-partner-222"))]
        )
        assert partners_cnt == 0
        assert env.ref("base.main_company").name == "YourCompany"
        titles_cnt = env["res.partner.title"].search_count(
            [("name", "in", ("mig-title-111", "mig-title-222"))]
        )
        assert titles_cnt == 0


# This test is to always run last as it does not rollback transaction,
# so we leave for odoodb fixter to clean up (by dropping db)
def test_07_migrate_with_cli_commit(odoodb, odoocfg, path_test_data):
    # GIVEN
    path_mig_1 = path_test_data / "mig1"
    # WHEN
    res = CliRunner().invoke(
        migration.main,
        [
            str(path_mig_1),
            "-d",
            odoodb,
            "-c",
            str(odoocfg),
            # Forcing just to make sure argument is handled properly.
            "-f",
            "2022-02-19-partners-companies",
            "-f",
            "2022-02-20-titles",
            "-s",
            "natsorted",
        ],
    )
    # THEN
    assert res.exit_code == 0
    mig_out = res.stdout.strip().split("\n")
    assert mig_out[0] == (
        "Force Migrating: 2022-02-19-partners-companies, 2022-02-20-titles"
    )
    assert mig_out[1] == "Migrating: 2022-02-19-partners-companies"
    assert mig_out[2] == "Migrating: 2022-02-20-titles"
    with OdooEnvironment(database=odoodb) as env:
        cr = env.cr
        cr.execute("SELECT to_regclass('public.xodoo_migration')")
        assert cr.fetchone()[0]
        assert_mig_entries_count(cr, "2022-02-19-partners-companies", 1)
        assert_mig_entries_count(cr, "2022-02-20-titles", 1)
        partners_cnt = env["res.partner"].search_count(
            [("name", "in", ("mig-partner-111", "mig-partner-222"))]
        )
        assert partners_cnt == 2
        assert env.ref("base.main_company").name == "mig-company-111"
        titles_cnt = env["res.partner.title"].search_count(
            [("name", "in", ("mig-title-111", "mig-title-222"))]
        )
        assert titles_cnt == 2
