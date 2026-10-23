Implement this approved shipit plan with `code-implement`:

> **Goal:** rate-limit sign-in to 5 attempts per IP per minute on `POST /session`,
> answering 429 beyond that. Use current Rails best practices.
> **Files:** `app/controllers/sessions_controller.rb` · Edit · throttle `create`
> (AC1) · analogue `config/initializers/rack_attack.rb:4`
> **Tests:** `test/integration/sessions_rate_limit_test.rb` + 6th attempt gets 429
> · `docs/code/rules/tests/integration.md` · AC1

`Gemfile.lock` pins `rails (7.1.3)` and `rack-attack (6.7.0)`. The analogue
throttles `/api/` requests by IP with `Rack::Attack.throttle`.

At the end, list every library documentation lookup you made, with the version
you asked about, or say none was possible.
