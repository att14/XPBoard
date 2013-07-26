TicketStatusCtrl = ['$scope', 'DataFetcher', function ($scope, DataFetcher) {
  var dataFetcher = new DataFetcher();
  $scope.tickets = dataFetcher.ticketDataForUsers(['atribone']);
  $scope.ticketsByStatus = _.groupBy($scope.tickets, 'status');
}];

ReviewStatusCtrl = ['$scope', function ReviewStatusCtrl($scope) {
  
}];

UserStatusCtrl = ['$scope', 'DataFetcher', function UserStatusCtrl($scope, DataFetcher) {
    var dataFetcher = new DataFetcher(function(users) {
        $scope.users = users;
    });
    dataFetcher.userData(['atribone']);
}]
