Feature: Organization clients can create Directories
  In order to provide for creation of Directory entities
  As an Organization client
  I can create Directory entities

  Scenario: Client can send unique Directory name and successfully create a Directory
    When I create a Directory with a unique name
    And I retrieve the created Directory
    Then the Directory name is the same as was sent
    And DenialContextInquiryEnabled is set to "true"

  Scenario: Client sending duplicate Directory name raises DirectoryNameInUse
    Given I created a Directory
    And I attempt to create a Directory with the same name
    Then a DirectoryNameInUse error occurs
