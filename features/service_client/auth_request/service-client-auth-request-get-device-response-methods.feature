Feature: Service Client Authorization Request: Get Device Response Policy
  In order to understand an auth response
  As a Directory Service
  I can retrieve an Authorization Requests that been responded to and determine
  the policy that was used

  Background:
    Given I created a Directory
    And I have added an SDK Key to the Directory
    And I created a Directory Service
    And I have a linked Device

  Scenario: Verify that an auth request with no policy contains the expected methods
    When I make an Authorization request
    And I approve the auth request
    And I get the response for the Authorization request
    Then the Authorization response should contain the following methods:
      | Method      | Set   | Active | Allowed | Supported  | User Required | Passed | Error |
      | wearables   | False | False  | True    | True       | Null          | Null   | Null  |
      | geofencing  | Null  | True   | True    | True       | Null          | Null   | Null  |
      | locations   | False | False  | True    | True       | Null          | Null   | Null  |
      | pin_code    | False | False  | True    | True       | Null          | Null   | Null  |
      | circle_code | False | False  | True    | True       | Null          | Null   | Null  |
      | face        | False | False  | True    | False      | Null          | Null   | Null  |
      | fingerprint | False | False  | True    | True       | Null          | Null   | Null  |
