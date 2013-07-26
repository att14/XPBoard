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

    DataFetcher.prototype.ticketDataForUsers = function(usernames) {
        var result;

        $.ajax({
            url: '/user-data',
            data: {
                user: usernames
            },
            async: false,
            traditional: true,
            success: function(users) {
                users = JSON.parse(users);
                result = _.reduce(users, function(memo, user) {
                    memo.push.apply(memo, user.tickets); return memo;
                }, []);
            }
        });

        return result;
    }

    return DataFetcher;
}]);