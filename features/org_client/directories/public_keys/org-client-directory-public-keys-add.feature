Feature: Organization clients can add a Public Key to a Directory
  In order to manage the Public Keys in the Directory Public Key rotation
  As an Organization client
  I can add new Directory Public Keys

  Background:
    Given I created a Directory

  Scenario: Adding a Public Key to a Directory works
    When I add a Public Key to the Directory
    And I retrieve the current Directory's Public Keys
    Then the Public Key is in the list of Public Keys for the Directory


  Scenario Outline: I can add a Public Key with a key type to a Directory and the key type is present when the key is retrieved
    When I add a Public Key with a <key_type> type to the Directory
    And I retrieve the current Directory's Public Keys
    Then the Public Key is in the list of Public Keys for the Directory and has a <key_type> key type
  Examples:
  | key_type   |
  | BOTH       |
  | ENCRYPTION |
  | SIGNATURE  |

  Scenario: Adding a Public Key to a Directory with an empty key type defaults to a dual use key type
    When I add a Public Key to the Directory
    And I retrieve the current Directory's Public Keys
    Then the Public Key is in the list of Public Keys for the Directory and has a "BOTH" key type

  Scenario: Adding a Public Key to a Directory with an invalid key type yields an error
    When I attempt to add a Public Key with a "sup" type to the Directory
    Then an InvalidParameters error occurs

  Scenario: Adding multiple Public Keys to a Directory works
    When I add a Public Key to the Directory
    When I add another Public Key to the Directory
    And I retrieve the current Directory's Public Keys
    Then the Public Key is in the list of Public Keys for the Directory
    And the other Public Key is in the list of Public Keys for the Directory

  Scenario: Attempting to add a Public Key to an invalid Directory throws a Forbidden exception
    When I attempt to add a Public Key to the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to add the same Public Key twice to the same Directory throws a PublicKeyAlreadyInUse exception
    When I add a Public Key to the Directory
    And I attempt to add the same Public Key to the Directory
    Then a PublicKeyAlreadyInUse error occurs