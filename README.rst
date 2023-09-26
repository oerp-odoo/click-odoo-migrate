xodoo
=====

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

``xodoo`` is collection of various scripts intended to be used for odoo.
It is based on ``click-odoo`` to connect and manage odoo.

Scripts
~~~~~~~

xodoo-migrate
-------------

Migration tool intended to run various migration scripts for Odoo. It should
be used when it does not make sense to run module migrations (e.g. need
to generate some customer specific data that is not directly related with any
module).

.. code::

    Usage: xodoo-migrate [OPTIONS] PATH

      PATH:  migration file or directory of migration files.

      Migration file must end with .py extension and must have 'migrate' function
      that expects 'env' and 'shared_data' argument.

      'shared_data' argument is a dictionary that collects previous
      migration scripts returned values (key is migration script name).
      If return (of 'migrate' function) is None, it is not included in
      shared_data.

    Options:
      -c, --config FILE          Specify the Odoo configuration file. Other ways
                                 to provide it are with the ODOO_RC or
                                 OPENERP_SERVER environment variables, or
                                 ~/.odoorc (Odoo >= 10) or ~/.openerp_serverrc.
      -d, --database TEXT        Specify the database name. If present, this
                                 parameter takes precedence over the database
                                 provided in the Odoo configuration file.
      --log-level TEXT           Specify the logging level. Accepted values depend
                                 on the Odoo version, and include debug, info,
                                 warn, error.  [default: warn]
      --logfile FILE             Specify the log file.
      --rollback                 Rollback the transaction even if the script does
                                 not raise an exception. Note that if the script
                                 itself commits, this option has no effect. This
                                 is why it is not named dry run. This option is
                                 implied when an interactive console is started.
      -f, --force TEXT           Specify migration file names (without extension)
                                 to force migrate. It will migrate even if it was
                                 already migrated. Must be subset of migration
                                 files provided in a path.
      -s, --sort-algorithm TEXT  Sort algorithm to sort migration files before
                                 migration. Possible choices: sorted, natsorted
      --help                     Show this message and exit.

If you use ``--rollback`` option, make sure you do not run ``cr.commit()`` in
your scripts, otherwise it will have no effect (script changes are automatically
committed if they do not fail at the end of transaction).
