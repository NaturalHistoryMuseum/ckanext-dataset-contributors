<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-dataset-contributors

[![Travis](https://img.shields.io/travis/NaturalHistoryMuseum/ckanext-dataset-contributors/main.svg?style=flat-square)](https://travis-ci.org/NaturalHistoryMuseum/ckanext-dataset-contributors)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-dataset-contributors/main.svg?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-dataset-contributors)
[![CKAN](https://img.shields.io/badge/ckan-2.9.0a-orange.svg?style=flat-square)](https://github.com/ckan/ckan)

_A CKAN extension that links contributors and their ORCIDs to datasets._


# Overview

This extension allows authors to associate a list of contributors with a dataset, and (optionally) links those contributors with an [ORCID](https://orcid.org) identifier.

A new database table (`contributors`) is added:

id|surname|given_names|affiliations|orcid|user_id
--|-------|-----------|------------|-----|-------
uuid|text|text|jsonb (nullable)|text (unique, nullable)|text (foreign key on `users`, nullable)

A list of contributor IDs is stored in the `contributors` field in `package_extras`.

NB: this plugin was developed on an alpha version of CKAN 2.9 and does not yet implement all the changes.

# Installation

Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

1. Clone the repository into the `src` folder:

  ```bash
  cd $INSTALL_FOLDER/src
  git clone https://github.com/NaturalHistoryMuseum/ckanext-dataset-contributors.git
  ```

2. Activate the virtual env:

  ```bash
  . $INSTALL_FOLDER/bin/activate
  ```

3. Install the requirements from requirements.txt:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-dataset-contributors
  pip install -r requirements.txt
  ```

4. Run setup.py:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-dataset-contributors
  python setup.py develop
  ```

5. Add 'dataset_contributors' to the list of plugins in your `$CONFIG_FILE`:

  ```ini
  ckan.plugins = ... dataset_contributors
  ```

## Additional steps

### SOLR Faceting
You will need to add a `contributors` field to your `schema.xml` for faceting to work.

```xml
<schema>
    <fields>
        <...>
        <field name="contributors" type="string" indexed="true" stored="true" multiValued="true"/>
        <...>
    </fields>
<...>
<copyField source="contributors" dest="text"/>
</schema>
```

Add the above lines to your SOLR `schema.xml` and restart SOLR. You will also have to enable the config option to see this in the UI (see below).

### FontAwesome
The templates in this plugin use the ORCID icon from [fontawesome 5.11+](https://github.com/FortAwesome/Font-Awesome/releases/tag/5.11.0). To use them, you'll have to make fontawesome 5.11+ available (e.g. in your main theme plugin).

# Configuration

These are the options that can be specified in your .ini config file.
NB: setting `ckanext.dataset_contributors.debug` to `True` means that the API accesses [sandbox.orcid.org](https://sandbox.orcid.org) instead of [orcid.org](https://orcid.org). Although both run by the ORCID organisation, these are _different websites_ and you will need a separate account/set of credentials for each. It is also worth noting that you will not have access to the full set of authors on the sandbox.

## API credentials [REQUIRED]

Name|Description|Options
--|--|--
`ckanext.dataset_contributors.orcid_key`|Your ORCID API client ID/key||
`ckanext.dataset_contributors.orcid_secret`|Your ORCID API client secret||

## Optional

Name|Description|Options|Default
--|--|--|--
`ckanext.dataset_contributors.debug`|If true, use sandbox.orcid.org (for testing)|True/False|True
`ckanext.dataset_contributors.enable_faceting`|If true, enable filtering datasets by contributor names (requires change to SOLR schema)|True/False|False

# Usage

## Actions

### `contributor_create`
Add a new contributor to the database. Default auth allows all logged-in users.

```python
data_dict = {
    'surname': 'SURNAME',
    'given_names': 'GIVEN NAMES',
    'affiliations': ['AFFILIATION1', 'AFFILIATION2'],
    'orcid': '0000-0000-0000-0000',
    'user_id': 'USER_ID'
}

toolkit.get_action('contributor_create')({}, data_dict)
```

### `contributor_show`
Get the details of a contributor in the database (as a dict). Default auth allows anonymous access.

```python
data_dict = {
    'id': 'CONTRIBUTOR_ID'
}

toolkit.get_action('contributor_show')({}, data_dict)
```

### `contributor_update`
Update the details of a contributor in the database. Default auth only allows sysadmins.

```python
# everything except 'id' is optional and will just not be updated if omitted
data_dict = {
    'id': 'CONTRIBUTOR_ID',
    'surname': 'SURNAME',
    'given_names': 'GIVEN NAMES',
    'affiliations': ['AFFILIATION1', 'AFFILIATION2'],
    'orcid': '0000-0000-0000-0000',
    'user_id': 'USER_ID'
}

toolkit.get_action('contributor_update')({}, data_dict)
```

### `contributor_orcid_update`
Update the details of a contributor using information pulled from the ORCID API. Requires the contributor to have a valid ORCID identifier. Default auth allows logged-in users.

```python
data_dict = {
    'id': 'CONTRIBUTOR_ID'
}

toolkit.get_action('contributor_orcid_update')({}, data_dict)
```

## Commands

### `orcid-sync`
1. `pull`: update contributor records with data pulled from the ORCID API.
Specific ORCIDs to be updated can be passed as arguments, or the command can be used by itself to update all records with an associated ORCID.
```sh
paster --plugin=ckanext-dataset-contributors orcid-sync pull [ORCID1] [ORCID2] [...] -c $CONFIG_FILE

# e.g. update records with ORCIDs 0000-0000-0000-0000 and 1111-1111-1111-1111
paster --plugin=ckanext-dataset-contributors orcid-sync pull 0000-0000-0000-0000 1111-1111-1111-1111 -c $CONFIG_FILE

# e.g. update all records with an ORCID
paster --plugin=ckanext-dataset-contributors orcid-sync pull -c $CONFIG_FILE
```

### `contributor-migrate`
1. `existing`: attempt to migrate contributors listed as `package_extras` to the new format. Unlikely to be relevant in the majority of cases. **Requires manual input; do not use in unattended scripts**.
```sh
paster --plugin=ckanext-dataset-contributors migrate-contributors existing -c $CONFIG_FILE
```
The `spacy` package is required to run this command. This is not installed by default, but instead is listed in `dev-requirements.txt` (along with the version of `requests` it requires).

## Templates

Add the following block to `theme/templates/package/snippets/package_metadata_fields.html` in your main theme plugin:
```jinja2
{% block package_custom_fields_contributors %}
    {{ super() }}
{% endblock %}
```

And this block to `theme/templates/package/snippets/additional_info.html`:
```jinja2
{% block contributors_row %}
    {{ super() }}
{% endblock %}
```

# Testing

To run the tests, use nosetests inside your virtualenv. The `--nocapture` flag will allow you to see the debug statements.
```bash
nosetests --ckan --with-pylons=$TEST_CONFIG_FILE --where=$INSTALL_FOLDER/src/ckanext-dataset-contributors --nologcapture --nocapture
```
