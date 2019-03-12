Feature: Organization Client can remove Organization Service Policy
  In order to manage the Authorization Policy of an Organization Service
  As an Organization Client
  I can remove the Authorization Policy of an Organization Service

  Background:
    Given I created an Organization Service

  Scenario: Removing Policy when there is no Policy results in blank Policy
    When I remove the Policy for the Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has no requirement for number of factors

  Scenario: Removing existing Policy results in blank policy
    Given the Organization Service Policy is set to require 1 factor
    And I set the Policy for the Organization Service
    When I remove the Policy for the Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has no requirement for number of factors

  Scenario: Removing the policy for invalid Service throws Forbidden
    When I attempt to remove the Policy for the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a ServiceNotFound error occurs
