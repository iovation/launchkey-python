Feature: Directory Client can remove a TOTP configuration for user
  In order to manage User TOTP
  As a Directory Client
  I can request a TOTP configuration to be removed for a user

  Background:
    Given I created a Directory

  Scenario: Deleting TOTP succeeds
    When I make a User TOTP delete request
    Then there are no errors
