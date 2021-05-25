# Family Protection Order API

## Overview

The API provides an interface into the database for Family Protection Order.

Calls to the api must be in the format as follows:
> http://serverUrl:port/form?name=nameOfForm

Here is an example
> http://localhost:8000/form?name=notice-to-disputant-response

## Development

The API is developed in Django/Python, using a Visual Studio 2017 project.

The database is bare after docker build. Run the following script within the container to add data.
```bash
./loadFixtures
```

## Development Deployment Environment

To deploy Family Protection Order on an instance of OpenShift, see [the instructions](../RunningLocal.md) in the file RunningLocal.md.

- [Schema Spy](https://virtual-hearing-form-schema-dev.apps.silver.devops.gov.bc.ca/)

## Database Migrations

Migrations are triggered automatically when the Django/Python container is deployed.  The process it triggered by wrapper code injected as part of the s2i-python-container build; https://github.com/sclorg/s2i-python-container/blob/master/3.6/s2i/bin/run

## ToDo:
- The auto-generated views are constructed using generics and a number of mixins.
  - Determine if there is a better way to do this.  Since it's not as clean as something constructed from ModelSerializer or HyperlinkedModelSerializer.

## Testing:
While updating the template you need to load it into the active container like this
```bash
docker cp notice-to-disputant-response.html fpo_fpo-api_1:/opt/app-root/src/templates/
```

Then send some test data
```bash
  curl -X POST --output notice-to-disputant-response.pdf \
    -H 'Accept: application/pdf' \
    -H 'Content-Type: application/json' \
    -d '@test-data.json' \
    "http://localhost:8000/form?name=notice-to-disputant-response"
```

These commands are in the files, respectively:
- templates/update-template.sh
- templates/test.sh

If you are using an editor like Vim, you can run the following command that executes both scripts on every save:
```ed
autocmd BufWritePost * execute '!./update-template.sh && ./test.sh'
```

To hot load the python code you need to start the default server in the container:
```bash
docker exec -it fpo_fpo-api_1 /bin/bash
python manage.py runserver 0:8000
```
This opens a new server on port 8000

Then in the editor have the appropriate file load into the container
```ed
autocmd BufWritePost * execute '!./update-views.sh'
```
