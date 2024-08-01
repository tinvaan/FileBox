# Filebox

FileBox is a simple personal, web-based, api-driven file/document management service. <br/>
FileBox API is hosted publicly at <https://filebox-production.up.railway.app>

## API Usage

The Filebox service exposes the following API endpoints,

- `POST /uploads` - Upload a new document (supported formats: `pdf`, `jpg`, `png`)

    ```shell
    -H { 'Content-Type': 'multipart/form-data' }
    -d { 'files': <file content> }
    ```

- `GET /uploads` - Lists all uploads to the service.
- `GET /uploads/<id>` - Lists information about the specified(`<id`>) upload.
- `PUT /uploads/<id>` - Modify information about an upload item.
- `DELETE /uploads/<id>` - Delete a specified upload item.

## Development

FileBox is built using `Python` (`3.10` and above) and uses an in-memory`MongoDB` datastore (i.e `mongomock`) for persistence.

To run the service locally,

```shell
➞ git clone https://github.com/tinvaan/filebox.git
➞ cd filebox
➞ pip install -r requirements.txt
```

Then launch the `run.py` script,

```shell
➞ python run.py
* Serving Flask app 'filebox'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5050
 * Running on http://192.168.18.4:5050
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 422-966-127
```

Optionally, you may also use the provided `Dockerfile` to run the service in a container.

```shell
➞  docker build . -t filebox:latest
➞  docker run -p 5050:5050 filebox:latest
 * Serving Flask app 'filebox'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5050
 * Running on http://172.17.0.2:5050
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 124-124-600
```

Navigate to <http://localhost:5050> to access the API.

## Unit Tests

The necessary dependencies for running unit tests are listed in `dev-requirements.txt` file. Install them using `pip`.

```shell
➞  pip install -r dev-requirements.txt
```

Now, the unit tests can be invoked via the `pytest` runner.

```shell
➞  pytest --disable-warnings -s tests                                                                 🐍 filebox@teleskop  [git:master] ✖
Test session starts (platform: darwin, Python 3.10.14, pytest 8.3.2, pytest-sugar 1.0.0)
rootdir: /Users/harish/Workspaces/interviews/Teleskop/FileBox
plugins: sugar-1.0.0
collected 16 items

 tests/test_models_uploads.py ✓✓✓✓✓✓✓✓✓                                                                                 56% █████▋
 tests/test_views_uploads.py ✓✓✓✓✓✓✓                                                                                   100% ██████████

Results (0.28s):
      16 passed
```

## Deployment

Builds are automatically triggered on every push to the `master` branch and are automatically deployed at <https://filebox-production.up.railway.app>

## Future improvements

- Support batch/bulk operations (viz. create & delete)
- Authentication for users & session management
- Configure CI/CD workflows
- Track code coverage
- Use `tox` for test environments

## Contributing

Report issues via the Github issue tracker and or reach out to Harish Navnit <harishnavnit@gmail.com> for any queries. Pull requests are welcome!
