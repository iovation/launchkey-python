Feature: Organization clients can get a list of all Directories
  In order to provide for retrieving all Directory entities
  As an Organization client
  I can get a list of all of my Directories

  Scenario: Getting a list of all directories includes the expected data
    Given I created a Directory
    Given I updated the Directory as active
    And I updated the Directory Android Key with "Hello Android"
    And I updated the Directory iOS P12 with a valid certificate
    And I updated the Directory webhook url to "https://a.webhook.url/path"
    And I generated and added 2 SDK Keys to the Directory
    And I added 2 Services to the Directory
    When I retrieve a list of all Directories
    Then the current Directory is in the Directory list
