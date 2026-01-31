# orders.feature — worked example shipped by the BDD testing pack.
#
# This scenario is LANGUAGE-NEUTRAL and RUNNER-AGNOSTIC: it names no step
# runner, no container library, and no transport detail. The active STACK pack
# supplies the binding that executes it (its Gherkin runner) and brings up the
# real database (its container library). The same .feature composes with any
# stack pack unchanged.
#
# It demonstrates the strategy this pack carries: outside-in scenarios, one per
# boundary behaviour, each backed by a REAL (containerised) dependency — no
# mocking a containerisable service.

Feature: Placing an order persists it and emits an event
  A client can place an order; a valid order is stored and announced, and an
  invalid order is rejected with nothing left behind.

  Background:
    Given a running orders service backed by a real database

  Scenario: a valid order is accepted
    When a client places a valid order
    Then the order is persisted
    And an "order.placed" event is recorded

  Scenario: a malformed order is rejected
    When a client places an order with no line items
    Then the request is rejected with a validation error
    And nothing is persisted

  Scenario: the order cannot be placed when the datastore is unavailable
    Given the order datastore is unavailable
    When a client places a valid order
    Then the request fails with a retryable error
    And no "order.placed" event is recorded
