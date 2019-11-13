Feature: Organization clients can update Directories
  In order to provide for updating of Directory entities
  As an Organization client
  I can update Directory attributes

  Background: Need an Directory to test these things.
    Given I created a Directory

  Scenario: Client can update active
    When I update the Directory as inactive
    And I retrieve the updated Directory
    Then the Directory is not active

  Scenario: I can update the Android Push Key
    When I update the Directory Android Key with "A new Android Key"
    And I retrieve the updated Directory
    Then the Directory Android Key is "A new Android Key"

  Scenario: I can clear the Android Push Key
    When I update the Directory Android Key with null
    And I retrieve the updated Directory
    Then the Directory has no Android Key

  Scenario: I can update the iOS Push Certificate
    When I update the Directory iOS P12 with a valid certificate
    And I retrieve the updated Directory
    Then Directory the iOS Certificate Fingerprint matches the provided certificate

  Scenario: I can clear the iOS Push Certificate
    When I update the Directory iOS P12 with null
    And I retrieve the updated Directory
    Then the Directory has no IOS Certificate Fingerprint

  Scenario: I can set the webhook url
    When I update the Directory webhook url to "https://a.webhook.url/path"
    And I retrieve the updated Directory
    Then the Directory webhook url is "https://a.webhook.url/path"

  Scenario: I can unset the webhook url
    When I update the Directory webhook url to "https://a.webhook.url/path"
    And I update the Directory webhook url to null
    And I retrieve the updated Directory
    Then the Directory webhook url is empty

  Scenario: I can set Denial Context Inquiry Enabled to False
    When I update the DenialContextInquiryEnabled to "false"
    And I retrieve the updated Directory
    Then DenialContextInquiryEnabled should be set to "false"

  Scenario: Attempting to update an invalid Directory throws a Forbidden exception
    When I attempt to update the active status of the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
