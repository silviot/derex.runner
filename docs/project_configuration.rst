Project Configuration
=====================

A project is the main starting point to use derex.

It can define custom packages (like xblocks) to install, themes, database
fixtures and plugins.

A minimal Project
-----------------

The bare minimum project is a directory with a single yaml file in it, stating
the project name.

For example, the `minimal` project included with derex.runner looks like this:

| minimal
| ├─ derex.config.yaml


The yaml file contents are:

.. code-block:: yaml

    project_name: minimal

Custom requirements
-------------------

Additional requirements need to be specified in a `requirements` directory.

TODO expand this section

Custom settings
---------------

A `settings` directory can be added to the project, containing files that can be
used as django settings for the LMS/CMS.

TODO expand this section

Variables
---------

A common need is to be able to share a configuration value among all containers.

The project config file can specify variables that will be passed on to all
containers, including ones defined by plugins.

For each defined variable you need to specify the value it should have for each
possible settings value.

For instance the following config will drive the variable DEREX_LMS_SITE_NAME.

.. code-block:: yaml

    variables:
    lms_site_name:
        production: onlinecourse.example.com
        staging: staging.onlinecourse.example.com

In turn the default derex config files for LMS will look into all environment variables
of the form DEREX_LMS_VARIABLE_NAME and set the settings value VARIABLE_NAME accordingly.
