angular.module('XPBoard').factory('DataFetcher', ['$http', function($http) {
    function DataFetcher(successCallback) {
        this.successCallback = successCallback;
    }

    DataFetcher.prototype.userData = function(usernames) {
        $http({
            'method': 'GET',
            'url': '/user-data',
            'params': {
                'user': usernames
            }
        }).success(this.successCallback);
    }

    return DataFetcher;
}]);