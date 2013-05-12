from mocker import Mocker, MockerTestCase, ANY, CONTAINS


class RequestReplacer(MockerTestCase):

    def runTest(self):
        pass

    def replacer(self, method, endpoint, json_string):
        result = self.mocker.mock()
        result.json()
        self.mocker.count(1, None)
        self.mocker.result(json_string)
        replacement = self.mocker.replace("requests." + method)
        if endpoint != "ping":
            replacement(CONTAINS(endpoint), params=ANY, verify=True)
        else:
            replacement(CONTAINS(endpoint), verify=True)
        self.mocker.result(result)
        self.mocker.replay()
