Feature: Service Client can verify a TOTP code for a user
  In order to verify User TOTP codes
  As a Service Client
  I can request a User TOTP code to be verified and return a result

  Background:
    Given I created a Directory
    And I created a Directory Service
    And I have created a User TOTP

  Scenario: Verifying a valid User TOTP code returns true
    When I verify a TOTP code with a valid code
    Then the TOTP verification response is True

  Scenario: Verifying an invalid User TOTP code returns false
    When I verify a TOTP code with an invalid code
    Then the TOTP verification response is False

  Scenario: Verifying a code for a User that does not have a TOTP secret
    When I verify a TOTP code with an invalid User
    Then an EntityNotFound error occurs