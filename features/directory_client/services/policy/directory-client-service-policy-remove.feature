Feature: Directory Client can remove Directory Service Policy
  In order to manage the Authorization Policy of a Directory Service
  As a Directory Client
  I can remove the Authorization Policy of a Directory Service

  Background:
    Given I created a Directory
    And I created a Directory Service

  Scenario: Removing Policy when there is no Policy results in blank Policy
    When I remove the Policy for the Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has no requirement for number of factors

  Scenario: Removing existing Policy results in blank policy
    Given the Directory Service Policy is set to require 1 factor
    And I set the Policy for the Directory Service
    When I remove the Policy for the Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has no requirement for number of factors

  Scenario: Removing the policy for invalid Service throws Forbidden
    When I attempt to remove the Policy for the Directory Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a ServiceNotFound error occurs
