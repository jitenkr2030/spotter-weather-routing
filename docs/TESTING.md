# Testing and Verification

## Backend Tests

The previously recorded verification run completed with 15 passing
backend tests.

Run the test suite using the project's configured Python environment
and Django settings. For a standard Django project:

```bash
python manage.py test
```

If the project uses a dedicated virtual environment, activate it
before running the command.

## Frontend Build

Run the build from the frontend directory containing package.json:

```bash
npm run build
```

The frontend build was previously verified successfully.

## Live Deployment Checks

Frontend:

```bash
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' \
  https://frontend-ten-kappa-22.vercel.app/
```

Backend health endpoint:

```bash
curl -i \
  https://spotter-weather-routing-f4wz9.faable.link/api/health/
```

Provider status:

```bash
curl -i \
  https://spotter-weather-routing-f4wz9.faable.link/api/providers/
```

## Manual Acceptance Checks

- [ ] Frontend loads without a fatal application error.
- [ ] Route inputs can be entered and submitted.
- [ ] Route results are displayed when a valid request succeeds.
- [ ] Weather and risk information are displayed when returned.
- [ ] Provider errors are handled without crashing the interface.
- [ ] Map and route interactions work as implemented.
- [ ] The deployed frontend can communicate with the backend.

## Reporting Results

Record the date, environment, commands, test count, failures and
known limitations for the final submission.

The previously recorded results are 15 passing backend tests,
a successful frontend build and successful browser verification.
Repeat the checks before submission if the code has changed.
