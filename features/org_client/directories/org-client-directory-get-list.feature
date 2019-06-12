Feature: Organization clients can get a list of Directories
  In order to provide for retrieving multiple Directory entities
  As an Organization client
  I can get a list of multiple Directories by ID

  Background:
    Given I created a Directory

  Scenario: Getting a list of directories includes the expected data
    Given I updated the Directory as active
    And I updated the Directory Android Key with "Hello Android"
    And I updated the Directory iOS P12 with a valid certificate
    And I updated the Directory webhook url to "https://a.webhook.url/path"
    And I generated and added 2 SDK Keys to the Directory
    And I added 2 Services to the Directory
    When I retrieve a list of Directories with the created Directory's ID
    Then the current Directory list is a list with only the current Directory

  Scenario: Get an invalid Directory raises an exception
    When I attempt retrieve a list of Directories with the Directory ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
